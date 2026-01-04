from django.contrib import admin
from django.utils.html import format_html
from .models import CrimeReport

@admin.register(CrimeReport)
class CrimeReportAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'location', 'get_status_badge', 'date_reported', 'reporter']
    list_filter = ['status', 'category', 'date_reported']
    search_fields = ['title', 'description', 'location', 'reporter__username']
    readonly_fields = ['date_reported']
    date_hierarchy = 'date_reported'
    
    fieldsets = (
        ('Report Details', {
            'fields': ('title', 'description', 'category', 'status')
        }),
        ('Location Information', {
            'fields': ('location', 'latitude', 'longitude')
        }),
        ('Reporter Information', {
            'fields': ('reporter', 'date_reported')
        }),
    )
    
    def get_status_badge(self, obj):
        status_colors = {
            'PENDING': 'warning',
            'UNDER_INVESTIGATION': 'info',
            'RESOLVED': 'success',
            'CLOSED': 'secondary',
            'REJECTED': 'danger',
        }
        
        color = status_colors.get(obj.status, 'secondary')
        return format_html('<span class="badge bg-{}">{}️</span>', color, obj.get_status_display())
    get_status_badge.short_description = 'Status'
    
    actions = ['mark_as_under_investigation', 'mark_as_resolved', 'mark_as_closed']
    
    def mark_as_under_investigation(self, request, queryset):
        queryset.update(status='UNDER_INVESTIGATION')
        self.message_user(request, f'{queryset.count()} report(s) marked as under investigation.')
    mark_as_under_investigation.short_description = 'Mark selected reports as under investigation'
    
    def mark_as_resolved(self, request, queryset):
        queryset.update(status='RESOLVED')
        self.message_user(request, f'{queryset.count()} report(s) marked as resolved.')
    mark_as_resolved.short_description = 'Mark selected reports as resolved'
    
    def mark_as_closed(self, request, queryset):
        queryset.update(status='CLOSED')
        self.message_user(request, f'{queryset.count()} report(s) marked as closed.')
    mark_as_closed.short_description = 'Mark selected reports as closed'
