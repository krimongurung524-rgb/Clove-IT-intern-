/**
 * RoomFinder – Real-time WebSocket Chat
 */
(function () {
    'use strict';

    let chatSocket = null;
    let typingTimeout = null;
    let isTyping = false;
    let reconnectAttempts = 0;
    const MAX_RECONNECT = 5;

    function getCookie(name) {
        let value = null;
        if (document.cookie) {
            document.cookie.split(';').forEach(function (c) {
                c = c.trim();
                if (c.indexOf(name + '=') === 0) {
                    value = decodeURIComponent(c.substring(name.length + 1));
                }
            });
        }
        return value;
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function scrollToBottom(el) {
        if (el) el.scrollTop = el.scrollHeight;
    }

    function setConnectionStatus(status) {
        const el = document.getElementById('chatConnectionStatus');
        if (!el) return;
        el.className = 'chat-status chat-status-' + status;
        const labels = {
            connecting: 'Connecting…',
            connected: 'Connected',
            disconnected: 'Disconnected',
            error: 'Connection error',
        };
        el.textContent = labels[status] || status;
        el.style.display = status === 'connected' ? 'none' : 'inline-flex';
    }

    function appendMessage(msg, currentUserId) {
        const container = document.getElementById('chatMessages');
        if (!container) return;

        // Avoid duplicate messages (e.g. after reconnect)
        if (msg.id && container.querySelector('[data-message-id="' + msg.id + '"]')) {
            return;
        }

        // Hide empty-state hint
        const hint = document.getElementById('emptyChatHint');
        if (hint) hint.style.display = 'none';

        const isMine = String(msg.sender_id) === String(currentUserId);
        const bubble = document.createElement('div');
        bubble.className = 'message-bubble ' + (isMine ? 'message-mine' : 'message-other');
        if (msg.id) bubble.setAttribute('data-message-id', msg.id);

        const time = msg.created_at || '';
        bubble.innerHTML =
            '<div>' + escapeHtml(msg.content) + '</div>' +
            '<small class="' + (isMine ? 'opacity-75' : 'text-muted') + '">' + escapeHtml(time) + '</small>';

        container.appendChild(bubble);
        scrollToBottom(container);
    }

    function showTyping(username, show) {
        let el = document.getElementById('typingIndicator');
        if (!el) return;
        if (show) {
            el.textContent = (username || 'Someone') + ' is typing…';
            el.style.display = 'block';
        } else {
            el.style.display = 'none';
            el.textContent = '';
        }
    }

    function connectWebSocket(conversationId, currentUserId) {
        if (chatSocket && (chatSocket.readyState === WebSocket.OPEN || chatSocket.readyState === WebSocket.CONNECTING)) {
            return;
        }

        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = protocol + '//' + window.location.host + '/ws/chat/' + conversationId + '/';

        setConnectionStatus('connecting');
        chatSocket = new WebSocket(wsUrl);

        chatSocket.onopen = function () {
            reconnectAttempts = 0;
            setConnectionStatus('connected');
            // Mark messages as read when we open the chat
            chatSocket.send(JSON.stringify({ type: 'mark_read' }));
        };

        chatSocket.onclose = function (event) {
            setConnectionStatus('disconnected');
            chatSocket = null;

            // Don't reconnect on auth/permission errors
            if (event.code === 4001 || event.code === 4003) {
                setConnectionStatus('error');
                return;
            }

            if (reconnectAttempts < MAX_RECONNECT) {
                reconnectAttempts += 1;
                const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 15000);
                setTimeout(function () {
                    connectWebSocket(conversationId, currentUserId);
                }, delay);
            }
        };

        chatSocket.onerror = function () {
            setConnectionStatus('error');
        };

        chatSocket.onmessage = function (e) {
            let data;
            try {
                data = JSON.parse(e.data);
            } catch (err) {
                return;
            }

            switch (data.type) {
                case 'chat_message':
                    appendMessage(data.message, currentUserId);
                    showTyping(null, false);
                    // Mark read if message is from the other person
                    if (String(data.message.sender_id) !== String(currentUserId) && chatSocket.readyState === WebSocket.OPEN) {
                        chatSocket.send(JSON.stringify({ type: 'mark_read' }));
                    }
                    break;

                case 'typing':
                    showTyping(data.username, data.is_typing);
                    break;

                case 'presence':
                    // Optional: update online indicator in header
                    var presenceEl = document.getElementById('userPresence');
                    if (presenceEl && data.username) {
                        presenceEl.textContent = data.status === 'online' ? 'Online' : 'Offline';
                        presenceEl.className = 'badge ' + (data.status === 'online' ? 'bg-success' : 'bg-secondary');
                    }
                    break;

                case 'messages_read':
                    // Could update read receipts on own messages
                    break;

                case 'error':
                    console.warn('Chat error:', data.message);
                    break;
            }
        };
    }

    function sendTyping(isTypingNow) {
        if (!chatSocket || chatSocket.readyState !== WebSocket.OPEN) return;
        if (isTyping === isTypingNow) return;
        isTyping = isTypingNow;
        chatSocket.send(JSON.stringify({
            type: 'typing',
            is_typing: isTypingNow,
        }));
    }

    function initChat() {
        const form = document.getElementById('messageForm');
        const chatMessages = document.getElementById('chatMessages');
        if (!form || !chatMessages) return;

        const conversationId = form.dataset.conversationId;
        const currentUserId = form.dataset.userId;
        if (!conversationId || !currentUserId) return;

        scrollToBottom(chatMessages);
        connectWebSocket(conversationId, currentUserId);

        const input = form.querySelector('input[name="content"]');
        if (!input) return;

        // Typing indicator
        input.addEventListener('input', function () {
            sendTyping(true);
            clearTimeout(typingTimeout);
            typingTimeout = setTimeout(function () {
                sendTyping(false);
            }, 1500);
        });

        form.addEventListener('submit', function (e) {
            e.preventDefault();
            const content = input.value.trim();
            if (!content) return;

            if (chatSocket && chatSocket.readyState === WebSocket.OPEN) {
                chatSocket.send(JSON.stringify({
                    type: 'chat_message',
                    content: content,
                }));
                input.value = '';
                sendTyping(false);
                clearTimeout(typingTimeout);
            } else {
                // Fallback to HTTP if WebSocket is down
                fetch('/messaging/send/' + conversationId + '/', {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': getCookie('csrftoken'),
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: 'content=' + encodeURIComponent(content),
                })
                    .then(function (r) { return r.json(); })
                    .then(function (data) {
                        if (data.success && data.message) {
                            appendMessage(data.message, currentUserId);
                            input.value = '';
                        }
                    })
                    .catch(function (err) {
                        console.error(err);
                        alert('Failed to send message. Please try again.');
                    });
            }
        });

        // Close socket when leaving page
        window.addEventListener('beforeunload', function () {
            if (chatSocket) {
                chatSocket.close();
            }
        });
    }

    document.addEventListener('DOMContentLoaded', initChat);
})();
