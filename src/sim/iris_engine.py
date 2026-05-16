import json
import re
from sim.iris_prompt import IrisPrompt
from sim.iris_memory import IrisMemory
from sim.iris_search import IrisSearch
from sim.iris_llm_api import IrisLlmApi
from sim.iris_function import IrisFunction
from log import Logger

class IrisEngine:
    def __init__(self, id):
        self.id = id
        self.iris_llm_api = IrisLlmApi()
        self.iris_memory = IrisMemory(db_path=f"../src/brain_db/[{self.id}]_brain")
        self.iris_search = IrisSearch()
        self.iris_function = IrisFunction()

    def start(self, llm_requester):
        self.iris_memory.start()
        self.iris_llm_api.set_llm_requester(llm_requester)

    def stop(self):
        self.iris_memory.stop()

    def run(self, user_input, agent):
        # STEP 1: 기억 소환 (Retrieval) - [VIVID]/[FAINT] 태그 포함
        memories = self._retrieve_memory(agent, user_input)
        Logger.log_debug(f"[{self.id}] Memory", memories if memories else "연관된 기억 없음")
        
        # STEP 2: 프롬프트 구성 (Context Building)
        raw_matrix = agent.get_personality_matrix()
        system_prompt = IrisPrompt.get_system_prompt(
            personality_matrix=raw_matrix,
            persona_context=agent.get_persona_context(),
            world_context=agent.get_world_context(),
            retrieved_memories=memories,
            response_style=agent.get_response_style(),
            participants=agent.get_participant_delegate().get_available_participants(),
            intrinsic_desires=agent.get_intrinsic_desires(),
            relationships=agent.get_relationships(),
            current_location=agent.get_location_delegate().get_current_location(),
            available_locations=agent.get_location_delegate().get_available_locations()
        )

        context = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]

        # STEP 3: 모델 호출 및 추론 (Inference)
        response = self.iris_llm_api.request(context=context)

        content = ""
        if isinstance(response, dict):
            content = response.get('message', {}).get('content', "")
        elif isinstance(response, str):
            content = str(response)

        if not content:
            Logger.log_debug("Error", "LLM으로부터 유효한 응답 내용을 받지 못했습니다.")
            return "인지 프로세스 중단..."
        
        # STEP 4: 결과 파싱 (Robust JSON Parsing)
        result = self.iris_llm_api.parse_llm_response(content)

        if result:
            # 사고 결과물 추출
            state_delta = result.get('state_delta', {})    # 이번 대화로 인한 심리 변화량
            new_memories = result.get('memories_to_save', []) # 새롭게 저장할 지식
            relationship_delta = result.get('relationship_delta', {}) # 이번 대화로 인한 관계 변화량
            
            self.iris_function.process_action_call(result.get('action_call', {}), agent)
            
            # STEP 5: 상태 업데이트 및 저장
            # 1. 감정 매트릭스 수치 갱신
            self.update_personality_matrix(state_delta, agent)
            
            # 2. 새로운 지식을 그래프 DB에 각인
            if new_memories:
                self.iris_memory.add_memory(new_memories, state_delta)

            # 3. 관계 변화량 갱신
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

        # 3. 최종 Valence 융합 (가중치 조절 가능)
        # 이성적(Logic)일수록 감정 수치를 0(중립)에 가깝게 감쇄(Damping) 시킴
        damping_factor = 1.0 - matrix['logic_emotion'] 
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

    def set_serper_api_key(self, api_key):
        self.iris_search.set_serper_api_key(api_key)