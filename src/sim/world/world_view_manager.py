from sim.agent_meta.vital_state import GenderType

class WorldViewManager:
    def __init__(self, world_system_manager):
        self.world_system_manager = world_system_manager

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
        time_engine = self.world_system_manager.time_engine
        weather_engine = self.world_system_manager.weather_engine
        
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
        space = self.world_system_manager.object_manager.find_space(location)
        location_detail = space.detail

        # 지도 초기화
        self.world_system_manager.map_engine.init_map(root_agent)
        
        # 지도 컨텍스트, 아이템 컨텍스트, 에이전트 컨텍스트
        ascii_map = self.world_system_manager.map_engine.get_map_context()
        items_view = self.world_system_manager.map_engine.get_map_objects_context()
        agents_view = self.world_system_manager.map_engine.get_map_agents_context(root_agent)

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

    def update_agent_log_view(self, agent, result):
        # 1. 문자열로 들어왔거나 "None" 텍스트인 경우 방어 처리
        if not result or result == "None":
            return None
            
        # 2. 혹시 result가 딕셔너리가 아니라 문자열(JSON) 상태라면 파싱 시도
        if isinstance(result, str):
            try:
                import json
                result = json.loads(result)
            except Exception:
                return f"--- CRITICAL: LOG PARSE ERROR ---\nRaw: {result}"

        # 3. 안전하게 데이터 추출
        subjective_perception = result.get('subjective_perception', '')
        unconscious_impulse = result.get('unconscious_impulse', '')
        internal_strategy = result.get('internal_strategy', '')
        
        action_call = result.get('action_call', {}) or {} # None 방지
        function = action_call.get('function', 'NONE')
        parameters = action_call.get('parameters', {})
        reason = action_call.get('reason', 'No reason provided.')
        
        # 4. 무의식 파편 가로 정렬 뷰 포매팅 (아까 정한 블록 스타일)
        if unconscious_impulse:
            impulses = [imp.strip() for imp in unconscious_impulse.split(',') if imp.strip()]
            unconscious_str = "  ".join([f"▶ [{imp}]" for imp in impulses])
        else:
            unconscious_str = "▶ [NONE]"

        # 5. Graph DB 메모리 파트 예외 방어 및 파싱
        memories_to_save = result.get('memories_to_save', [])
        # 만약 LLM이 텍스트 형태로 중복 직렬화해서 보냈을 경우 2차 방어
        if isinstance(memories_to_save, str):
            try:
                import json
                memories_to_save = json.loads(memories_to_save)
            except Exception:
                memories_to_save = []

        memories_str = ''
        if memories_to_save:
            for memory in memories_to_save:
                try:
                    memories_str += f"\n[RELATION] {memory.get('subject')} ──({memory.get('relation')})──> {memory.get('object')}\n"
                    memories_str += f" └─ [METADATA] {memory.get('metadata', {})}\n"
                except Exception:
                    continue
        else:
            memories_str = "[NO GRAPH MEMORY UPDATE]"

        # 6. 최종 압축 템플릿 출력
        agent_log = f"""
❖ SUBJECTIVE REFRACTION (주관적 환경 왜곡 수용)
"{subjective_perception}"

❖ UNCONSCIOUS IMPULSE (무의식적 욕구 분출)
{unconscious_str}

❖ INTERNAL STRATEGY (단독 행동 및 생존 전략)
{internal_strategy}

❖ SYSTEM ACTION EXECUTION (최종 의사결정 집행)
• FUNCTION : {str(function).upper()}
• PARAMS   : {parameters}
• REASON   : {reason}

❖ KUZU GRAPH MEMORY UPDATE (시냅스 기억 저장 로그)
{memories_str.strip()}


----------------------------------------------------------------------
"""
        return agent_log
        
        