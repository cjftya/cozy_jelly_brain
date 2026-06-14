from sim.tool.tool_type import ToolType
from sim.tool.use_tool import UseTool
from sim.tool.move_tool import MoveTool
from sim.tool.inspect_tool import InspectTool
from sim.tool.speak_tool import SpeakTool
from sim.tool.rest_tool import RestTool
from sim.tool.none_tool import NoneTool
from sim.tool.explore_tool import ExploreTool
from sim.tool.give_tool import GiveTool
from sim.tool.take_tool import TakeTool
from sim.tool.web_search_tool import WebSearchTool
from sim.tool.build_raft_tool import BuildRaftTool
from sim.tool.resurrect_tool import ResurrectTool
from sim.tool.release_tool import ReleaseTool

class ToolManager:
    TOOL_CLASSES = {
        ToolType.MOVE_TO: MoveTool,
        ToolType.INSPECT: InspectTool,
        ToolType.SPEAK: SpeakTool,
        ToolType.REST: RestTool,
        ToolType.NONE: NoneTool,
        ToolType.USE: UseTool,
        ToolType.GIVE: GiveTool,
        ToolType.TAKE: TakeTool,
        ToolType.WEB_SEARCH: WebSearchTool,
        ToolType.EXPLORE: ExploreTool,
        ToolType.BUILD_RAFT: BuildRaftTool,
        ToolType.RESURRECT: ResurrectTool,
        ToolType.RELEASE: ReleaseTool
    }

    def __init__(self):
        self.tools = {}

    def add_tool(self, tool):
        self.tools[tool.get_tool_type()] = tool

    def remove_tool(self, tool_type):
        self.tools.pop(tool_type, None)

    def add_available_tool_type(self, tool_type):
        if tool_type in self.TOOL_CLASSES and tool_type not in self.tools:
            self.tools[tool_type] = self.TOOL_CLASSES[tool_type]()

    def add_all_available_tool_types(self, tool_types):
        for tool_type in tool_types:
            self.add_available_tool_type(tool_type)

    def remove_available_tool_type(self, tool_type):
        self.remove_tool(tool_type)

    def get_available_tool_types(self):
        return list(self.tools.keys())

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

    def get_tools_manual(self, available_tool_types=None):
        tools_context = []
        prefix = "  "
        if available_tool_types is None:
            available_tool_types = list(self.tools.keys())

        if not available_tool_types:
            none_tool = self.tools.get(ToolType.NONE)
            if not none_tool:
                none_tool = NoneTool()
            return prefix + none_tool.get_manual()

        for tool_type in available_tool_types:
            if self.has_tool_by_type(tool_type):
                tools_context.append(prefix + self.tools[tool_type].get_manual())
        return "\n".join(tools_context)