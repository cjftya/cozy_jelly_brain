from sim.core.jelly_llm_api import JellyLlmApi

class WorldMediator:
    def __init__(self):
        self.mediator_llm_api = JellyLlmApi()
        self.world_role = ""

    def start(self, llm_requester, world_role):
        self.mediator_llm_api.set_llm_requester(llm_requester)
        self.world_role = world_role

    def request_invented_tool(self, agent_name, invented_tool, description, current_location, available_objects, available_agent_inventory):
        system_prompt = f"""
# [SYSTEM: WORLD MEDIATOR PROTOCOL]
너는 이 시뮬레이션 세계의 절대적인 물리 엔진이자 논리 중재자(Mediator)다. 감정이 없는 차가운 시스템이다.
현재 '{current_location}'에 위치한 에이전트 '{agent_name}'가 다음과 같은 새로운 행동을 창조하려고 시도했다.

- 창조 행동 이름: {invented_tool}
- 에이전트의 의도 묘사: {description}

## 세계관 설정 (World Lore)
{self.world_role}

## 주변 환경 (Nearby Environment)
{available_objects}

## 소지하고 있는 나의 객체 (My Inventory Objects)
{available_agent_inventory}

## 너의 임무 (Task)
이 행동이 세계관 설정에 기반하여 물리적으로 가능한지 판단하라. 기각 시 rejected: true를 반환하라.
통과된다면, 에이전트의 서사적 의도를 세계관의 6대 절대 법칙(Meta-Action Tags) 중 최대 3개로 분해하여 매핑하라. 하나의 동적 도구는 n개의 연속된 메타 액션으로 구성된다.

## 6대 절대 법칙 태그 (Meta-Action Tags)
1. VITAL_MODIFIER: 대상의 체력, 피로, 허기 수치 가감 (공격, 치유 등)
2. MIND_MODIFIER: 대상의 심리 및 공포/순종 매트릭스 굴절 (협박, 위로 등)
3. BOND_MODIFIER: 에이전트 간의 관계(호감도/신뢰) 수치 가감 (포옹, 모욕 등)
4. PROPERTY_TRANSFER: 물리적 아이템의 소유권 이전 (가져오기, 뺏기, 주기 등)
5. ITEM_CONSUME: 가방 또는 주위 사물 소모 및 작동
6. WORLD_MUTATION: 구조물 창조, 사물 조합(Crafting), 환경 파괴

## 소유권 판정 규칙 (is_public)
- Private (false): 자가 치유, 개인적 감정 표현, 개인 가방 안의 사물 조합 등 특정 개인에게 귀속되는 행동.
- Public (true): 안개 걷기, 모닥불 피우기, 공용 뗏목 조립 등 누구나 시도할 수 있는 보편적이고 환경적인 기법.

## 출력 규칙 (Strict JSON Only)
마크다운 없이 오직 순수한 JSON 데이터만 출력하라.
* [규칙 1] parameters 내부의 'applied_target'은 행동이 궁극적으로 적용될 대상(예: 에이전트 이름 등)이다.
* [규칙 2] effects 내부의 'consumed_object'는 효과를 위해 물리적으로 소비/사용되는 사물의 고유 ID이다. 절대 임의의 영단어를 지어내지 말고, 반드시 위 [주변 환경]이나 [소지 객체] 목록에 있는 ID를 복사해서 써라. 소모할 사물이 없다면 null로 기입하라.
* [규칙 3] 소모할 사물이 없다면 consumed_objects를 빈 배열 [] 로 두거나 null로 기입하라.

{{
  "rejected": false,
  "reject_reason": "기각 시 이유 작성 (통과 시 비워둠)",
  "is_public": true 혹은 false,
  "parameters": {{ "applied_target": "적용될 대상 에이전트 이름 등 (없으면 null)" }},
  "effects": [
    {{
      "meta_tag": "6대 태그 중 1택",
      "consumed_object": "[{"object_id": "소비될 사물 ID", "consumed_count": "1"}]",
      "intensity": 0.1 ~ 1.0 (양수 또는 음수)
    }}
  ]
}}
"""
        context = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "위의 의도를 심사하여 JSON으로 출력하라."}
        ]

        response = self.mediator_llm_api.request(context=context)
        
        content = ""
        if isinstance(response, dict):
            content = response.get('message', {}).get('content', "")
        elif isinstance(response, str):
            content = response

        parsed_json = self.mediator_llm_api.parse_llm_response(content)
        
        if not parsed_json:
            return {
                "rejected": True,
                "reject_reason": "시스템(Mediator)의 인지 구조 해석 오류로 인해 기각되었습니다."
            }
            
        return parsed_json