from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from .models import Event, EventRegistration

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'organizer', 'event_type', 'start_date', 'venue', 'status_badge', 'is_featured', 'is_upcoming_badge']
    list_filter = ['status', 'event_type', 'start_date', 'is_featured']
    search_fields = ['title', 'description', 'venue', 'organizer__username']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'start_date'
    list_editable = ['is_featured']
    
    fieldsets = (
        ('Event Information', {
            'fields': ('title', 'description', 'event_type', 'is_featured')
        }),
        ('Date & Time', {
            'fields': ('start_date', 'start_time', 'end_date', 'end_time')
        }),
        ('Location', {
            'fields': ('venue', 'address')
        }),
        ('Contact Information', {
            'fields': ('organizer', 'contact_phone', 'contact_email')
        }),
        ('Event Details', {
            'fields': ('max_attendees', 'registration_required', 'registration_deadline')
        }),
        ('Media', {
            'fields': ('poster', 'additional_images')
        }),
        ('Approval', {
            'fields': ('status', 'approved_by', 'approved_at', 'approval_notes')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        if obj.status == 'approved':
            return format_html('<span class="badge bg-success">Approved</span>')
        elif obj.status == 'pending':
            return format_html('<span class="badge bg-warning">Pending</span>')
        else:
            return format_html('<span class="badge bg-danger">Rejected</span>')
    status_badge.short_description = 'Status'
    
    def is_upcoming_badge(self, obj):
        if obj.is_upcoming:
            return format_html('<span class="badge bg-primary">Upcoming</span>')
        elif obj.is_ongoing:
            return format_html('<span class="badge bg-success">Ongoing</span>')
        else:
            return format_html('<span class="badge bg-secondary">Past</span>')
    is_upcoming_badge.short_description = 'Timeline'
    
    actions = ['approve_events', 'reject_events', 'feature_events', 'unfeature_events']
    
    def approve_events(self, request, queryset):
        queryset.update(status='approved', approved_by=request.user, approved_at=timezone.now())
        self.message_user(request, f'{queryset.count()} event(s) approved.')
    approve_events.short_description = 'Approve selected events'
    
    def reject_events(self, request, queryset):
        queryset.update(status='rejected', approved_by=request.user, approved_at=timezone.now())
        self.message_user(request, f'{queryset.count()} event(s) rejected.')
    reject_events.short_description = 'Reject selected events'
    
    def feature_events(self, request, queryset):
        queryset.update(is_featured=True)
        self.message_user(request, f'{queryset.count()} event(s) featured.')
    feature_events.short_description = 'Feature selected events'
    
    def unfeature_events(self, request, queryset):
        queryset.update(is_featured=False)
        self.message_user(request, f'{queryset.count()} event(s) unfeatured.')
    unfeature_events.short_description = 'Unfeature selected events'


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ['event', 'attendee', 'registered_at', 'attendance_confirmed']
    list_filter = ['attendance_confirmed', 'registered_at']
    search_fields = ['event__title', 'attendee__username', 'attendee__first_name', 'attendee__last_name']
    readonly_fields = ['registered_at']
    date_hierarchy = 'registered_at'
    
    fieldsets = (
        ('Registration Information', {
            'fields': ('event', 'attendee', 'registered_at', 'attendance_confirmed')
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
    )
    
    actions = ['confirm_attendance', 'unconfirm_attendance']
    
    def confirm_attendance(self, request, queryset):
        queryset.update(attendance_confirmed=True)
        self.message_user(request, f'Attendance confirmed for {queryset.count()} registration(s).')
    confirm_attendance.short_description = 'Mark attendance as confirmed'
    
    def unconfirm_attendance(self, request, queryset):
        queryset.update(attendance_confirmed=False)
        self.message_user(request, f'Attendance unconfirmed for {queryset.count()} registration(s).')
    unconfirm_attendance.short_description = 'Mark attendance as not confirmed'
