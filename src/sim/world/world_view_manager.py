class WorldViewManager:
    def __init__(self, world_system_manager):
        self.world_system_manager = world_system_manager

    def update_world_details_view(self):
        time_engine = self.world_system_manager.time_engine
        weather_engine = self.world_system_manager.weather_engine

        weather_type = weather_engine.weather_type
        weather_description = weather_engine.get_weather_description(weather_type)

        view_data = f"""
[WORLD] Date: {time_engine.get_date()} | Clock: {time_engine.get_clock()}
[WEATHER] {weather_type}
----------------------------------------------------------------------
• Day of Week : {time_engine.day_of_week}
• Current Day Cycle : {time_engine.day_cycle}
• Current Month Season : {time_engine.season}
• Climate Environment Description : {weather_description}
"""
        return view_data

    def update_agent_light_log_view(self, agent, result):
        if isinstance(result, str):
            try:
                import json

                result = json.loads(result)
            except Exception:
                return f"--- CRITICAL: LOG PARSE ERROR ---\nRaw: {result}"

        subjective_perception = result.get("subjective_perception", "")
        internal_strategy = result.get("internal_strategy", "")

        action_call = result.get("action_call", {}) or {}  # None 방지
        function = action_call.get("function", "NONE")
        reason = action_call.get("reason", "No reason provided.")

        agent_log = f"""
<{agent.name}>
--[Subjective Perception]--
{subjective_perception}
--[Internal Strategy]--
{internal_strategy}
--[System Action Execution]--
• Tool : {str(function).upper()}
• Reason : {reason}
──────────────────
"""
        return agent_log

    def update_agent_log_view(self, agent, result):
        if not result or result == "None":
            return None

        if isinstance(result, str):
            try:
                import json

                result = json.loads(result)
            except Exception:
                return f"--- CRITICAL: LOG PARSE ERROR ---\nRaw: {result}"

        subjective_perception = result.get("subjective_perception", "")
        unconscious_impulse = result.get("unconscious_impulse", "")
        internal_strategy = result.get("internal_strategy", "")

        action_call = result.get("action_call", {}) or {}  # None 방지
        function = action_call.get("function", "NONE")
        parameters = action_call.get("parameters", {})
        reason = action_call.get("reason", "No reason provided.")

        if unconscious_impulse:
            impulses = [
                imp.strip() for imp in unconscious_impulse.split(",") if imp.strip()
            ]
            unconscious_str = "  ".join([f"▶ [{imp}]" for imp in impulses])
        else:
            unconscious_str = "▶ [NONE]"

        memories_to_save = result.get("memories_to_save", [])
        if isinstance(memories_to_save, str):
            try:
                import json

                memories_to_save = json.loads(memories_to_save)
            except Exception:
                memories_to_save = []

        memories_str = ""
        if memories_to_save:
            for memory in memories_to_save:
                try:
                    memories_str += f"\n[RELATION] {memory.get('subject')} ──({memory.get('relation')})──> {memory.get('object')}\n"
                    memories_str += f" └─ [METADATA] {memory.get('metadata', {})}\n"
                except Exception:
                    continue
        else:
            memories_str = "[NO GRAPH MEMORY UPDATE]"

        agent_log = f"""
❖ SUBJECTIVE REFRACTION
{subjective_perception}

❖ UNCONSCIOUS IMPULSE
{unconscious_str}

❖ INTERNAL STRATEGY
{internal_strategy}

❖ SYSTEM ACTION EXECUTION
• FUNCTION : {str(function).upper()}
• PARAMS   : {parameters}

❖ KUZU GRAPH MEMORY UPDATE
{memories_str.strip()}


----------------------------------------------------------------------
"""
        return agent_log
