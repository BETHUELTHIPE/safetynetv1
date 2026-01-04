from django.contrib import admin
from .models import SaleItem, SavedItem, ItemMessage

@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    """Admin configuration for SaleItem model"""
    list_display = ('title', 'price', 'seller', 'location', 'status', 'featured', 'created_at', 'view_count')
    list_filter = ('status', 'category', 'created_at', 'featured')
    search_fields = ('title', 'description', 'seller__username', 'location')
    readonly_fields = ('view_count', 'created_at', 'updated_at')
    list_editable = ('status', 'featured')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Item Information', {
            'fields': ('title', 'description', 'price', 'negotiable', 'category', 'tags', 'status')
        }),
        ('Seller Information', {
            'fields': ('seller', 'location', 'contact_number', 'whatsapp_number', 'show_email')
        }),
        ('Media', {
            'fields': ('main_image', 'additional_image1', 'additional_image2', 'video', 'pdf_document')
        }),
        ('Listing Details', {
            'fields': ('featured', 'expiry_date', 'view_count', 'created_at', 'updated_at')
        }),
    )


@admin.register(SavedItem)
class SavedItemAdmin(admin.ModelAdmin):
    """Admin configuration for SavedItem model"""
    list_display = ('user', 'item', 'saved_at')
    list_filter = ('saved_at',)
    search_fields = ('user__username', 'item__title')
    date_hierarchy = 'saved_at'


@admin.register(ItemMessage)
class ItemMessageAdmin(admin.ModelAdmin):
    """Admin configuration for ItemMessage model"""
    list_display = ('sender', 'recipient', 'item', 'created_at', 'read')
    list_filter = ('read', 'created_at')
    search_fields = ('sender__username', 'recipient__username', 'message', 'item__title')
    date_hierarchy = 'created_at'
