from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Wishlist(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlists')

    def __str__(self):
        return self.title

class Comment(models.Model):
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')

    def __str__(self):
        return f"Comment by {self.user.username} on {self.wishlist.title}"

class Memory(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    memory_date = models.DateField(help_text="When did this memory happen?")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='memories')

    def __str__(self):
        return self.title

class MemoryPhoto(models.Model):
    memory = models.ForeignKey(Memory, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='memory_photos/', help_text="Upload a photo from this memory")
    caption = models.CharField(max_length=200, blank=True, help_text="Optional caption for the photo")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo for {self.memory.title}"
