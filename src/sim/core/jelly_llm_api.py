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
        """LLM 응답에서 JSON만 안전하게 추출"""
        try:
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return json.loads(text)
        except Exception as e:
            Logger.log("Parsing Error", f"Failed to parse JSON: {e}\n{text}")
            return None

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
                return res
            else:
                error_msg = content
                if any(err in error_msg.lower() for err in retriable_errors):
                    delay = (base_delay * (2 ** i)) + (random.uniform(0, 1))
                    Logger.log("RETRY", f"일시적 장애 감지({error_msg}). {i+1}차 재시도 중...")
                    time.sleep(delay)
                    continue

                if "safety" in error_msg.lower():
                    Logger.log("SAFETY_BLOCK", "안전 가이드라인에 의해 차단되었습니다.")
                    return {"final_response": "...... (규정에 의해 말문이 막혔습니다.)", "state_delta": {}}
                Logger.log("FATAL", f"중단된 인지 프로세스: {error_msg}")
                raise res

    def _wait_for_rate_limit(self):
        """호출 전 최소 간격을 보장함"""
        now = time.time()
        elapsed = now - self.last_call_time
        if elapsed < self.min_interval:
            wait_time = self.min_interval - elapsed
            time.sleep(wait_time)
        self.last_call_time = time.time()