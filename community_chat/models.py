from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Message(models.Model):
    """Model for chat messages in the community chatboard."""
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now)

    # File attachments
    image = models.ImageField(upload_to='chat_images/', blank=True, null=True)
    pdf = models.FileField(upload_to='chat_pdfs/', blank=True, null=True)
    video = models.FileField(upload_to='chat_videos/', blank=True, null=True)

    # Metadata
    is_deleted = models.BooleanField(default=False)
    edited_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['timestamp']
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'

    def __str__(self):
        if self.content:
            return f"{self.author.username}: {self.content[:50]}..."
        elif self.image:
            return f"{self.author.username}: [Image]"
        elif self.pdf:
            return f"{self.author.username}: [PDF]"
        elif self.video:
            return f"{self.author.username}: [Video]"
        else:
            return f"{self.author.username}: [Empty message]"

class MessageReaction(models.Model):
    """Model for reactions to messages (likes, etc.)."""
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reaction_type = models.CharField(max_length=20, default='like')  # 'like', 'love', 'laugh', etc.
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ['message', 'user']
        verbose_name = 'Message Reaction'
        verbose_name_plural = 'Message Reactions'

    def __str__(self):
        return f"{self.user.username} reacted {self.reaction_type} to message {self.message.id}"