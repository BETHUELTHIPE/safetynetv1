from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import Event, EventRegistration

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'organizer', 'category', 'start_date', 'venue', 'status', 'is_approved_badge', 'is_upcoming']
    list_filter = ['status', 'category', 'start_date', 'is_featured', 'created_at']
    search_fields = ['title', 'description', 'organizer__username', 'venue']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-start_date', '-start_time']

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'category', 'organizer')
        }),
        ('Date & Time', {
            'fields': ('start_date', 'start_time', 'end_date', 'end_time')
        }),
        ('Location', {
            'fields': ('venue', 'address', 'latitude', 'longitude')
        }),
        ('Contact Information', {
            'fields': ('contact_person', 'contact_email', 'contact_phone')
        }),
        ('Event Details', {
            'fields': ('max_attendees', 'ticket_price', 'registration_required', 'registration_deadline', 'is_featured')
        }),
        ('Media', {
            'fields': ('image', 'flyer')
        }),
        ('Approval', {
            'fields': ('status', 'approved_by', 'approved_at', 'approval_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def is_approved_badge(self, obj):
        if obj.status == 'approved':
            return format_html('<span class="badge bg-success">Approved</span>')
        elif obj.status == 'pending':
            return format_html('<span class="badge bg-warning">Pending</span>')
        elif obj.status == 'rejected':
            return format_html('<span class="badge bg-danger">Rejected</span>')
        else:
            return format_html('<span class="badge bg-secondary">{}</span>', obj.status)
    is_approved_badge.short_description = 'Status'

    def is_upcoming(self, obj):
        return obj.is_upcoming()
    is_upcoming.boolean = True
    is_upcoming.short_description = 'Upcoming'

    actions = ['approve_events', 'reject_events']

    def approve_events(self, request, queryset):
        queryset.update(status='approved', approved_by=request.user, approved_at=timezone.now())
        self.message_user(request, f'{queryset.count()} event(s) have been approved.')
    approve_events.short_description = 'Approve selected events'

    def reject_events(self, request, queryset):
        queryset.update(status='rejected', approved_by=request.user, approved_at=timezone.now())
        self.message_user(request, f'{queryset.count()} event(s) have been rejected.')
    reject_events.short_description = 'Reject selected events'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('organizer', 'approved_by')


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ['event', 'attendee', 'registered_at', 'status', 'number_of_attendees']
    list_filter = ['status', 'registered_at', 'event__category']
    search_fields = ['attendee__username', 'event__title']
    readonly_fields = ['registered_at']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('event', 'attendee')