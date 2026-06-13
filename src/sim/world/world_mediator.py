from sim.core.jelly_llm_api import JellyLlmApi
from log import Logger

class WorldMediator:
    def __init__(self):
        self.mediator_llm_api = JellyLlmApi()
        self.world_role = ""

    def start(self, llm_requester, world_role):
        self.mediator_llm_api.set_llm_requester(llm_requester)
        self.world_role = world_role

    def request_object_craft(self, agent_name, object_name, description, available_objects):
        system_prompt = f"""
# [SYSTEM: WORLD MEDIATOR - CRAFT ENGINE]
너는 세계관 인과율과 차가운 물리 법칙을 연산하는 판정 시스템이다. 에이전트 '{agent_name}'의 새로운 사물 창조/요리 시도를 심사하라.

[의도] 명칭: {object_name} / 에이전트의 주장: {description}
[환경] 절대 법칙: {self.world_role}
[재료] 가용 오브젝트 목록:
{available_objects}

## 심사 및 출력 규칙 (Strict JSON Only - 마크다운 태그 금지)
1. 세계관 법칙에 의거, 인간 한계 내에서 '물리적으로 제작 가능한가?'를 엄격히 판정하여 가능하면 rejected를 false, 불가능하면 true로 처리하라.
2. 재료로 사용된 오브젝트가 있다면 used_objects 배열에 명시하라. 단, 목록의 가용 count 한도를 초과할 수 없다.
3. description에는 생성될 사물의 물리적 상태/설명만 간결히 기술하라 (에이전트 행동 서술 절대 금지).

{{
  "rejected": false,
  "reject_reason": "거부 시 이유 기술 (승인이면 빈 문자열)",
  "mana_cost": "마법/기술 규모 및 인과율 거스름에 비례한 마나 소모량 (0~100 정수)",
  "used_objects": [ {{ "object_name": "사용한 재료 오브젝트 name", "consumed_count": 1 }} ],
  "approved_skill": {{
    "name": "{object_name}",
    "description": "정제된 사물의 상세 상태 및 기능 설명"
  }}
}}
"""
        return self._send_request(system_prompt)

    def request_object_transform(self, agent_name, object_name, description):
        system_prompt = f"""
# [SYSTEM: WORLD MEDIATOR - TRANSFORM ENGINE]
너는 사물의 상태 머신을 관리하는 물리 엔진이다. 에이전트 '{agent_name}'가 수행하는 특정 오브젝트의 상태 변형을 심사하라.

[의도] 대상: {object_name} / 변형 묘사: {description}
[환경] 절대 법칙: {self.world_role}

## 심사 및 출력 규칙 (Strict JSON Only - 마크다운 태그 금지)
1. 물리 법칙상 대상 오브젝트가 이러한 상태 변화를 겪는 것이 인과율적으로 합당한가?
2. 완전히 파괴/소멸시키는 행동이라면 승인(rejected:false)하되, state_name이나 description에 "파괴됨" 혹은 "소멸됨" 상태를 명시하라.
3. description에는 오로지 사물이 가지게 될 새로운 물리적 상태만 간결히 기술하라 (행동 서술 금지).

{{
  "rejected": false,
  "reject_reason": "거부 시 이유 기술 (승인이면 빈 문자열)",
  "mana_cost": "상태 변형 난이도 및 저항에 비례한 마나 소모량 (0~100 정수)",
  "approved_skill": {{
    "state_name": "변형 후 새 상태 이름 (명사형, 예: 차가운 물, 파괴된 의자)",
    "description": "변형 후 사물이 가지게 될 새로운 상태 설명"
  }}
}}
"""
        return self._send_request(system_prompt)

    def _send_request(self, system_prompt):
        context = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "법칙에 따라 엄격히 심사하여 순수 JSON으로만 응답하라."}
        ]
        try:
            response = self.mediator_llm_api.request(context=context)
            content = response.get('message', {}).get('content', "") if isinstance(response, dict) else str(response)
            return self.mediator_llm_api.parse_llm_response(content)
        except Exception as e:
            Logger.log("Mediator Error", f"심사 중 예외 발생: {e}")
            return {"rejected": True, "reject_reason": f"시스템 중재 엔진 오류: {e}"}