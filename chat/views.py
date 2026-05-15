from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.files.storage import default_storage
from .models import Room, Message
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


@login_required
def inbox(request):
    """Show all conversations for the logged-in user."""
    rooms = request.user.chat_rooms.prefetch_related('participants', 'messages').all()

    conversations = []
    for room in rooms:
        other = room.get_other_user(request.user)
        last = room.last_message()
        unread = room.unread_count(request.user)
        conversations.append({
            'room': room,
            'other_user': other,
            'last_message': last,
            'unread_count': unread,
        })

    # Sort by last message timestamp
    conversations.sort(
        key=lambda c: c['last_message'].timestamp if c['last_message'] else c['room'].created_at,
        reverse=True
    )

    # All other users to start a new chat
    other_users = User.objects.exclude(id=request.user.id).order_by('username')

    return render(request, 'chat/inbox.html', {
        'conversations': conversations,
        'other_users': other_users,
    })


@login_required
def room(request, room_id):
    """Open a specific chat room."""
    chat_room = get_object_or_404(Room, id=room_id)

    # Security: only participants can access
    if not chat_room.participants.filter(id=request.user.id).exists():
        return redirect('chat_inbox')

    other_user = chat_room.get_other_user(request.user)
    chat_messages_qs = chat_room.messages.select_related('sender').all()

    # Mark messages from other as read (HTTP-side; WS consumer also handles it)
    chat_room.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    return render(request, 'chat/room.html', {
        'room': chat_room,
        'other_user': other_user,
        'chat_messages': chat_messages_qs,   # renamed: was 'messages' — clashed with Django messages framework
        'current_user': request.user,
    })


@login_required
def start_chat(request, user_id):
    """Start or resume a private chat with another user."""
    other = get_object_or_404(User, id=user_id)
    if other == request.user:
        return redirect('chat_inbox')

    chat_room, _ = Room.get_or_create_room(request.user, other)
    return redirect('chat_room', room_id=chat_room.id)


@login_required
@require_POST
def send_image(request, room_id):
    """Upload an image message via AJAX."""
    chat_room = get_object_or_404(Room, id=room_id)
    if not chat_room.participants.filter(id=request.user.id).exists():
        return JsonResponse({'error': 'Forbidden'}, status=403)

    image = request.FILES.get('image')
    if not image:
        return JsonResponse({'error': 'No image provided'}, status=400)
    # Optional reply/forward fields from the form
    reply_to = request.POST.get('reply_to')
    forwarded_from = request.POST.get('forwarded_from')

    msg = Message.objects.create(room=chat_room, sender=request.user, image=image)

    # If provided, attach reply/forward relationships
    if reply_to:
        try:
            parent = Message.objects.get(id=reply_to)
            msg.reply_to = parent
        except Message.DoesNotExist:
            pass
    if forwarded_from:
        try:
            from django.contrib.auth.models import User
            u = User.objects.get(id=forwarded_from)
            msg.forwarded_from = u
        except Exception:
            pass
    msg.save()

    # Build an absolute URL for the image (helps when proxied/static/media served)
    try:
        image_url = request.build_absolute_uri(msg.image.url)
    except Exception:
        image_url = msg.image.url

    # Broadcast the image message via channels so the other participant sees it
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'chat_{room_id}',
        {
            'type': 'chat_message',
            'message_id': msg.id,
            'content': msg.content or '',
            'sender_username': request.user.username,
            'sender_id': request.user.id,
            'timestamp': msg.timestamp.strftime('%I:%M %p'),
            'image_url': image_url,
            'reply_to_id': msg.reply_to.id if msg.reply_to else None,
            'forwarded_from_id': msg.forwarded_from.id if msg.forwarded_from else None,
            'forwarded_from_username': msg.forwarded_from.username if msg.forwarded_from else None,
        }
    )

    return JsonResponse({
        'success': True,
        'message_id': msg.id,
        'image_url': image_url,
        'sender_username': request.user.username,
        'sender_id': request.user.id,
        'timestamp': msg.timestamp.strftime('%I:%M %p'),
    })


@login_required
def unread_count(request):
    """Return total unread message count (for navbar badge)."""
    count = Message.objects.filter(
        room__participants=request.user,
        is_read=False
    ).exclude(sender=request.user).count()
    return JsonResponse({'unread': count})
