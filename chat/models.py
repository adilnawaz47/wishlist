from django.db import models
from django.contrib.auth.models import User


class Room(models.Model):
    """Private chat room between exactly two users."""
    participants = models.ManyToManyField(User, related_name='chat_rooms')
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def get_or_create_room(cls, user1, user2):
        """Return existing 1-to-1 room or create a new one."""
        rooms = cls.objects.filter(participants=user1).filter(participants=user2)
        for room in rooms:
            if room.participants.count() == 2:
                return room, False
        room = cls.objects.create()
        room.participants.add(user1, user2)
        return room, True

    def get_other_user(self, user):
        return self.participants.exclude(id=user.id).first()

    def last_message(self):
        return self.messages.order_by('-timestamp').first()

    def unread_count(self, user):
        return self.messages.filter(is_read=False).exclude(sender=user).count()

    def __str__(self):
        return f"Room {self.id}"


class Message(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField(blank=True)
    image = models.ImageField(upload_to='chat_images/', blank=True, null=True)
    # Optional: message this replies to
    reply_to = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='replies')
    # If this message was forwarded from another user
    forwarded_from = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='forwarded_messages')
    # Optional GIF URL (external or uploaded URL)
    gif_url = models.URLField(max_length=500, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.sender.username}: {self.content[:40]}"
