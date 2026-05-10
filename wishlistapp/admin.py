from django.contrib import admin
from .models import Wishlist, Comment, Memory, MemoryPhoto

# Register your models here.
admin.site.register(Wishlist)
admin.site.register(Comment)
admin.site.register(Memory)
admin.site.register(MemoryPhoto)
