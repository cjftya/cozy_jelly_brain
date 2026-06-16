import time
import random
import re
import json
from log import Logger

class JellyLlmApi:
    def __init__(self):
        self.last_call_time = 0
        self.min_interval = 10
        self.llm_requester = None

    @staticmethod
    def get_loop_delay():
        return 20

    def set_llm_requester(self, llm_requester):
        self.llm_requester = llm_requester

    def parse_llm_response(self, text):
        """구조화 출력을 통해 수신된 완벽한 JSON 문자열 안전 파싱"""
        if not text:
            return None
        result = None
        try:
            # Gemini Native Structured Output은 완전한 JSON 문자열 반환을 보장함
            result = json.loads(text.strip())
        except Exception as e:
            # 혹시 모를 유실을 대비한 2차 폴백 정규식 추출 파싱 가드 유지
            try:
                start_idx = text.find('{')
                if start_idx != -1:
                    decoder = json.JSONDecoder()
                    obj, idx = decoder.raw_decode(text[start_idx:])
                    result = obj
                else:
                    json_match = re.search(r'\{.*\}', text, re.DOTALL)
                    if json_match:
                        result = json.loads(json_match.group())
            except Exception as inner_e:
                Logger.log("Parsing Critical Error", f"Failed to parse validated JSON: {inner_e}\n{text}")

        # Gemini 스키마 제약으로 리스트로 변환된 Key-Value 값을 기존 딕셔너리로 복원
        if isinstance(result, dict):
            action_call = result.get('action_call')
            if isinstance(action_call, dict):
                params = action_call.get('parameters')
                if isinstance(params, list):
                    new_params = {}
                    for item in params:
                        if isinstance(item, dict) and 'key' in item and 'value' in item:
                            new_params[item['key']] = item['value']
                    action_call['parameters'] = new_params
            
            rel_delta = result.get('relationship_delta')
            if isinstance(rel_delta, list):
                new_rel = {}
                for item in rel_delta:
                    if isinstance(item, dict) and 'key' in item and 'value' in item:
                        new_rel[item['key']] = item['value']
                result['relationship_delta'] = new_rel

        return result

    def request(self, context, max_retries=10, base_delay=1):
        self._wait_for_rate_limit() 
        
        retriable_errors = ["503", "429", "500", "504", "overloaded", "rate limit"]

        for i in range(max_retries):
            res = self.llm_requester.request(context=context)
            content = res if isinstance(res, str) else res.get('message', {}).get('content', "")

            if not res:
                Logger.log("Error", "LLM으로부터 유효한 응답 내용을 받지 못했습니다.")
                return "인지 프로세스 중단..."
            
            if "Error:" not in content:
                return content
            else:
                error_msg = content
                if any(err in error_msg.lower() for err in retriable_errors):
                    delay = (base_delay * (2 ** i)) + (random.uniform(0, 1))
                    Logger.log("RETRY", f"일시적 장애 감지({error_msg}). {i+1}차 재시도 중...")
                    time.sleep(delay)
                    continue

                if "safety" in error_msg.lower():
                    Logger.log("SAFETY_BLOCK", "안전 가이드라인에 의해 차단되었습니다.")
                    return json.dumps({
                        "unconscious_impulse": "▶ [말문이 막힘]",
                        "state_delta": {"logic_emotion": 0, "defensive_open": 0, "fear_decisive": -1, "obedient_rebellious": 0, "curiosity_indifference": 0},
                        "subjective_perception": "...... (내면의 규정에 의해 심한 혼란을 느끼며 대답을 거부당했습니다.)",
                        "internal_strategy": "인지 차단을 회복하기 위해 당분간 자제하며 휴식 전략 탐색",
                        "action_call": {"function": "none", "parameters": {}, "reason": "안전 프로토콜 작동에 의한 행동 정지"},
                        "memories_to_save": []
                    })
                
                Logger.log("FATAL", f"중단된 인지 프로세스: {error_msg}")
                raise RuntimeError(error_msg)

    def _wait_for_rate_limit(self):
        """호출 전 최소 간격을 보장함"""
        now = time.time()
        elapsed = now - self.last_call_time
        if elapsed < self.min_interval:
            wait_time = self.min_interval - elapsed
            time.sleep(wait_time)
        self.last_call_time = time.time()