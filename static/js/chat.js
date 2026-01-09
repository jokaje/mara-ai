class MaraChat {
    constructor() {
        this.currentSessionId = null;
        this.sessions = new Map();
        this.ws = null;
        this.isStreaming = false;
        this.currentStreamingElement = null;
        
        this.initializeElements();
        this.bindEvents();
        this.loadSessions();
        this.createSession();
    }
    
    initializeElements() {
        this.elements = {
            chatList: document.getElementById('chat-list'),
            chatMessages: document.getElementById('chat-messages'),
            messageInput: document.getElementById('message-input'),
            sendButton: document.getElementById('send-button'),
            newChatBtn: document.getElementById('new-chat-btn'),
            status: document.getElementById('status')
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
        session.messages.forEach(msg => this.addMessageToUI(msg));
        this.updateChatList();
        this.connectWebSocket();
    }
    
    deleteSession(sessionId) {
        if (this.sessions.size <= 1) return alert('Mindestens einen Chat behalten!');
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
            JSON.parse(saved).forEach(sessionData => {
                sessionData.createdAt = new Date(sessionData.createdAt);
                sessionData.messages = sessionData.messages || [];
                this.sessions.set(sessionData.id, sessionData);
            });
        }
    }
    
    connectWebSocket() {
        if (this.ws) this.ws.close();
        
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/${this.currentSessionId}`;
        console.log('🔌 WS:', wsUrl);
        
        this.updateStatus('Verbinde...', 'connecting');
        this.ws = new WebSocket(wsUrl);
        
        this.ws.onopen = () => {
            console.log('✅ WS OFFEN');
            this.updateStatus('Verbunden', 'connected');
        };
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log('📨 WS RAW:', data);  // LIVE DEBUG!
            this.handleMessage(data);
        };
        
        this.ws.onerror = (e) => console.error('❌ WS ERROR:', e);
        this.ws.onclose = () => {
            console.log('🔌 WS GESCHLOSSEN');
            this.updateStatus('Getrennt', 'disconnected');
        };
    }
    
    updateStatus(text, className) {
        this.elements.status.textContent = text;
        this.elements.status.className = `status ${className}`;
    }
    
    sendMessage() {
        const message = this.elements.messageInput.value.trim();
        if (!message || !this.ws || this.ws.readyState !== WebSocket.OPEN) return;
        
        console.log('📤 SEND:', message);
        
        const userMessage = { role: 'user', content: message, timestamp: new Date() };
        this.addMessageToUI(userMessage);
        this.addMessageToSession(userMessage);
        
        this.ws.send(JSON.stringify({ message }));
        this.elements.messageInput.value = '';
        this.elements.sendButton.disabled = true;
        this.isStreaming = true;
        
        this.currentStreamingElement = this.addMessageToUI({
            role: 'assistant', content: '', timestamp: new Date(), isStreaming: true
        });
    }
    
    handleMessage(data) {
        console.log('🔄 HANDLE:', data.type, data.content?.slice(0,20));
        
        if (data.type === 'stream_chunk') {
            console.log('📦 CHUNK LIVE:', data.content);
            if (this.currentStreamingElement) {
                const contentEl = this.currentStreamingElement.querySelector('.message-content');
                contentEl.textContent += data.content;
                contentEl.scrollIntoView({ behavior: 'smooth' });
            }
        } else if (data.type === 'stream_start') {
            console.log('🎬 START');
            if (this.currentStreamingElement) {
                this.currentStreamingElement.querySelector('.message-content').classList.add('streaming-text');
            }
        } else if (data.type === 'stream_end') {
            console.log('✅ ENDE');
            if (this.currentStreamingElement) {
                this.currentStreamingElement.querySelector('.message-content').classList.remove('streaming-text');
                this.currentStreamingElement = null;
            }
            this.isStreaming = false;
            this.elements.sendButton.disabled = false;
        } else if (data.type === 'error') {
            console.error('💥 ERROR:', data.content);
            this.addMessageToUI({ role: 'system', content: `Fehler: ${data.content}`, timestamp: new Date() });
            this.isStreaming = false;
            this.elements.sendButton.disabled = false;
            this.currentStreamingElement = null;
        }
        
        this.elements.chatMessages.scrollTop = this.elements.chatMessages.scrollHeight;
    }
    
    addMessageToUI(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${message.role}-message`;
        
        const header = document.createElement('div');
        header.className = 'message-header';
        header.textContent = message.role === 'user' ? 'Du' : 'Mara';
        
        const content = document.createElement('div');
        content.className = 'message-content';
        content.textContent = message.content;
        if (message.isStreaming) content.classList.add('streaming-text');
        
        messageDiv.appendChild(header);
        messageDiv.appendChild(content);
        this.elements.chatMessages.appendChild(messageDiv);
        this.elements.chatMessages.scrollTop = this.elements.chatMessages.scrollHeight;
        return messageDiv;
    }
    
    addMessageToSession(message) {
        const session = this.sessions.get(this.currentSessionId);
        if (session) {
            session.messages.push(message);
            if (session.messages.length === 1) {
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
            
            const preview = document.createElement('div');
            preview.className = 'preview';
            preview.textContent = session.messages[session.messages.length - 1]?.content?.slice(0, 50) || 'Neuer Chat';
            
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
