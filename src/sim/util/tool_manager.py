from sim.tool.tool_type import ToolType
from sim.tool.move_tool import MoveTool
from sim.tool.inspect_tool import InspectTool
from sim.tool.speak_tool import SpeakTool
from sim.tool.rest_tool import RestTool
from sim.tool.none_tool import NoneTool
from sim.tool.explore_tool import ExploreTool
from sim.tool.custom_rule_tool import CustomRuleTool
from sim.tool.web_search_tool import WebSearchTool
from sim.tool.craft_tool import CraftTool

class ToolManager:
    def __init__(self):
        self.tools = {
            ToolType.MOVE_TO: MoveTool(),
            ToolType.INSPECT: InspectTool(),
            ToolType.SPEAK: SpeakTool(),
            ToolType.REST: RestTool(),
            ToolType.NONE: NoneTool(),
            ToolType.CUSTOM_RULE: CustomRuleTool(),
            ToolType.WEB_SEARCH: WebSearchTool(),
            ToolType.CRAFT: CraftTool(),
            
            # cast away sim specific tools
            ToolType.EXPLORE: ExploreTool()
        }

    def add_tool(self, tool):
        self.tools[tool.get_tool_type()] = tool

    def remove_tool(self, tool_type):
        self.tools.pop(tool_type, None)

    def has_tool_by_type(self, tool_type):
        return tool_type in self.tools

    def has_tool_by_name(self, tool_name):
        for tool in self.tools.values():
            if tool.get_name() == tool_name:
                return True
        return False

    def get_tool_by_name(self, tool_name):
        for tool in self.tools.values():
            if tool.get_name() == tool_name:
                return tool
        return None

    def get_tool_by_type(self, tool_type):
        return self.tools.get(tool_type)

    def get_tools(self):
        return self.tools.values()

    def get_tools_manual(self, available_tool_types):
        tools_context = []
        if available_tool_types is None:
            return self.tools[ToolType.NONE].get_manual()

        for tool_type in available_tool_types:
            if self.has_tool_by_type(tool_type):
                tools_context.append(self.tools[tool_type].get_manual())
        return "\n".join(tools_context)