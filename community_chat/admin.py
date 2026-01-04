from django.contrib import admin
from .models import Message, MessageReaction

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['author', 'content_preview', 'timestamp', 'has_attachments', 'is_deleted']
    list_filter = ['timestamp', 'is_deleted', 'author']
    search_fields = ['author__username', 'content']
    readonly_fields = ['timestamp', 'edited_at']
    ordering = ['-timestamp']

    def content_preview(self, obj):
        if obj.content:
            return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
        elif obj.image:
            return "[Image attachment]"
        elif obj.pdf:
            return "[PDF attachment]"
        elif obj.video:
            return "[Video attachment]"
        return "[Empty message]"
    content_preview.short_description = 'Content'

    def has_attachments(self, obj):
        return bool(obj.image or obj.pdf or obj.video)
    has_attachments.boolean = True
    has_attachments.short_description = 'Has Attachments'

@admin.register(MessageReaction)
class MessageReactionAdmin(admin.ModelAdmin):
    list_display = ['message', 'user', 'reaction_type', 'created_at']
    list_filter = ['reaction_type', 'created_at']
    search_fields = ['user__username', 'message__content']
    readonly_fields = ['created_at']