class AgentView:
    def __init__(self, world_context_manager):
        self.world_context_manager = world_context_manager

    def _draw_gauge(self, value):
        return f"[{'█' * int(value*10)}{'░' * (10 - int(value*10))}] {value*100:.0f}%"

    def update_agent_details_view(self, agent):
        personality_matrix = agent.get_personality_matrix()
        view_data = f"""
[PHYSICAL VITALS : 신체 상태]
-----------------------------------------
• 생명력 (Health)  :  {agent.vital_state.health:.2f} / 100  
• 피로도 (Fatigue) :  {agent.vital_state.fatigue:.2f} / 100  
• 허기짐 (Hunger)  :  {agent.vital_state.hunger:.2f} / 100  

⚠️ 시스템 경고 : {agent.vital_state.warning}


[HORMONAL MATRIX : 정신 매트릭스]
-----------------------------------------
• 이성 vs 감성 (Logic vs Emotion)
{self._draw_gauge(personality_matrix['logic_emotion'])}

• 방어 vs 개방 (Defensive vs Open)
{self._draw_gauge(personality_matrix['defensive_open'])}

• 공포 vs 결단 (Fear vs Decisive)
{self._draw_gauge(personality_matrix['fear_decisive'])}

• 복종 vs 반항 (Obedient vs Rebellious)
{self._draw_gauge(personality_matrix['obedient_rebellious'])}

• 호기심 vs 무관심 (Curiosity vs Indifference)
{self._draw_gauge(personality_matrix['curiosity_indifference'])}
=========================================
"""
        return view_data