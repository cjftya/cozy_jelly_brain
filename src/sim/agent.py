from sim.iris_engine import IrisEngine

class Agent:
    def __init__(self, name="UNKNOWN", identifier="UNKNOWN"):
        self.name = name
        self.identifier = identifier
        self.available_participants = []
        self.llm_requester = None
        self.iris_engine = IrisEngine(self.name)

        # 성격 매트릭스 (Personality Matrix)
        # logic_emotion : 감성적인가 이성적인가
        # defensive_open : 방어적인가 개방적인가
        # fear_decisive : 공포에 우유부단한가 용감하고 단호한가
        # obedient_rebellious : 복종적인가 반항적인가
        # curiosity_indifference : 호기심이 많은가 무관심한가
        self.personality_matrix = self.get_personality_matrix()
        self.relationship_map = None

        # 공간 정보
        self.current_location = ""
        self.available_locations = []

    def start(self, llm_requester):
        self.llm_requester = llm_requester
        self.iris_engine.start(llm_requester)

    def stop(self):
        self.llm_requester = None
        self.iris_engine.stop()
    
    def run(self, user_input):
        res = self.iris_engine.run(user_input, self)
        return res

    def get_personality_matrix(self):
        return None

    def get_persona_context(self):
        return None
    
    def get_world_context(self):
        return None

    def get_response_style(self):
        return None

    def get_intrinsic_desires(self):
        return None

    def get_relationships(self):
        if not self.relationship_map:
            return "식별된 관계 데이터가 없음."

        return "\n".join([f"- {name}: {score}" for name, score in self.relationship_map.items()])

    def support_web_search(self):
        return False

    def get_available_participants(self):
        return "\n".join([line for line in self.available_participants])

    def add_participant(self, participant):
        self.available_participants.append("- **" + participant + "**")
    
    def remove_participant(self, participant):
        self.available_participants.remove("- **" + participant + "**")

    def clear_participants(self):
        self.available_participants.clear()

    def add_all_participants(self, participants):
        for participant in participants:
            self.add_participant(participant)

    def get_current_location(self):
        return self.current_location

    def get_available_locations(self):
        return "\n".join([line for line in self.available_locations])

    def add_location(self, location):
        self.available_locations.append("- **" + location + "**")
    
    def remove_location(self, location):
        self.available_locations.remove("- **" + location + "**")

    def clear_locations(self):
        self.available_locations.clear()

    def add_all_locations(self, locations):
        for location in locations:
            self.add_location(location)

    def set_serper_api_key(self, api_key):
        if self.iris_engine:
            self.iris_engine.set_serper_api_key(api_key)