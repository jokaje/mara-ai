
class ShortTermMemory:
    def __init__(self):
        self.conversation = []
    
    def add_message(self, role, content):
        self.conversation.append({
            'role': role,
            'content': content
        })
    
    def get_recent(self, limit=10):
        return self.conversation[-limit:]
    
    def get_all(self):
        return self.conversation
    
    def clear(self):
        self.conversation = []
