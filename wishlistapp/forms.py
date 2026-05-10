from django import forms
from .models import Wishlist, Comment, Memory, MemoryPhoto

class WishlistForm(forms.ModelForm):
    class Meta:
        model = Wishlist
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter wishlist title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Describe your wishlist', 'rows': 4}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Add a comment...', 'rows': 3}),
        }

class MemoryForm(forms.ModelForm):
    class Meta:
        model = Memory
        fields = ['title', 'description', 'memory_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter memory title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Describe this beautiful memory', 'rows': 4}),
            'memory_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class MemoryPhotoForm(forms.Form):
    images = forms.FileField(
        required=False,
        help_text="Select multiple photos"
    )
    caption = forms.CharField(
        max_length=200,
        required=False,
        label="",  # Remove label since we provide custom labels in template
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional caption for all photos'}),
    )