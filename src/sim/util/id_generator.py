class IdGenerator:
    def __init__(self):
        self.agent_id = 0
        self.object_id = 0

    def gen_agent_id(self):
        self.agent_id += 1
        return f"AGENT_{self.agent_id}"

    def gen_object_id(self):
        self.object_id += 1
        return f"OBJECT_{self.object_id}"
