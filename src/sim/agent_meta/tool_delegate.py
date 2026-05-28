from sim.tool.tool_type import ToolType

class ToolDelegate:
    def __init__(self):
        self.available_tool_types = []

    def get_available_tool_types(self):
        return self.available_tool_types

    def add_available_tool_type(self, tool_type):
        self.available_tool_types.append(tool_type)

    def add_all_available_tool_types(self, tool_types):
        self.available_tool_types.extend(tool_types)

    def remove_available_tool_type(self, tool_type):
        self.available_tool_types.remove(tool_type)

    def clear_available_tool_types(self):
        self.available_tool_types = []
        
    