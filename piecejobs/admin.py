from django.contrib import admin
from .models import BusinessService, ServiceApplication

@admin.register(BusinessService)
class BusinessServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'poster', 'location', 'status', 'offer_price', 'created_at')
    list_filter = ('status', 'category', 'created_at')
    search_fields = ('title', 'description', 'location', 'poster__username')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    list_per_page = 20
    
    fieldsets = (
        ('Service Information', {
            'fields': ('title', 'description', 'duration', 'people_needed', 'offer_price', 'category', 'status')
        }),
        ('Contact Information', {
            'fields': ('whatsapp_number', 'contact_number', 'location')
        }),
        ('Media Files', {
            'fields': ('photo', 'pdf_document', 'video')
        }),
        ('Metadata', {
            'fields': ('poster', 'created_at', 'updated_at')
        }),
    )

@admin.register(ServiceApplication)
class ServiceApplicationAdmin(admin.ModelAdmin):
    list_display = ('service', 'applicant', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('service__title', 'applicant__username', 'message')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    list_per_page = 20
    
    fieldsets = (
        ('Application Information', {
            'fields': ('service', 'applicant', 'message', 'contact_number', 'status')
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    )
