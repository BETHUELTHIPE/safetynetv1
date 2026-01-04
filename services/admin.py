from django.contrib import admin
from .models import ServiceCategory, ServiceListing, ServiceReview, ServiceInquiry

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    """Admin configuration for ServiceCategory model"""
    list_display = ('name', 'description')
    search_fields = ('name', 'description')


@admin.register(ServiceListing)
class ServiceListingAdmin(admin.ModelAdmin):
    """Admin configuration for ServiceListing model"""
    list_display = ('title', 'provider', 'category', 'price_type', 'status', 'featured', 'verified', 'created_at')
    list_filter = ('status', 'featured', 'verified', 'category', 'price_type', 'created_at')
    search_fields = ('title', 'description', 'provider__username', 'service_areas', 'tags')
    readonly_fields = ('created_at', 'updated_at', 'view_count')
    date_hierarchy = 'created_at'
    list_editable = ('status', 'featured', 'verified')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'category', 'subcategories', 'tags')
        }),
        ('Pricing', {
            'fields': ('price_type', 'price_amount', 'price_description')
        }),
        ('Service Details', {
            'fields': ('experience_years', 'qualifications', 'availability', 'service_areas')
        }),
        ('Contact Information', {
            'fields': ('contact_number', 'whatsapp_number', 'show_email', 'website')
        }),
        ('Media', {
            'fields': ('profile_image', 'gallery_image1', 'gallery_image2', 'gallery_image3', 'portfolio_pdf')
        }),
        ('Status and Provider', {
            'fields': ('provider', 'status', 'featured', 'verified', 'view_count', 'created_at', 'updated_at')
        }),
    )


@admin.register(ServiceReview)
class ServiceReviewAdmin(admin.ModelAdmin):
    """Admin configuration for ServiceReview model"""
    list_display = ('service', 'reviewer', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('service__title', 'reviewer__username', 'comment')
    date_hierarchy = 'created_at'


@admin.register(ServiceInquiry)
class ServiceInquiryAdmin(admin.ModelAdmin):
    """Admin configuration for ServiceInquiry model"""
    list_display = ('service', 'name', 'email', 'created_at', 'read')
    list_filter = ('read', 'created_at')
    search_fields = ('service__title', 'name', 'email', 'message')
    date_hierarchy = 'created_at'
    list_editable = ('read',)
