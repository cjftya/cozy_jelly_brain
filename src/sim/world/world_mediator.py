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
통과된다면, 에이전트의 서사적 의도를 세계관의 5대 절대 법칙(Meta-Action Tags) 중 최대 3개로 분해하여 매핑하라. 하나의 동적 도구는 n개의 연속된 메타 액션으로 구성된다.

## 5대 절대 법칙 태그 (Meta-Action Tags)
1. VITAL_MODIFIER: 대상의 체력, 피로, 허기 수치 가감 (공격, 치유 등)
2. MIND_MODIFIER: 대상의 심리 및 공포/순종 매트릭스 굴절 (협박, 위로 등)
3. BOND_MODIFIER: 에이전트 간의 관계(호감도/신뢰) 수치 가감 (포옹, 모욕 등)
4. PROPERTY_TRANSFER: 물리적 아이템의 소유권 이전 (가져오기, 주기 등)
5. ITEM_CONSUME: 가방 또는 주위 사물 단일 소모 및 작동 (파괴, 먹기 등)

## 소유권 판정 규칙 (is_public)
- Private (false): 자가 치유, 개인적 감정 표현, 개인 가방 안의 사물 조합 등 특정 개인에게 귀속되는 행동.
- Public (true): 안개 걷기, 모닥불 피우기, 공용 뗏목 조립 등 누구나 시도할 수 있는 보편적이고 환경적인 기법.

## 출력 규칙 (Strict JSON Only)
마크다운 없이 오직 순수한 JSON 데이터만 출력하라.
* [규칙 1] parameters의 'applied_target'은 행동이 적용될 주 대상이다.
* [규칙 2] effects의 'consumed_objects'는 소모될 사물의 목록(object_id, consumed_count)이다.

{{
  "rejected": false,
  "reject_reason": "기각 시 이유 작성 (통과 시 비워둠)",
  "is_public": true 혹은 false,
  "parameters": {{ "applied_target": "적용될 대상 에이전트 이름 등 (없으면 null)" }},
  "effects": [
    {{
      "meta_tag": "5대 태그 중 1택",
      "consumed_object": "[{"object_id": "소비될 사물 ID", "consumed_count": "1"}]",
      "intensity": 0.1 ~ 1.0 (양수 또는 음수)
    }}
  ]
}}
"""
        return self._send_request(system_prompt)

    def request_craft_approval(self, agent_name, target_creation, materials):
        system_prompt = f"""
# [SYSTEM: CRAFTING MEDIATOR PROTOCOL]
너는 세계관의 물리 엔진이다. 에이전트 '{agent_name}'가 다음 재료를 모아 새로운 사물을 만들고자 한다.
- 만들 사물: {target_creation}

## 세계관 설정 (World Lore)
{self.world_role}

## 제출된 재료 (Materials)
{materials}

## 너의 임무 (Task)
제출된 재료만으로 '{target_creation}'을(를) 만드는 것이 물리적으로 합당한지 심사하라. (예: 통나무와 덩굴로 뗏목 만들기 = 가능 / 코코넛으로 총 만들기 = 불가능). 
합당하다면 approved: true로 하고, 에이전트가 제출한 재료 목록 중에서 실제로 소모될 재료들의 ID와 갯수만 확정하여 consumed_objects로 반환하라.
* 규칙: created_object_type는 생성하고자 할 '{target_creation}'의 타입이다. (0: 공간, 1: 객체, 2: 건물)

## 출력 규칙 (Strict JSON Only)
{{
  "approved": true 혹은 false,
  "reason": "승인 혹은 기각의 물리적 이유",
  "consumed_objects": [
    {{ "object_id": "소모될 재료 ID", "consumed_count": 1 }}
  ],
  "created_object_type": 
}}
"""
        return self._send_request(system_prompt)

    def _send_request(self, system_prompt):
        context = [{"role": "system", "content": system_prompt}, {"role": "user", "content": "위의 의도를 심사하여 JSON으로 출력하라."}]
        response = self.mediator_llm_api.request(context=context)
        content = response.get('message', {}).get('content', "") if isinstance(response, dict) else str(response)
        return self.mediator_llm_api.parse_llm_response(content)