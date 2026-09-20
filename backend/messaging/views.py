from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Max
from django.utils import timezone
from django.contrib.auth import get_user_model
from properties.models import Property
from .models import Conversation, Message

User = get_user_model()


def _user_conversations(user):
    qs = (
        Conversation.objects.filter(participants=user)
        .annotate(last_msg_time=Max('messages__created_at'))
        .order_by('-last_msg_time')
        .prefetch_related('participants', 'messages')
    )
    # Attach helpers for template
    for conv in qs:
        conv.unread = conv.unread_count_for(user)
        conv.other = conv.get_other_participant(user)
    return qs


@login_required
def conversations_list(request):
    """List all conversations for current user"""
    conversations = _user_conversations(request.user)
    context = {
        'conversations': conversations,
    }
    return render(request, 'dashboard/messages.html', context)


@login_required
def conversation_detail(request, pk):
    """View a conversation and send messages (HTTP fallback; primary is WebSocket)"""
    conversation = get_object_or_404(
        Conversation.objects.prefetch_related('messages__sender', 'participants'),
        pk=pk,
        participants=request.user
    )

    # Mark messages as read
    conversation.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            msg = Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=content
            )
            Conversation.objects.filter(pk=conversation.pk).update(updated_at=timezone.now())

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                display_name = (
                    f'{request.user.first_name} {request.user.last_name}'.strip()
                    or request.user.username
                )
                return JsonResponse({
                    'success': True,
                    'message': {
                        'id': msg.id,
                        'content': msg.content,
                        'sender_id': request.user.id,
                        'sender_username': request.user.username,
                        'sender_name': display_name,
                        'created_at': msg.created_at.strftime('%H:%M'),
                        'is_read': False,
                    }
                })

            return redirect('messaging:conversation', pk=pk)

    other_user = conversation.get_other_participant(request.user)
    conversations = _user_conversations(request.user)

    context = {
        'conversation': conversation,
        'messages': conversation.messages.select_related('sender'),
        'other_user': other_user,
        'conversations': conversations,
    }
    return render(request, 'dashboard/messages.html', context)


@login_required
def start_conversation(request, user_id, property_id=None):
    """Start a new conversation with a user (usually property owner)"""
    other_user = get_object_or_404(User, pk=user_id)

    if other_user == request.user:
        messages.error(request, "You cannot message yourself.")
        return redirect('home')

    existing = Conversation.objects.filter(participants=request.user).filter(
        participants=other_user
    )

    property_obj = None
    if property_id:
        property_obj = get_object_or_404(Property, pk=property_id)
        existing = existing.filter(property=property_obj)
    else:
        existing = existing.filter(property__isnull=True)

    conversation = existing.first()

    if not conversation:
        conversation = Conversation.objects.create(property=property_obj)
        conversation.participants.add(request.user, other_user)

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=content
            )

    return redirect('messaging:conversation', pk=conversation.pk)


@login_required
def send_message_ajax(request, pk):
    """HTTP AJAX fallback for sending messages when WebSocket is unavailable"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    conversation = get_object_or_404(Conversation, pk=pk, participants=request.user)
    content = request.POST.get('content', '').strip()

    if not content:
        return JsonResponse({'error': 'Message cannot be empty'}, status=400)

    msg = Message.objects.create(
        conversation=conversation,
        sender=request.user,
        content=content
    )
    Conversation.objects.filter(pk=conversation.pk).update(updated_at=timezone.now())

    display_name = (
        f'{request.user.first_name} {request.user.last_name}'.strip()
        or request.user.username
    )
    return JsonResponse({
        'success': True,
        'message': {
            'id': msg.id,
            'content': msg.content,
            'sender_id': request.user.id,
            'sender_username': request.user.username,
            'sender_name': display_name,
            'created_at': msg.created_at.strftime('%H:%M'),
            'is_read': False,
        }
    })
