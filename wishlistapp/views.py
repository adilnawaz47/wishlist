from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .models import Wishlist, Comment, Memory, MemoryPhoto
from .forms import WishlistForm, CommentForm, MemoryForm, MemoryPhotoForm
from django.http import HttpResponse
from django.contrib.auth.models import User


# Registration View
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully! Welcome!')
            return redirect('wishlist_list')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

# Wishlist Views
class WishlistListView(LoginRequiredMixin, ListView):
    model = Wishlist
    template_name = 'wishlistapp/wishlist_list.html'
    context_object_name = 'wishlists'
    ordering = ['-created_at']

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Wishlist.objects.all()
        return Wishlist.objects.filter(user=self.request.user)

class WishlistDetailView(LoginRequiredMixin, DetailView):
    model = Wishlist
    template_name = 'wishlistapp/wishlist_detail.html'
    context_object_name = 'wishlist'

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Wishlist.objects.all()
        return Wishlist.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        return context

class WishlistCreateView(LoginRequiredMixin, CreateView):
    model = Wishlist
    form_class = WishlistForm
    template_name = 'wishlistapp/wishlist_form.html'
    success_url = reverse_lazy('wishlist_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Wishlist created successfully!')
        return super().form_valid(form)

class WishlistUpdateView(LoginRequiredMixin, UpdateView):
    model = Wishlist
    form_class = WishlistForm
    template_name = 'wishlistapp/wishlist_form.html'
    success_url = reverse_lazy('wishlist_list')

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Wishlist.objects.all()
        return Wishlist.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Wishlist updated successfully!')
        return super().form_valid(form)

class WishlistDeleteView(LoginRequiredMixin, DeleteView):
    model = Wishlist
    template_name = 'wishlistapp/wishlist_confirm_delete.html'
    success_url = reverse_lazy('wishlist_list')

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Wishlist.objects.all()
        return Wishlist.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Wishlist deleted successfully!')
        return super().delete(request, *args, **kwargs)

class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'wishlistapp/comment_form.html'
    
    def get_success_url(self):
        return reverse_lazy('wishlist_detail', kwargs={'pk': self.object.wishlist.pk})

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Comment.objects.all()
        return Comment.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Comment updated successfully!')
        return super().form_valid(form)

class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'wishlistapp/comment_confirm_delete.html'
    
    def get_success_url(self):
        return reverse_lazy('wishlist_detail', kwargs={'pk': self.object.wishlist.pk})

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Comment.objects.all()
        return Comment.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Comment deleted successfully!')
        return super().delete(request, *args, **kwargs)

# Comment Views
@login_required
def add_comment(request, pk):
    if request.user.is_superuser:
        wishlist = get_object_or_404(Wishlist, pk=pk)
    else:
        wishlist = get_object_or_404(Wishlist, pk=pk, user=request.user)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.wishlist = wishlist
            comment.user = request.user
            comment.save()
            messages.success(request, 'Comment added!')
            return redirect('wishlist_detail', pk=pk)
    return redirect('wishlist_detail', pk=pk)

# Memory Views
class MemoryListView(LoginRequiredMixin, ListView):
    model = Memory
    template_name = 'wishlistapp/memory_list.html'
    context_object_name = 'memories'
    ordering = ['-memory_date']

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Memory.objects.all()
        return Memory.objects.filter(user=self.request.user)

class MemoryDetailView(LoginRequiredMixin, DetailView):
    model = Memory
    template_name = 'wishlistapp/memory_detail.html'
    context_object_name = 'memory'

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Memory.objects.all()
        return Memory.objects.filter(user=self.request.user)

class MemoryCreateView(LoginRequiredMixin, CreateView):
    model = Memory
    form_class = MemoryForm
    template_name = 'wishlistapp/memory_form.html'
    success_url = reverse_lazy('memory_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['photo_form'] = MemoryPhotoForm()
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        
        # Handle multiple photo uploads
        photo_form = MemoryPhotoForm(self.request.POST, self.request.FILES)
        if photo_form.is_valid():
            images = self.request.FILES.getlist('images')
            caption = photo_form.cleaned_data.get('caption', '')
            if images:
                for image in images:
                    MemoryPhoto.objects.create(
                        memory=self.object,
                        image=image,
                        caption=caption
                    )
                messages.success(self.request, f'Memory created with {len(images)} photo(s) successfully!')
            else:
                messages.success(self.request, 'Memory created successfully!')
        else:
            messages.success(self.request, 'Memory created successfully!')
        
        return response

class MemoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Memory
    form_class = MemoryForm
    template_name = 'wishlistapp/memory_form.html'
    success_url = reverse_lazy('memory_list')

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Memory.objects.all()
        return Memory.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Include photo_form for editing (to allow adding more photos)
        context['photo_form'] = MemoryPhotoForm()
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Handle adding more photos during edit
        photo_form = MemoryPhotoForm(self.request.POST, self.request.FILES)
        if photo_form.is_valid():
            images = self.request.FILES.getlist('images')
            caption = photo_form.cleaned_data.get('caption', '')
            if images:
                for image in images:
                    MemoryPhoto.objects.create(
                        memory=self.object,
                        image=image,
                        caption=caption
                    )
                messages.success(self.request, f'Memory updated! Added {len(images)} more photo(s).')
            else:
                messages.success(self.request, 'Memory updated successfully!')
        else:
            messages.success(self.request, 'Memory updated successfully!')
        
        return response

class MemoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Memory
    template_name = 'wishlistapp/memory_confirm_delete.html'
    success_url = reverse_lazy('memory_list')

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Memory.objects.all()
        return Memory.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Memory deleted successfully!')
        return super().delete(request, *args, **kwargs)

def create_admin(request):
    User.objects.filter(username='admin').delete()

    user = User.objects.create_user(
        username='admin',
        email='admin@example.com',
        password='admin123'
    )

    user.is_staff = True
    user.is_superuser = True
    user.save()

    return HttpResponse("Admin created successfully")