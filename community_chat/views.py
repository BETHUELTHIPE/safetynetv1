from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Message, MessageReaction
from .forms import MessageForm

@login_required
def chatboard(request):
    """Main chatboard view displaying all messages."""
    messages_list = Message.objects.filter(is_deleted=False).select_related('author')

    # Pagination
    paginator = Paginator(messages_list, 20)  # Show 20 messages per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'message_form': MessageForm(),
    }
    return render(request, 'community_chat/chatboard.html', context)

@login_required
@require_POST
def post_message(request):
    """Handle posting a new message with optional file attachments."""
    form = MessageForm(request.POST, request.FILES)
    if form.is_valid():
        message = form.save(commit=False)
        message.author = request.user
        message.save()
        messages.success(request, 'Your message has been posted!')
        return redirect('community_chat:chatboard')
    else:
        messages.error(request, 'There was an error posting your message. Please try again.')
        return redirect('community_chat:chatboard')

@login_required
@require_POST
def delete_message(request, message_id):
    """Allow users to delete their own messages."""
    message = get_object_or_404(Message, id=message_id, author=request.user)
    message.is_deleted = True
    message.save()
    messages.success(request, 'Message deleted successfully.')
    return JsonResponse({'success': True})

@login_required
@require_POST
def toggle_reaction(request, message_id):
    """Toggle like/unlike on a message."""
    message = get_object_or_404(Message, id=message_id)
    reaction, created = MessageReaction.objects.get_or_create(
        message=message,
        user=request.user,
        defaults={'reaction_type': 'like'}
    )

    if not created:
        # User already reacted, remove the reaction
        reaction.delete()
        liked = False
    else:
        liked = True

    # Get updated reaction count
    reaction_count = message.reactions.count()

    return JsonResponse({
        'success': True,
        'liked': liked,
        'reaction_count': reaction_count
    })

@login_required
def get_messages(request):
    """API endpoint to fetch messages (for AJAX updates)."""
    since = request.GET.get('since')
    if since:
        messages_list = Message.objects.filter(
            is_deleted=False,
            timestamp__gt=since
        ).select_related('author').order_by('timestamp')
    else:
        messages_list = Message.objects.filter(
            is_deleted=False
        ).select_related('author').order_by('-timestamp')[:50]

    messages_data = []
    for msg in messages_list:
        messages_data.append({
            'id': msg.id,
            'author': msg.author.username,
            'content': msg.content,
            'timestamp': msg.timestamp.isoformat(),
            'image_url': msg.image.url if msg.image else None,
            'pdf_url': msg.pdf.url if msg.pdf else None,
            'video_url': msg.video.url if msg.video else None,
            'reaction_count': msg.reactions.count(),
            'user_reacted': msg.reactions.filter(user=request.user).exists(),
        })

    return JsonResponse({'messages': messages_data})