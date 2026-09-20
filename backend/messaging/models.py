from django.db import models
from django.conf import settings
from django.utils import timezone
from properties.models import Property


class Conversation(models.Model):
    """Conversation between two users about a property (optional)"""
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='conversations')
    property = models.ForeignKey(
        Property, on_delete=models.SET_NULL, null=True, blank=True, related_name='conversations'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        users = ", ".join([u.username for u in self.participants.all()[:2]])
        return f"Conversation: {users}"
    
    def get_other_participant(self, user):
        return self.participants.exclude(id=user.id).first()
    
    def last_message(self):
        return self.messages.order_by('-created_at').first()
    
    def unread_count_for(self, user):
        return self.messages.filter(is_read=False).exclude(sender=user).count()

class Message(models.Model):
    """Individual message in a conversation"""
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Message from {self.sender.username}: {self.content[:50]}"
