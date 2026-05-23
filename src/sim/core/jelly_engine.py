import json
import re
from sim.core.jelly_prompt import JellyPrompt
from sim.core.jelly_memory import JellyMemory
from sim.core.jelly_search import JellySearch
from sim.core.jelly_llm_api import JellyLlmApi
from sim.core.jelly_function import JellyFunction
from sim.agent_meta.participants_delegate import ParticipantsDelegate
from sim.util.object_manager import ObjectManager
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from sim.agent import Agent
from log import Logger

class JellyEngine:
    def __init__(self, id, world_system_manager):
        self.id = id
        self.core_llm_api = JellyLlmApi()
        self.core_memory = JellyMemory(db_path=f"../src/brain_db/[{self.id}]_brain")
        self.core_search = JellySearch()
        self.core_function = JellyFunction(world_system_manager)

    def start(self, llm_requester):
        self.core_memory.start()
        self.core_llm_api.set_llm_requester(llm_requester)

    def stop(self):
        self.core_memory.stop()

    def event(self, agent, event_type, external_event, available_tools=["none"]):
        available_participants = ParticipantsDelegate().get_available_participants()

        detected_objects = agent.perceive_objects()
        object_manager = ObjectManager()
        object_manager.add_objects(detected_objects)
        available_objects = object_manager.get_objects_full_context()

        memories = self._retrieve_memory(agent, external_event)

        system_prompt = self._get_system_context(agent, available_participants, available_objects, available_tools, False, memories)

        context = []
        context.append({"role": "system", "content": system_prompt})
        context.append({"role": "user", "content": external_event})

        return self._run_llm_core(context, agent)

    def search(self, agent, external_event, detected_objects, available_tools=["none"]):
        available_participants = ParticipantsDelegate().get_available_participants()

        object_manager = ObjectManager()
        object_manager.add_objects(detected_objects)
        available_objects = object_manager.get_objects_full_context()

        memories = self._retrieve_memory(agent, external_event)

        system_prompt = self._get_system_context(agent, available_participants, available_objects, available_tools, False, memories)

        context = []
        context.append({"role": "system", "content": system_prompt})
        context.append({"role": "user", "content": external_event})

        return self._run_llm_core(context, agent)

    def speak(self, user_input, agent, available_agents, from_scan=False, available_tools=["none"]):
        names = [d.name for d in available_agents]
        participant_delegate = ParticipantsDelegate()
        participant_delegate.add_all_participants(names)
        available_participants = participant_delegate.get_available_participants()

        detected_objects = agent.perceive_objects()
        object_manager = ObjectManager()
        object_manager.add_objects(detected_objects)
        available_objects = object_manager.get_objects_full_context()

        memories = None if from_scan else self._retrieve_memory(agent, user_input)

        system_prompt = self._get_system_context(agent, available_participants, available_objects, available_tools, True, memories)

        context = []
        context.append({"role": "system", "content": system_prompt})
        context.append({"role": "user", "content": user_input})

        return self._run_llm_core(context, agent)

    def _get_system_context(self, agent, available_participants, available_objects, available_tools, is_dialogue_mode, memories=None):
        raw_matrix = agent.get_personality_matrix()
        return JellyPrompt.get_system_prompt(
            personality_matrix=raw_matrix,
            name=agent.name,
            persona_context=agent.get_persona_context(),
            world_context=agent.get_world_context(),
            retrieved_memories=memories,
            response_style=agent.get_response_style(),
            available_participants=available_participants,
            intrinsic_desires=agent.get_intrinsic_desires(),
            relationships=agent.get_relationships(),
            current_location=agent.get_location_delegate().get_current_location(),
            available_locations=agent.get_location_delegate().get_available_locations(context_format=True),
            available_agent_inventory=agent.get_inventory().get_objects_full_context(),
            available_objects=available_objects,
            available_tools=available_tools,
            is_dialogue_mode=is_dialogue_mode,
            vital_context=agent.get_vital_state().get_context(),
            world_state_context=agent.world_system_manager.get_state_context()
        )

    def _run_llm_core(self, context, agent: "Agent"):
        # system_prompt = context[0]["content"]
        # print(system_prompt)

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
            
            self.update_personality_matrix(state_delta, agent)
            
            if new_memories:
                self.core_memory.add_memory(new_memories, state_delta)

            if relationship_delta:
                self.update_relationship_delta(relationship_delta, agent)

            return result

        return f"데이터 해석 실패:\n{response}"

    def _retrieve_memory(self, agent, user_input):
        # 1. 매트릭스 기반 내부 감정 계산
        matrix = agent.get_personality_matrix()
        sender_name = self._extract_sender_name(user_input)

        # 개방성(Open)이 높고 호기심(Curiosity)이 높을수록 긍정, 반대면 부정
        # curiosity_indifference는 0.0이 호기심이므로 (1.0 - val)로 계산
        internal_positivity = (matrix['defensive_open'] + (1.0 - matrix['curiosity_indifference'])) / 2
        internal_valence = (internal_positivity - 0.5) * 2 # -1.0 ~ 1.0 범위로 변환

        # 2. 관계 점수 기반 외부 감정 계산
        rel_score = agent.relationship_map.get(sender_name, 0.0)
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
        match = re.search(r"\[EXTERNAL_SIGNAL:\s*([^\]]+)\]", text)
        if match:
            return match.group(1).strip()
        return "UNKNOWN"

    def update_personality_matrix(self, delta, agent):
        """매트릭스 수치 업데이트 및 경계값 고정(Clamping)"""
        for key, value in delta.items():
            if key in agent.personality_matrix:
                # 급격한 변화 방지를 위해 변화폭 제한
                limited_delta = max(-0.3, min(0.3, value)) 
                new_val = round(agent.personality_matrix[key] + limited_delta, 2)
                # 0.0 ~ 1.0 범위 강제
                agent.personality_matrix[key] = max(0.0, min(1.0, new_val))
        
        Logger.log_debug("Matrix Updated", agent.get_personality_matrix())

    def update_relationship_delta(self, delta_map, agent):
        for name, delta in delta_map.items():
            # 기존에 없던 이름이면 0.0(기본값)에서 시작하도록 처리
            current_score = agent.relationship_map.get(name, 0.0)
            new_score = max(0.0, min(100.0, current_score + delta)) # 0~100 사이로 고정
            agent.relationship_map[name] = round(new_score, 1)
        
        Logger.log_debug("Relationship Delta Updated", agent.get_relationships())

    def perform_brain_cleanup(self):
        self.core_memory.perform_brain_cleanup()

    def set_serper_api_key(self, api_key):
        self.core_search.set_serper_api_key(api_key)