from django.contrib import admin
from .models import BuyRequest, BuyRequestResponse

@admin.register(BuyRequest)
class BuyRequestAdmin(admin.ModelAdmin):
    """Admin configuration for BuyRequest model"""
    list_display = ('title', 'requester', 'status', 'urgency', 'created_at', 'view_count')
    list_filter = ('status', 'urgency', 'category', 'created_at')
    search_fields = ('title', 'description', 'requester__username', 'location', 'tags')
    readonly_fields = ('created_at', 'updated_at', 'view_count')
    date_hierarchy = 'created_at'
    list_editable = ('status',)
    
    fieldsets = (
        ('Request Information', {
            'fields': ('title', 'description', 'price_range_min', 'price_range_max', 'urgency', 'category', 'tags')
        }),
        ('Contact Information', {
            'fields': ('location', 'contact_number', 'whatsapp_number', 'show_email')
        }),
        ('Media', {
            'fields': ('reference_image', 'pdf_document')
        }),
        ('Status and Metadata', {
            'fields': ('requester', 'status', 'expiry_date', 'view_count', 'created_at', 'updated_at')
        }),
    )


@admin.register(BuyRequestResponse)
class BuyRequestResponseAdmin(admin.ModelAdmin):
    """Admin configuration for BuyRequestResponse model"""
    list_display = ('buy_request', 'responder', 'price_offer', 'created_at', 'read')
    list_filter = ('read', 'created_at')
    search_fields = ('buy_request__title', 'responder__username', 'message')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
