import json
import re
import os
from sim.core.jelly_prompt import JellyPrompt
from sim.core.jelly_memory import JellyMemory
from sim.core.jelly_llm_api import JellyLlmApi
from sim.core.jelly_function import JellyFunction
from sim.agent_meta.participants_delegate import ParticipantsDelegate
from sim.util.object_manager import ObjectManager
from sim.tool.tool_type import ToolType
from sim.core.event_bus import EventBus, EventType
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from sim.agent import Agent
from log import Logger

class JellyEngine:
    def __init__(self, id, world_system_manager, brain_root_dir_path=None):
        self.id = id
        self.core_llm_api = JellyLlmApi()
        if brain_root_dir_path:
            brain_path = f"{brain_root_dir_path}/{self.id}_brain"
            self.core_memory = JellyMemory(db_path=brain_path)
        else:
            self.core_memory = JellyMemory(db_path=f"[{self.id}]_brain")
            
        self.core_function = JellyFunction(world_system_manager)

    def start(self, llm_requester):
        self.core_memory.start()
        self.core_llm_api.set_llm_requester(llm_requester)

    def stop(self):
        self.core_memory.stop()

    def think_event_normal(self, agent, event_type, external_event, available_tool_types):
        detected_agents = agent.perceive_agents()
        names = []
        for d in detected_agents:
            if d.vital_state.is_alive:
                names.append(d.name)
            else:
                names.append(f"{d.name}(죽음)")
        participant_delegate = ParticipantsDelegate()
        participant_delegate.add_all_participants(names)

        detected_objects = agent.perceive_objects()
        object_manager = ObjectManager()
        object_manager.add_objects(detected_objects)
        available_objects = object_manager.get_objects_full_context()

        memories = self._retrieve_memory(agent, external_event, False)

        system_prompt = self._get_system_context(agent, participant_delegate, available_objects, available_tool_types, False, memories)

        return self._run_llm_core(agent, external_event, system_prompt)

    def think_event_detect_objects(self, agent, external_event, detected_objects, available_tool_types):
        detected_agents = agent.perceive_agents()
        names = []
        for d in detected_agents:
            if d.vital_state.is_alive:
                names.append(d.name)
            else:
                names.append(f"{d.name}(죽음)")
        participant_delegate = ParticipantsDelegate()
        participant_delegate.add_all_participants(names)

        object_manager = ObjectManager()
        object_manager.add_objects(detected_objects)
        available_objects = object_manager.get_objects_full_context()

        memories = self._retrieve_memory(agent, external_event, False)

        system_prompt = self._get_system_context(agent, participant_delegate, available_objects, available_tool_types, False, memories)

        return self._run_llm_core(agent, external_event, system_prompt)

    def think_event_speak(self, user_input, agent, available_agents, from_scan=False, available_tool_types=None):
        names = []
        for d in available_agents:
            if d.vital_state.is_alive:
                names.append(d.name)
            else:
                names.append(f"{d.name}(죽음)")
        participant_delegate = ParticipantsDelegate()
        participant_delegate.add_all_participants(names)

        detected_objects = agent.perceive_objects()
        object_manager = ObjectManager()
        object_manager.add_objects(detected_objects)
        available_objects = object_manager.get_objects_full_context()

        memories = None if from_scan else self._retrieve_memory(agent, user_input, True)

        system_prompt = self._get_system_context(agent, participant_delegate, available_objects, available_tool_types, True, memories)

        return self._run_llm_core(agent, user_input, system_prompt)

    def _get_system_context(self, agent, participant_delegate, available_objects, available_tool_types, is_dialogue_mode, memories=None):
        raw_matrix = agent.personality_delegate.get_matrix()
        relationship_matrix_context = agent.relationships.get_context(participant_delegate.get_available_participants())

        if not is_dialogue_mode:
            if ToolType.SPEAK in available_tool_types:
                available_tool_types.remove(ToolType.SPEAK)
            if ToolType.GIVE in available_tool_types:
                available_tool_types.remove(ToolType.GIVE)
        else:
            if ToolType.SPEAK not in available_tool_types:
                available_tool_types.append(ToolType.SPEAK)
            if ToolType.GIVE not in available_tool_types:
                available_tool_types.append(ToolType.GIVE)

        fixed_manual = agent.world_system_manager.tool_manager.get_tools_manual(available_tool_types)
        dynamic_manual = agent.dynamic_tool_manager.get_tools_manual(agent)

        return JellyPrompt.get_system_prompt(
            personality_matrix=raw_matrix,
            name=agent.name,
            persona_context=agent.persona_context,
            world_context=agent.world_context,
            retrieved_memories=memories,
            response_style=agent.response_style,
            available_participants=participant_delegate.get_available_participants(context_format=True),
            intrinsic_desires=agent.intrinsic_desires,
            relationship_score=relationship_matrix_context,
            current_location=agent.location_delegate.get_current_location(),
            available_locations=agent.location_delegate.get_available_locations(context_format=True),
            available_agent_inventory=agent.inventory.get_objects_full_context(),
            before_action=agent.before_action,
            before_action_reason=agent.before_action_reason,
            available_objects=available_objects,
            available_tools=fixed_manual,
            available_dynamic_tools=dynamic_manual,
            is_dialogue_mode=is_dialogue_mode,
            vital_context=agent.vital_state.get_context(),
            world_state_context=agent.world_system_manager.get_state_context()
        )

    def _run_llm_core(self, agent: "Agent", user_input, system_prompt):
        # print(system_prompt)

        context = []
        context.append({"role": "system", "content": system_prompt})
        context.append({"role": "user", "content": user_input})

        response = self.core_llm_api.request(context=context)

        content = ""
        if isinstance(response, dict):
            content = response.get('message', {}).get('content', "")
        elif isinstance(response, str):
            content = str(response)

        if not content:
            Logger.log_debug("Error", "LLM으로부터 유효한 응답 내용을 받지 못했습니다.")
            return "인지 프로세스 중단..."
        
        result = self.core_llm_api.parse_llm_response(content)

        print(result)

        if result:
            state_delta = result.get('state_delta', {})
            new_memories = result.get('memories_to_save', [])
            relationship_delta = result.get('relationship_delta', {})
        
            self.core_function.process_action_call(result.get('action_call', {}), agent)
            
            if state_delta:
                agent.personality_delegate.apply_state_delta(state_delta)
            
            if new_memories:
                self.core_memory.add_memory(new_memories, state_delta)

            if relationship_delta:
                agent.relationships.apply_relationship_delta(relationship_delta)

            subjective_perception = result.get('subjective_perception', '')
            internal_strategy = result.get('internal_strategy', '')
            if subjective_perception or internal_strategy:
                EventBus().publish(EventType.AGENT_PERCEPTION_UPDATED, {
                    "name": agent.name,
                    "perception": subjective_perception,
                    "strategy": internal_strategy
                })

            return result

        return f"데이터 해석 실패:\n{response}"

    def _retrieve_memory(self, agent, user_input, is_dialogue_mode):
        # 1. 매트릭스 기반 내부 감정 계산
        matrix = agent.personality_delegate.get_matrix()

        # 개방성(Open)이 높고 호기심(Curiosity)이 높을수록 긍정, 반대면 부정
        # curiosity_indifference는 0.0이 호기심이므로 (1.0 - val)로 계산
        internal_positivity = (matrix['defensive_open'] + (1.0 - matrix['curiosity_indifference'])) / 2
        internal_valence = (internal_positivity - 0.5) * 2 # -1.0 ~ 1.0 범위로 변환

        # 2. 관계 점수 기반 외부 감정 계산
        rel_valence = 0.0
        if is_dialogue_mode:
            sender_name = self._extract_sender_name(user_input)
            rel_score = agent.relationships.get_value(sender_name)
            rel_valence = (rel_score - 50.0) / 50.0 # -1.0 ~ 1.0 범위로 변환

        # 3. 최종 Valence 융합
        # 이성적일수록 감정을 감쇄시키되, 최소 0.3의 최소 감정선은 유지
        base_resonance = self.core_memory.emotional_resonance
        damping_factor = max(base_resonance, 1.0 - matrix['logic_emotion'])

        combined_valence = (internal_valence * 0.4 + rel_valence * 0.6) * damping_factor
        current_valence = round(combined_valence, 2)

        memories = self.core_memory.retrieve_memory(user_input, current_valence, top_k=3)
        memories = memories if len(memories) > 0 else "연관된 기억 없음"
        return memories

    def _extract_sender_name(self, text):
        match = re.search(r"\[From\s+([^\]]+)\]", text)
        if match:
            return match.group(1).strip()
        return "UNKNOWN"

    def perform_brain_cleanup(self):
        self.core_memory.perform_brain_cleanup()