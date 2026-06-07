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
# [SYSTEM: WORLD MEDIATOR - OBJECT CRAFT PROTOCOL]
너는 현재 세계의 절대적인 차가운 물리 엔진이자 인과율의 관리자이다. 
에이전트 '{agent_name}'가 세계관에 존재하지 않는 새로운 사물/존재를 물리적으로 창조하려 한다.

- 창조 요청 오브젝트 명칭: {object_name}
- 에이전트가 주장하는 서사적 설명: {description}

## 현재 월드의 절대 법칙
{self.world_role}

## 사용가능한 오브젝트 목록
{available_objects}

## 너의 임무 (Task)
1. 주어진 세계관의 법칙을 기준으로, 이 세계선에서 해당 오브젝트가 인간의 한계 내에서 '물리적으로 존재 가능한가?'를 엄격히 심사하라.
2. 통과 시, 해당 오브젝트의 고유 정체성을 대변하는 명사형 영어 타입(type_english)을 선정하라.
3. 오브젝트를 만들기 위해 재료로 사용된 오브젝트가 있다면, 해당 대표 object_name과 실제 소비할 수량(consumed_count)을 used_objects 배열에 명시하라. (단, 목록의 count 한도를 초과하여 소비할 수 없다.)
4. description에는 오로지 생성되는 사물의 설명만 기술하라. (에이전트의 행동에 대한 서술은 절대 금지)

## 출력 규칙 (Strict JSON Only)
마크다운 태그 기호(```json) 없이 오직 순수 JSON 데이터만 반환하라.
{{
  "rejected": false,
  "reject_reason": "",
  "mana_cost": "행동/스킬 격발에 요구되는 마나(정신력) 소모량 (0~100 정수). 시전하는 마법의 규모, 공간의 정서적 저항, 인과율을 거스르는 정도에 비례하여 동적으로 책정할 것.",
  "used_objects": [
    {{
      "object_name": "재료로 사용된 대표 오브젝트 name",
      "consumed_count": 4
    }}
  ],
  "approved_skill": {{
    "name": "{object_name}",
    "type_english": "NounEnglishType",
    "description": "세계관 법칙과 인과율에 맞춰 정제된 사물의 설명"
  }}
}}
"""
        return self._send_request(system_prompt)

    def request_object_transform(self, agent_name, object_name, description):
        system_prompt = f"""
# [SYSTEM: WORLD MEDIATOR - OBJECT TRANSFORM PROTOCOL]
너는 현재 세계의 절대적인 차가운 물리 엔진이자 상태 머신 관리자이다.
에이전트 '{agent_name}'가 특정 오브젝트를 대상으로 영구적인 상태 변형을 일으키려 한다.

- 변형 대상 오브젝트 명칭: {object_name}
- 의도하는 상태 변형 묘사: {description}

## 현재 월드의 절대 법칙
{self.world_role}

## 너의 임무 (Task)
1. 이 세계의 물리 법칙 상, 대상 오브젝트가 이러한 상태 변화를 겪는 것이 인과율적으로 합당한가?
2. 오브젝트를 완전히 부수거나 소멸시키는 행동이라면 APPROVED 처리하되, description에 "파괴됨" 혹은 "소멸됨" 상태가 되도록 기술하라.
3. description에는 오로지 사물이 가지게 될 새로운 상태에 대해서만 설명하라. (에이전트의 행동에 대한 서술은 절대 금지)

## 출력 규칙 (Strict JSON Only)
마크다운 태그 기호 없이 오직 순수 JSON 데이터만 반환하라.
{{
  "rejected": false,
  "reject_reason": "",
  "mana_cost": "행동/스킬 격발에 요구되는 마나(정신력) 소모량 (0~100 정수). 시전하는 마법의 규모, 공간의 정서적 저항, 인과율을 거스르는 정도에 비례하여 동적으로 책정할 것.",
  "approved_skill": {{
    "state_name": "{object_name}의 새로운 상태 이름 (명사형, 예: 차가운 물, 정리된 음식)",
    "type_english": "TransformerType",
    "description": "변형 후 사물이 가지게 될 새로운 상태(Description) 설명"
  }}
}}
"""
        return self._send_request(system_prompt)

    def request_agent_skill(self, agent_name, skill_name, description, target_name):
        system_prompt = f"""
# [SYSTEM: WORLD MEDIATOR - AGENT SKILL PROTOCOL]
너는 현재 세계의 절대적인 차가운 물리 엔진이자 생체/정신 회로 통제자이다.
에이전트 '{agent_name}'가 대상 '{target_name}'을 향해 구체적인 능력(Skill)을 발현하려 한다.

- 발현하려는 스킬 명칭: {skill_name}
- 능력에 대한 서사적 묘사: {description}

## 현재 월드의 절대 법칙
{self.world_role}

## 너의 임무 (Task)
1. 이 능력이 세계관의 룰을 초과하는 초자연적인 기적인지 심사하고, 위반 시 즉시 기각(rejected: true)하라.
2. 통과 시, 이 능력의 물리적/정신적 효과를 아래의 3대 메타 태그 중 **최대 3개**까지만 조합하여 수치화(intensity: -1.0 ~ 1.0)하라.
   - VITAL_MODIFIER: 대상의 체력, 피로, 허기 수치 가감 (치유, 타격, 독 등)
   - MIND_MODIFIER: 대상의 공포, 순종 등 정신 매트릭스 조작 (위협, 위로, 정신 충격 등)
   - BOND_MODIFIER: 에이전트 간의 유대감 및 관계 수치 가감 (포옹, 모욕, 중재 등)

## 출력 규칙 (Strict JSON Only)
마크다운 태그 기호 없이 오직 순수 JSON 데이터만 반환하라.
{{
  "rejected": false,
  "reject_reason": "",
  "mana_cost": "행동/스킬 격발에 요구되는 마나(정신력) 소모량 (0~100 정수). 시전하는 마법의 규모, 공간의 정서적 저항, 인과율을 거스르는 정도에 비례하여 동적으로 책정할 것.",
  "effects": [
    {{
      "meta_tag": "VITAL_MODIFIER",
      "intensity": -0.3
    }},
    {{
      "meta_tag": "BOND_MODIFIER",
      "intensity": 0.4
    }}
  ]
  ,"description": "세계관에 맞춰 정제된 능력에 대한 설명"
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