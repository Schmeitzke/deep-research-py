from django.db import models
from django.conf import settings

class ChatSession(models.Model):
    """
    Represents a full chat session between a user and the system.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chat_sessions"
    )
    title = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Optional title or summary of the session."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Session {self.pk} for {self.user.username}"

    class Meta:
        ordering = ['-created_at']


class ChatMessage(models.Model):
    """
    Represents a single message in a chat session.
    """
    ROLE_CHOICES = [
        ('user', 'User'),
        ('system', 'System'),
    ]
    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name="messages"
    )
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        help_text="Indicates whether the message was sent by the user or the system."
    )
    content = models.TextField(
        help_text="The full text content of the message."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message {self.pk} in Session {self.session.pk} ({self.role})"

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['session', 'created_at']),
        ]
