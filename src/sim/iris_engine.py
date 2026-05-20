import json
import re
from sim.iris_prompt import IrisPrompt
from sim.iris_memory import IrisMemory
from sim.iris_search import IrisSearch
from sim.iris_llm_api import IrisLlmApi
from sim.iris_function import IrisFunction
from sim.agent_meta.participants_delegate import ParticipantsDelegate
from sim.object_meta.object_manager import ObjectManager
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from sim.agent import Agent
from log import Logger

class IrisEngine:
    def __init__(self, id, world_context_manager):
        self.id = id
        self.iris_llm_api = IrisLlmApi()
        self.iris_memory = IrisMemory(db_path=f"../src/brain_db/[{self.id}]_brain")
        self.iris_search = IrisSearch()
        self.iris_function = IrisFunction(world_context_manager)

    def start(self, llm_requester):
        self.iris_memory.start()
        self.iris_llm_api.set_llm_requester(llm_requester)

    def stop(self):
        self.iris_memory.stop()

    def event(self, agent, event_type, external_event, available_tools=["none"]):
        available_participants = ParticipantsDelegate().get_available_participants()

        memories = self._retrieve_memory(agent, external_event)

        detected_objects = agent.perceive_objects()
        object_manager = ObjectManager()
        object_manager.add_objects(detected_objects)
        available_objects = object_manager.get_objects_full_context()

        raw_matrix = agent.get_personality_matrix()
        system_prompt = IrisPrompt.get_system_prompt(
            personality_matrix=raw_matrix,
            persona_context=agent.get_persona_context(),
            world_context=agent.get_world_context(),
            retrieved_memories=memories,
            response_style=agent.get_response_style(),
            available_participants=available_participants,
            intrinsic_desires=agent.get_intrinsic_desires(),
            relationships=agent.get_relationships(),
            current_location=agent.get_location_delegate().get_current_location(),
            available_locations=agent.get_location_delegate().get_available_locations(),
            available_agent_inventory=agent.get_inventory().get_objects_full_context(),
            available_objects=available_objects,
            available_tools=available_tools,
            is_dialogue_mode=False,
            vital_context=agent.get_vital_state().get_context(),
            world_state_context=agent.world_context_manager.get_state_context()
        )

        context = []
        context.append({"role": "system", "content": system_prompt})
        context.append({"role": "user", "content": external_event})

        return self._run_llm_core(context, agent)

    def search(self, agent, external_event, detected_objects, available_tools=["none"]):
        available_participants = ParticipantsDelegate().get_available_participants()

        memories = self._retrieve_memory(agent, external_event)

        object_manager = ObjectManager()
        object_manager.add_objects(detected_objects)
        available_objects = object_manager.get_objects_full_context()

        raw_matrix = agent.get_personality_matrix()
        system_prompt = IrisPrompt.get_system_prompt(
            personality_matrix=raw_matrix,
            persona_context=agent.get_persona_context(),
            world_context=agent.get_world_context(),
            retrieved_memories=memories,
            response_style=agent.get_response_style(),
            available_participants=available_participants,
            intrinsic_desires=agent.get_intrinsic_desires(),
            relationships=agent.get_relationships(),
            current_location=agent.get_location_delegate().get_current_location(),
            available_locations=agent.get_location_delegate().get_available_locations(),
            available_agent_inventory=agent.get_inventory().get_objects_full_context(),
            available_objects=available_objects,
            available_tools=available_tools,
            is_dialogue_mode=False,
            vital_context=agent.get_vital_state().get_context(),
            world_state_context=agent.world_context_manager.get_state_context()
        )

        context = []
        context.append({"role": "system", "content": system_prompt})
        context.append({"role": "user", "content": external_event})

        return self._run_llm_core(context, agent)

    def speak(self, user_input, agent, available_agents, from_scan=False, available_tools=["none"]):
        names = [d.name for d in available_agents]
        participant_delegate = ParticipantsDelegate()
        participant_delegate.add_all_participants(names)
        available_participants = participant_delegate.get_available_participants()

        memories = None if from_scan else self._retrieve_memory(agent, user_input)
        Logger.log_debug(f"[{self.id}] Memory", memories if memories else "연관된 기억 없음")

        detected_objects = agent.perceive_objects()
        object_manager = ObjectManager()
        object_manager.add_objects(detected_objects)
        available_objects = object_manager.get_objects_full_context()

        raw_matrix = agent.get_personality_matrix()
        system_prompt = IrisPrompt.get_system_prompt(
            personality_matrix=raw_matrix,
            persona_context=agent.get_persona_context(),
            world_context=agent.get_world_context(),
            retrieved_memories=memories,
            response_style=agent.get_response_style(),
            available_participants=available_participants,
            intrinsic_desires=agent.get_intrinsic_desires(),
            relationships=agent.get_relationships(),
            current_location=agent.get_location_delegate().get_current_location(),
            available_locations=agent.get_location_delegate().get_available_locations(),
            available_agent_inventory=agent.get_inventory().get_objects_full_context(),
            available_objects=available_objects,
            available_tools=available_tools,
            is_dialogue_mode=True,
            vital_context=agent.get_vital_state().get_context(),
            world_state_context=agent.world_context_manager.get_state_context()
        )

        context = []
        context.append({"role": "system", "content": system_prompt})
        context.append({"role": "user", "content": user_input})

        return self._run_llm_core(context, agent)

    def _run_llm_core(self, context, agent: "Agent"):
        response = self.iris_llm_api.request(context=context)

        content = ""
        if isinstance(response, dict):
            content = response.get('message', {}).get('content', "")
        elif isinstance(response, str):
            content = str(response)

        if not content:
            Logger.log_debug("Error", "LLM으로부터 유효한 응답 내용을 받지 못했습니다.")
            return "인지 프로세스 중단..."
        
        result = self.iris_llm_api.parse_llm_response(content)

        if result:
            state_delta = result.get('state_delta', {})
            new_memories = result.get('memories_to_save', [])
            relationship_delta = result.get('relationship_delta', {})
        
            self.iris_function.process_action_call(result.get('action_call', {}), agent)
            
            self.update_personality_matrix(state_delta, agent)
            
            if new_memories:
                self.iris_memory.add_memory(new_memories, state_delta)

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
        base_resonance = self.iris_memory.emotional_resonance
        damping_factor = max(base_resonance, 1.0 - matrix['logic_emotion'])

        combined_valence = (internal_valence * 0.4 + rel_valence * 0.6) * damping_factor
        current_valence = round(combined_valence, 2)

        return self.iris_memory.retrieve_memory(user_input, current_valence, top_k=3)

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
        self.iris_memory.perform_brain_cleanup()

    def set_serper_api_key(self, api_key):
        self.iris_search.set_serper_api_key(api_key)