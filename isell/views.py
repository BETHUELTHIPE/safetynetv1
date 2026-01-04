from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.utils import timezone

from .models import SaleItem, SavedItem, ItemMessage
from .forms import SaleItemForm, ItemMessageForm

def item_list(request):
    """View to list all items for sale"""
    
    # Start with active items only
    items = SaleItem.objects.filter(status='ACTIVE')
    
    # Handle search
    query = request.GET.get('q')
    if query:
        items = items.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query) |
            Q(location__icontains=query) |
            Q(tags__icontains=query)
        )
    
    # Handle category filter
    category = request.GET.get('category')
    if category:
        items = items.filter(category=category)
    
    # Handle price range filter
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        items = items.filter(price__gte=min_price)
    if max_price:
        items = items.filter(price__lte=max_price)
    
    # Handle sort order
    sort = request.GET.get('sort', 'newest')
    if sort == 'price_low':
        items = items.order_by('price')
    elif sort == 'price_high':
        items = items.order_by('-price')
    elif sort == 'oldest':
        items = items.order_by('created_at')
    else:  # Default to newest
        items = items.order_by('-created_at')
    
    # Get categories for filtering
    categories = SaleItem.objects.filter(status='ACTIVE').values_list(
        'category', flat=True
    ).distinct()
    
    # Pagination
    paginator = Paginator(items, 12)  # Show 12 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get saved items if user is authenticated
    saved_items = []
    if request.user.is_authenticated:
        saved_items = SavedItem.objects.filter(user=request.user).values_list('item_id', flat=True)
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'query': query,
        'selected_category': category,
        'min_price': min_price,
        'max_price': max_price,
        'sort': sort,
        'saved_items': saved_items,
        'title': 'I Sell - Marketplace'
    }
    
    return render(request, 'isell/item_list.html', context)


def item_detail(request, pk):
    """View to display an item's details"""
    
    item = get_object_or_404(SaleItem, pk=pk)
    
    # Increment view count
    item.view_count += 1
    item.save()
    
    # Check if item is saved by user
    is_saved = False
    if request.user.is_authenticated:
        is_saved = SavedItem.objects.filter(user=request.user, item=item).exists()
    
    # Item message form
    form = ItemMessageForm()
    
    context = {
        'item': item,
        'is_saved': is_saved,
        'form': form,
        'title': item.title
    }
    
    return render(request, 'isell/item_detail.html', context)


@login_required
def create_item(request):
    """View for creating a new item listing"""
    
    if request.method == 'POST':
        form = SaleItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.seller = request.user
            item.save()
            
            messages.success(request, "Your item has been listed successfully!")
            return redirect('isell:item_detail', pk=item.pk)
    else:
        form = SaleItemForm()
    
    context = {
        'form': form,
        'title': 'Create Listing - I Sell',
        'button_text': 'Post Listing',
        'is_edit': False
    }
    
    return render(request, 'isell/item_form.html', context)


@login_required
def edit_item(request, pk):
    """View for editing an existing item"""
    
    item = get_object_or_404(SaleItem, pk=pk)
    
    # Check if user is the seller
    if item.seller != request.user:
        return HttpResponseForbidden("You don't have permission to edit this listing.")
    
    if request.method == 'POST':
        form = SaleItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, "Your listing has been updated successfully!")
            return redirect('isell:item_detail', pk=item.pk)
    else:
        form = SaleItemForm(instance=item)
    
    context = {
        'form': form,
        'item': item,
        'title': 'Edit Listing',
        'button_text': 'Update Listing',
        'is_edit': True
    }
    
    return render(request, 'isell/item_form.html', context)


@login_required
def delete_item(request, pk):
    """View for deleting/deactivating an item"""
    
    item = get_object_or_404(SaleItem, pk=pk)
    
    # Check if user is the seller
    if item.seller != request.user:
        return HttpResponseForbidden("You don't have permission to delete this listing.")
    
    if request.method == 'POST':
        # Just mark as removed, don't actually delete
        item.status = 'REMOVED'
        item.save()
        messages.success(request, "Your listing has been removed.")
        return redirect('isell:my_items')
    
    context = {
        'item': item,
        'title': 'Delete Listing'
    }
    
    return render(request, 'isell/item_confirm_delete.html', context)


@login_required
def my_items(request):
    """View to display a user's own listings"""
    
    items = SaleItem.objects.filter(seller=request.user)
    
    # Filter by status
    status = request.GET.get('status', 'all')
    if status != 'all':
        items = items.filter(status=status.upper())
    
    items = items.order_by('-created_at')
    
    context = {
        'items': items,
        'status': status,
        'title': 'My Listings'
    }
    
    return render(request, 'isell/my_items.html', context)


@login_required
def saved_items(request):
    """View to display items saved by the user"""
    
    saved = SavedItem.objects.filter(user=request.user).select_related('item')
    
    context = {
        'saved_items': saved,
        'title': 'Saved Items'
    }
    
    return render(request, 'isell/saved_items.html', context)


@login_required
@require_POST
def toggle_save_item(request, pk):
    """AJAX view to save/unsave an item"""
    
    item = get_object_or_404(SaleItem, pk=pk)
    saved_item = SavedItem.objects.filter(user=request.user, item=item)
    
    if saved_item.exists():
        # Item is already saved, so unsave it
        saved_item.delete()
        saved = False
    else:
        # Item is not saved, so save it
        SavedItem.objects.create(user=request.user, item=item)
        saved = True
    
    return JsonResponse({'saved': saved})


@login_required
def mark_as_sold(request, pk):
    """View to mark an item as sold"""
    
    item = get_object_or_404(SaleItem, pk=pk)
    
    # Check if user is the seller
    if item.seller != request.user:
        return HttpResponseForbidden("You don't have permission to update this listing.")
    
    item.status = 'SOLD'
    item.save()
    
    messages.success(request, "Your item has been marked as sold!")
    return redirect('isell:item_detail', pk=item.pk)


@login_required
def send_message(request, pk):
    """View to send a message about an item"""
    
    item = get_object_or_404(SaleItem, pk=pk)
    
    # Don't allow messaging your own item
    if item.seller == request.user:
        messages.error(request, "You cannot send a message about your own item.")
        return redirect('isell:item_detail', pk=item.pk)
    
    if request.method == 'POST':
        form = ItemMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.item = item
            message.sender = request.user
            message.recipient = item.seller
            message.save()
            
            messages.success(request, "Your message has been sent to the seller!")
            return redirect('isell:item_detail', pk=item.pk)
    else:
        form = ItemMessageForm()
    
    context = {
        'form': form,
        'item': item,
        'title': f'Send Message about {item.title}'
    }
    
    return render(request, 'isell/send_message.html', context)


@login_required
def my_messages(request):
    """View to display user's received messages"""
    
    # Get received messages
    received_messages = ItemMessage.objects.filter(
        recipient=request.user
    ).select_related('item', 'sender')
    
    # Get sent messages
    sent_messages = ItemMessage.objects.filter(
        sender=request.user
    ).select_related('item', 'recipient')
    
    context = {
        'received_messages': received_messages,
        'sent_messages': sent_messages,
        'title': 'My Messages'
    }
    
    return render(request, 'isell/my_messages.html', context)
