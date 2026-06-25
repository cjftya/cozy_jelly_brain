class BaseTool:
    def __init__(self, name, tool_type):
        self.name = name
        self.tool_type = tool_type

    def execute(self, params, agent, world_system_manager):
        pass

    def get_name(self):
        return self.name

    def get_tool_type(self):
        return self.tool_type

    def get_description(self):
        return None

    def get_params(self):
        return None

    def get_manual(self):
        return f"- **{self.name}**: {self.get_params()} - {self.get_description()}"
