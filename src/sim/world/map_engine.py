from sim.object_meta.object_type import ObjectType

class MapData:
    def __init__(self):
        self.w = 0
        self.h = 0
        self.objects = []
        self.agents = []

class MapEngine:
    def __init__(self, world_context_manager):
        self.world_context_manager = world_context_manager
        self.map_data = None

    def init_map(self, root_agent):
        self.map_data = None
        item_key = 'a'
        agent_key = 'A'

        # 모든 공간 로드
        spaces = self.world_context_manager.object_manager.get_objects_by_type(ObjectType.SPACE)
        for space in spaces:
            # 선택된 에이전트가 있는공간만 로드
            if root_agent.get_location_delegate().get_current_location() != space.name:
                continue
            
            map_data_info = MapData()
            map_data_info.w = space.size.x
            map_data_info.h = space.size.y

            # 해당 공간의 아이템 로드
            objects = self.world_context_manager.object_manager.find_childs(space)
            for obj in objects:
                map_data_info.objects.append([item_key, obj.name, obj.detail, obj.position.x, obj.position.y])
                item_key = chr(ord(item_key) + 1)

            # 해당 공간의 에이전트 로드
            global_agents = self.world_context_manager.agent_manager.get_agents()
            for agent in global_agents:
                if agent.get_location_delegate().get_current_location() == space.name:
                    map_data_info.agents.append([agent_key, agent.name, None, agent.position.x, agent.position.y])
                    agent_key = chr(ord(agent_key) + 1)

            self.map_data = map_data_info

    def get_map_data(self):
        return self.map_data

    def get_map_objects_context(self):
        items_view = ""
        for item in self.map_data.objects:
            items_view += f" > {item[0]}. {item[1]} ({item[2]}) [{item[3]}, {item[4]}]\n"
        return items_view

    def get_map_agents_context(self, root_agent):
        agents_view = ""
        for agent in self.map_data.agents:
            if agent[1] == root_agent.name:
                agents_view += f" > {agent[0]}. {agent[1]} [{agent[3]}, {agent[4]}] (YOU)\n"
                continue

            agents_view += f" > {agent[1]}. [{agent[3]}, {agent[4]}]\n"
        return agents_view

    def get_map_context(self):
        if self.map_data is None:
            return ""

        map_context = ""
        # 먼저 맵의 태두리를 size에 맞게 그린다
        for i in range(self.map_data.w + 2):
            map_context += "# "
        map_context += "\n"

        # 그 다음 맵의 내부를 size에 맞게 그린다
        for y in range(self.map_data.h + 1):
            map_context += "# "
            for x in range(self.map_data.w + 1):
                # 만약 agents나 objects가 있다면 해당 위치에 그린다
                if x < self.map_data.w:
                    skip_ground = False
                    for agent in self.map_data.agents:
                        if agent[3] == x and agent[4] == y:
                            map_context += agent[0] + " "
                            skip_ground = True
                    for obj in self.map_data.objects:
                        if obj[3] == x and obj[4] == y:
                            map_context += obj[0] + " "
                            skip_ground = True
                    if not skip_ground:
                        map_context += ". "
                else:
                    map_context += "# "

            map_context += "\n"

        # 마지막으로 맵의 태두리를 size에 맞게 그린다
        for i in range(self.map_data.w + 2):
            map_context += "# "
        map_context += "\n"

        return map_context