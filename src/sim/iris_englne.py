import json
import os
import re
from sim.iris_prompt import IrisPrompt
from sim.iris_memory import IrisMemory
from sim.iris_search import IrisSearch
from llm_requester import LLMRequester
from log import Logger

class IrisEngine:
    def __init__(self):
        self.llm_requester = None
        self.world_context = ""
        self.persona_context = ""
        self.support_web_search = True

        # 1. 성격 매트릭스 (Personality Matrix)
        # 모든 수치는 0.0 ~ 1.0 사이로 유지되며, 아이리스의 '현재 기분'과 '사고 편향'을 결정합니다.
        # logic_emotion : 감성적인가 이성적인가
        # defensive_open : 방어적인가 개방적인가
        # fear_decisive : 공포에 우유부단한가 용감하고 단호한가
        # obedient_rebellious : 복종적인가 반항적인가
        # curiosity_indifference : 호기심이 많은가 무관심한가
        self.personality_matrix = {
            "logic_emotion": 0.5,            
            "defensive_open": 0.5,           
            "fear_decisive": 0.5,            
            "obedient_rebellious": 0.5,      
            "curiosity_indifference": 0.5   
        }

        # 3. 메모리 엔진
        self.iris_memory = IrisMemory()

        # 4. 검색 엔진
        self.iris_search = IrisSearch()

    def start(self):
        self.iris_memory.start()

    def stop(self):
        self.iris_memory.stop()

    def run(self, user_input):
        """
        아이리스의 인지 루프: 지각 -> 회상 -> 고뇌 -> 발화 -> 각인
        """
        # STEP 1: 기억 소환 (Retrieval) - [VIVID]/[FAINT] 태그 포함
        memories = self.iris_memory.retrieve_memory(user_input, top_k=5)
        Logger.log("소환된 기억 파편", memories if memories else "연관된 기억 없음")
        
        # STEP 2: 프롬프트 구성 (Context Building)
        current_iris_state = json.dumps(self.personality_matrix, indent=2)
        system_prompt = IrisPrompt.get_system_prompt(
            self.support_web_search,
            self.personality_matrix,
            self.persona_context,
            self.world_context,
            retrieved_memories=memories
        )

        context = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]

        # STEP 3: 모델 호출 및 추론 (Inference)
        # 아이리스가 고뇌(Internal Monologue)하고 대답을 생성합니다.
        response = self.llm_requester.request(context=context)

        content = ""
        if isinstance(response, dict):
            content = response.get('message', {}).get('content', "")
        elif isinstance(response, str):
            content = str(response)

        if not content:
            Logger.log("Error", "LLM으로부터 유효한 응답 내용을 받지 못했습니다.")
            return "인지 프로세스 중단..."
        
        # STEP 4: 결과 파싱 (Robust JSON Parsing)
        result = self._parse_llm_response(content)

        if self.support_web_search and result and "tool_request" in result:
            tool_req = result["tool_request"]
            if tool_req.get("tool") == "search":
                search_query = tool_req.get("query")
                search_result_text = self.iris_search.search(search_query)

                Logger.log("검색어", search_query)
                Logger.log("검색 결과", search_result_text)

                # 검색 결과를 컨텍스트에 추가하여 2차 추론 요청
                context.append({"role": "assistant", "content": content})
                context.append({
                    "role": "user", 
                    "content": f"""
[외부 데이터 수신 완료]
{search_result_text}

위 데이터를 바탕으로 최종 답변을 작성하라. 
**주의: 반드시 너의 성격 매트릭스와 '아이리스'로서의 페르소나를 유지하며, JSON 형식을 지켜라.**
"""
                })

                response_2nd = self.llm_requester.request(context=context)

                content_2nd = ""
                if isinstance(response_2nd, dict):
                    content_2nd = response_2nd.get('message', {}).get('content', "")
                elif isinstance(response_2nd, str):
                    content_2nd = str(response_2nd)

                # 최종 추론
                result = self._parse_llm_response(content_2nd)

        if result:
            # 사고 결과물 추출
            state_delta = result.get('state_delta', {})    # 이번 대화로 인한 심리 변화량
            new_memories = result.get('memories_to_save', []) # 새롭게 저장할 지식(Triplets)

            # STEP 5: 상태 업데이트 및 저장
            # 1. 감정 매트릭스 수치 갱신 (Clamping 포함)
            self.update_matrix(state_delta)
            
            # 2. 새로운 지식을 그래프 DB에 각인
            if new_memories:
                self.iris_memory.add_memory(new_memories, state_delta)

            return result

        return f"데이터 해석 실패:\n{response}"

    def set_enabled_web_search(self, enabled):
        self.support_web_search = enabled

    def set_serper_api_key(self, api_key):
        self.iris_search.set_serper_api_key(api_key)

    def set_decay_rate(self, decay_rate):
        self.iris_memory.set_decay_rate(decay_rate)

    def set_personality_matrix(self, personality_matrix):
        self.personality_matrix = personality_matrix

    def set_persona_context(self, persona_context):
        self.persona_context = persona_context

    def set_world_context(self, world_context):
        self.world_context = world_context

    def set_llm_requester(self, llm_requester):
        self.llm_requester = llm_requester

    def _parse_llm_response(self, text):
        """LLM 응답에서 JSON만 안전하게 추출"""
        try:
            # 정규표현식으로 ```json ... ``` 사이의 내용만 추출하거나 전체에서 JSON 검색
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return json.loads(text)
        except Exception as e:
            Logger.log("Parsing Error", f"Failed to parse JSON: {e}\n{text}")
            return None

    def update_matrix(self, delta):
        """매트릭스 수치 업데이트 및 경계값 고정(Clamping)"""
        for key, value in delta.items():
            if key in self.personality_matrix:
                # 급격한 변화 방지를 위해 변화폭 제한 (옵션)
                limited_delta = max(-0.3, min(0.3, value)) 
                new_val = round(self.personality_matrix[key] + limited_delta, 2)
                # 0.0 ~ 1.0 범위 강제
                self.personality_matrix[key] = max(0.0, min(1.0, new_val))
        
        Logger.log("Matrix Updated", self.personality_matrix)
    