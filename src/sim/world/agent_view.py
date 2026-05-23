from sim.agent_meta.vital_state import GenderType

class AgentView:
    def __init__(self, world_context_manager):
        self.world_context_manager = world_context_manager

    def _draw_gauge(self, value):
        return f"[{'█' * int(value*10)}{'░' * (10 - int(value*10))}] {value*100:03.0f} %"

    def update_agent_details_view(self, agent):
        gender_context = "여성" if agent.vital_state.gender == GenderType.FEMALE else "남성"
        personality_matrix = agent.get_personality_matrix()
        view_data = f"""
[VITALS] Age: {agent.vital_state.age:05.2f} | Gender: {gender_context}
• [{agent.vital_state.health:06.2f}] {self._draw_gauge(agent.vital_state.health/100.0)} - 건강
• [{agent.vital_state.fatigue:06.2f}] {self._draw_gauge(agent.vital_state.fatigue/100.0)} - 피로
• [{agent.vital_state.hunger:06.2f}] {self._draw_gauge(agent.vital_state.hunger/100.0)} - 허기
[WARNING] {agent.vital_state.warning}
----------------------------------------------------------------------
[PERSONALITY]
• [{personality_matrix['logic_emotion']:.2f}] : {self._draw_gauge(personality_matrix['logic_emotion'])} - 이성 vs 감성
• [{personality_matrix['defensive_open']:.2f}] : {self._draw_gauge(personality_matrix['defensive_open'])} - 방어 vs 개방
• [{personality_matrix['fear_decisive']:.2f}] : {self._draw_gauge(personality_matrix['fear_decisive'])} - 공포 vs 결단
• [{personality_matrix['obedient_rebellious']:.2f}] : {self._draw_gauge(personality_matrix['obedient_rebellious'])} - 복종 vs 반항
• [{personality_matrix['curiosity_indifference']:.2f}] : {self._draw_gauge(personality_matrix['curiosity_indifference'])} - 호기심 vs 무관심
"""
        return view_data

    def update_world_details_view(self):
        time_engine = self.world_context_manager.time_engine
        weather_engine = self.world_context_manager.weather_engine
        
        weather_name = weather_engine.weather
        weather_description = weather_engine.get_weather_description(weather_name)
        
        view_data = f"""
[WORLD] Date: {time_engine.get_date()} | Clock: {time_engine.get_clock()}
[WEATHER] {weather_name}
----------------------------------------------------------------------
• Day of Week : {time_engine.day_of_week}
• Current Day Cycle : {time_engine.day_cycle}
• Current Month Season : {time_engine.season}
• Climate Environment Description : {weather_description}
"""
        return view_data

    def update_ascii_map_view(self, root_agent):
        # 정보 수집
        location = root_agent.get_location_delegate().get_current_location()
        space = self.world_context_manager.object_manager.find_space(location)
        location_detail = space.detail

        # 지도 초기화
        self.world_context_manager.map_engine.init_map(root_agent)
        
        # 지도 컨텍스트, 아이템 컨텍스트, 에이전트 컨텍스트
        ascii_map = self.world_context_manager.map_engine.get_map_context()
        items_view = self.world_context_manager.map_engine.get_map_objects_context()
        agents_view = self.world_context_manager.map_engine.get_map_agents_context(root_agent)

        view_data = f"""
• Location: {location} ({location_detail})
• Global Coordinates: [{space.position.x}, {space.position.y}]
• Space Size: [{space.size.x}, {space.size.y}]
───────────────────────────────────────────────────────────────────────────
{ascii_map}
───────────────────────────────────────────────────────────────────────────

• Agents In Area
{agents_view}

• Items In Area
{items_view}
"""
        return view_data