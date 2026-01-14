console.log('Mara Chat Client v7.0 (MindBar Thought + Dynamic Emotion) geladen');

class MaraChat {
    constructor() {
        this.currentSessionId = null;
        this.sessions = new Map();
        this.ws = null;

        this.isStreaming = false;
        this.currentStreamingElement = null;
        this.accumulatedStreamText = "";

        this.initializeElements();
        this.bindEvents();
        this.loadSessions();

        if (this.sessions.size === 0) {
            this.createSession();
        } else {
            const lastSessionId = Array.from(this.sessions.keys()).pop();
            this.switchToSession(lastSessionId);
        }
    }

    initializeElements() {
        this.elements = {
            chatList: document.getElementById('chat-list'),
            chatMessages: document.getElementById('chat-messages'),
            messageInput: document.getElementById('message-input'),
            sendButton: document.getElementById('send-button'),
            newChatBtn: document.getElementById('new-chat-btn'),
            status: document.getElementById('status'),
            mindBar: document.getElementById('mind-bar'),
            thoughtDisplay: document.getElementById('thought-display'),
            emotionIndicator: document.getElementById('emotion-indicator')
        };
    }

    bindEvents() {
        this.elements.sendButton.addEventListener('click', () => this.sendMessage());
        this.elements.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        this.elements.newChatBtn.addEventListener('click', () => this.createSession());
    }

    updateStatus(text, className) {
        if (this.elements.status) {
            this.elements.status.textContent = text;
            this.elements.status.className = `status ${className}`;
        }
    }

    /**
     * Ziel:
     * - Grauer Balken: thought
     * - Oben rechts: Emotion: <emotion>
     */
    updateMindBar(thought, emotion) {
        const td = this.elements.thoughtDisplay;
        const mb = this.elements.mindBar;
        const ei = this.elements.emotionIndicator;
        const st = this.elements.status;

        if (td && typeof thought === 'string' && thought.trim().length > 0) {
            td.textContent = thought;
        }

        if (typeof emotion === 'string' && emotion.trim().length > 0) {
            if (mb) {
                mb.className = 'mind-bar';
                mb.classList.add(emotion);
            }
            if (ei) {
                ei.title = `Aktuelle Emotion: ${emotion}`;
            }
            if (st) {
                // Verbindungsklasse nicht zerstören, nur Text ändern
                st.textContent = `Emotion: ${emotion}`;
                if (!st.className.includes('connected') &&
                    !st.className.includes('connecting') &&
                    !st.className.includes('disconnected')) {
                    st.className = 'status connected';
                }
            }
        }
    }

    generateSessionId() {
        return 'chat_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    createSession() {
        const sessionId = this.generateSessionId();
        const session = { id: sessionId, title: 'Neuer Chat', messages: [], createdAt: new Date() };
        this.sessions.set(sessionId, session);
        this.switchToSession(sessionId);
        this.saveSessions();
        this.updateChatList();
    }

    switchToSession(sessionId) {
        this.currentSessionId = sessionId;
        const session = this.sessions.get(sessionId);

        this.elements.chatMessages.innerHTML = '';
        if (session && session.messages) {
            session.messages.forEach(msg => this.addMessageToUI(msg));
        }

        this.updateChatList();
        this.connectWebSocket();
        this.scrollToBottom();
        this.updateMindBar("Bereit.", "neutral");
    }

    deleteSession(sessionId) {
        if (this.sessions.size <= 1) {
            alert('Mindestens einen Chat behalten!');
            return;
        }
        if (confirm('Chat löschen?')) {
            this.sessions.delete(sessionId);
            if (this.currentSessionId === sessionId) {
                const firstSessionId = this.sessions.keys().next().value;
                this.switchToSession(firstSessionId);
            }
            this.saveSessions();
            this.updateChatList();
        }
    }

    saveSessions() {
        const sessionsArray = Array.from(this.sessions.entries()).map(([id, session]) => ({
            ...session, createdAt: session.createdAt.toISOString()
        }));
        localStorage.setItem('mara-chat-sessions', JSON.stringify(sessionsArray));
    }

    loadSessions() {
        const saved = localStorage.getItem('mara-chat-sessions');
        if (saved) {
            try {
                const parsed = JSON.parse(saved);
                parsed.forEach(sessionData => {
                    sessionData.createdAt = new Date(sessionData.createdAt);
                    sessionData.messages = sessionData.messages || [];
                    this.sessions.set(sessionData.id, sessionData);
                });
            } catch (e) {
                console.error("Fehler beim Laden:", e);
            }
        }
    }

    connectWebSocket() {
        if (this.ws) this.ws.close();

        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/${this.currentSessionId}`;

        this.updateStatus('Verbinde...', 'connecting');
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
            this.updateStatus('Verbunden', 'connected');
            this.updateMindBar("Bereit.", "neutral");
            this.elements.sendButton.disabled = false;
        };

        this.ws.onmessage = (event) => {
            let data;
            try {
                data = JSON.parse(event.data);
            } catch (e) {
                console.warn("Nicht-JSON:", event.data);
                return;
            }
            this.handleMessage(data);
        };

        this.ws.onclose = () => {
            this.updateStatus('Getrennt', 'disconnected');
            this.elements.sendButton.disabled = true;
        };

        this.ws.onerror = () => {
            this.updateStatus('Fehler', 'disconnected');
        };
    }

    sendMessage() {
        const message = this.elements.messageInput.value.trim();
        if (!message || !this.ws || this.ws.readyState !== WebSocket.OPEN) return;

        const userMessage = { role: 'user', content: message, timestamp: new Date() };
        this.addMessageToUI(userMessage);
        this.addMessageToSession(userMessage);

        // Streaming vorbereiten (Assistant-Bubble erst bei stream_start!)
        this.isStreaming = true;
        this.accumulatedStreamText = "";
        this.currentStreamingElement = null;

        this.ws.send(JSON.stringify({ message }));
        this.elements.messageInput.value = '';
        this.elements.sendButton.disabled = true;

        // UI: wir warten jetzt auf meta + stream_start
        this.updateStatus('Sende...', 'connecting');
        this.updateMindBar("Sende...", "neutral");
    }

    handleMessage(data) {
        // Debug: falls du sehen willst, ob thought wirklich kommt
        // if (data?.type === 'meta') console.log("META RAW:", data);

        if (data.type === 'meta') {
            this.updateMindBar(data.thought, data.emotion);
            return;
        }

        if (data.type === 'stream_start') {
            // Assistant Bubble erstellen
            this.currentStreamingElement = this.addMessageToUI({
                role: 'assistant',
                content: '',
                timestamp: new Date(),
                isStreaming: true
            });
            return;
        }

        if (data.type === 'text') {
            if (this.currentStreamingElement) {
                const contentEl = this.currentStreamingElement.querySelector('.message-content');
                const chunk = data.content || '';
                contentEl.textContent += chunk;
                this.accumulatedStreamText += chunk;
                this.scrollToBottom();
            }
            return;
        }

        if (data.type === 'stream_end') {
            this.finalizeStreamingMessage();
            this.updateStatus('Verbunden', 'connected');
            this.updateMindBar("Bereit.", "neutral");
            return;
        }

        if (data.type === 'error') {
            console.error('💥 Error:', data.content);
            this.addMessageToSession({ role: 'system', content: `Fehler: ${data.content}`, timestamp: new Date() });

            this.isStreaming = false;
            this.elements.sendButton.disabled = false;

            this.updateStatus('Fehler', 'disconnected');
            this.updateMindBar("Fehler aufgetreten.", "neutral");
            return;
        }

        if (data.type === 'system') {
            // Optional: ignorieren oder als Status anzeigen
            // this.updateStatus(data.content || 'Verbunden', 'connected');
            return;
        }
    }

    finalizeStreamingMessage() {
        if (this.currentStreamingElement) {
            const contentEl = this.currentStreamingElement.querySelector('.message-content');
            contentEl.classList.remove('streaming-text');

            const fullText = contentEl.textContent || this.accumulatedStreamText;

            if (fullText) {
                this.addMessageToSession({
                    role: 'assistant',
                    content: fullText,
                    timestamp: new Date()
                });
            }

            this.currentStreamingElement = null;
        }

        this.isStreaming = false;
        this.elements.sendButton.disabled = false;
        this.accumulatedStreamText = "";
    }

    addMessageToUI(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${message.role}-message`;

        const header = document.createElement('div');
        header.className = 'message-header';
        header.textContent = message.role === 'user' ? 'Du' : (message.role === 'system' ? 'System' : 'Mara');

        const content = document.createElement('div');
        content.className = 'message-content';
        content.textContent = message.content || '';
        if (message.isStreaming) content.classList.add('streaming-text');

        messageDiv.appendChild(header);
        messageDiv.appendChild(content);
        this.elements.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
        return messageDiv;
    }

    scrollToBottom() {
        this.elements.chatMessages.scrollTop = this.elements.chatMessages.scrollHeight;
    }

    addMessageToSession(message) {
        const session = this.sessions.get(this.currentSessionId);
        if (session) {
            session.messages.push(message);
            if (session.messages.length === 1 && message.role === 'user') {
                session.title = message.content.slice(0, 30) + '...';
                this.updateChatList();
            }
            this.saveSessions();
        }
    }

    updateChatList() {
        this.elements.chatList.innerHTML = '';
        this.sessions.forEach((session, sessionId) => {
            const chatItem = document.createElement('div');
            chatItem.className = `chat-item ${sessionId === this.currentSessionId ? 'active' : ''}`;
            chatItem.onclick = () => this.switchToSession(sessionId);

            const title = document.createElement('div');
            title.className = 'title';
            title.textContent = session.title;

            const lastMsg = session.messages.slice(-1)[0];
            const previewText = lastMsg ? (lastMsg.content || '').slice(0, 40) : 'Neuer Chat';

            const preview = document.createElement('div');
            preview.className = 'preview';
            preview.textContent = previewText;

            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'delete-btn';
            deleteBtn.textContent = '×';
            deleteBtn.onclick = (e) => { e.stopPropagation(); this.deleteSession(sessionId); };

            chatItem.append(title, preview, deleteBtn);
            this.elements.chatList.appendChild(chatItem);
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.maraChat = new MaraChat();
});
