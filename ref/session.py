# session.py
class SessionContextManager:
    def __init__(self):
        self.memory = {}

    def get(self, key, default=None):
        return self.memory.get(key, default)

    def set(self, key, value):
        self.memory[key] = value

    def append_history(self, entry):
        if "history" not in self.memory:
            self.memory["history"] = []
        self.memory["history"].append(entry)

    def clear(self):
        self.memory.clear()
