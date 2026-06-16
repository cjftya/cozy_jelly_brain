from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class StateDelta(BaseModel):
    logic_emotion: int = Field(..., description="이성/감성 수치 변화량 (-2 ~ 2 범위의 정수)")
    defensive_open: int = Field(..., description="경계/개방 수치 변화량 (-2 ~ 2 범위의 정수)")
    fear_decisive: int = Field(..., description="공포/결단 수치 변화량 (-2 ~ 2 범위의 정수)")
    obedient_rebellious: int = Field(..., description="순응/반항 수치 변화량 (-2 ~ 2 범위의 정수)")
    curiosity_indifference: int = Field(..., description="호기심/무관심 수치 변화량 (-2 ~ 2 범위의 정수)")

class KeyValueParam(BaseModel):
    key: str = Field(..., description="매개변수 키 이름 (도구 사양의 매개변수 명칭)")
    value: str = Field(..., description="매개변수 값")

class ActionCall(BaseModel):
    function: str = Field(..., description="선택한 도구의 정확한 영문 함수 이름 (예: move_to, take, build_raft, rest 등)")
    parameters: List[KeyValueParam] = Field(default_factory=list, description="도구 매뉴얼 사양에 일치하는 파라미터 Key-Value 리스트")
    reason: str = Field(..., description="새로운 호르몬 상태와 유기체 내면 전략에 부합하는 도구 실행의 명확한 인지적 근거")

class MemoryMetadata(BaseModel):
    label: str = Field(..., description="기억 시냅스 구조의 서사적 핵심 요약 라벨명 (무조건 한국어)")
    importance: float = Field(..., description="사건의 주관적 중요도 판정 수치 (0.0 ~ 1.0)")
    valence: float = Field(..., description="사건의 감정 정서가 판정 수치 (-1.0: 극단적 부정/비장함 ~ 1.0: 극단적 긍정/희망)")
    emotional_imprint: str = Field(..., description="에이전트 영혼에 새겨진 정서적 낙인 단어 (무조건 한국어, 예: 안도감, 공포, 헌신의 결의)")
    reason: Optional[str] = Field(default="", description="당시 사건이 발생한 구체적인 내면적 맥락 또는 사유")

class MemoryTriplet(BaseModel):
    subject: str = Field(..., description="기억 구조의 주체 엔티티 명칭 (무조건 한국어, 예: 나, TOM, 아스트리 레이아)")
    relation: str = Field(..., description="주체와 객체를 잇는 핵심 관계 서술어 (무조건 한국어)")
    object: str = Field(..., description="기억 구조의 객체 엔티티 명칭 (무조건 한국어, 예: 단단한 통나무, 제인의 야자잎 침대)")
    metadata: MemoryMetadata

class RelationshipDeltaItem(BaseModel):
    key: str = Field(..., description="대상 에이전트 이름 (무조건 영어, 예: TOM, JANE)")
    value: int = Field(..., description="호감도 변동 가중치 (-2 ~ 2 범위의 정수)")

class OrganicCognitiveResponse(BaseModel):
    unconscious_impulse: str = Field(..., description="유기체의 인지 루프 심부에서 분출된 날것의 본능 파편 기술 (예: ▶ [굶주림] ▶ [돌파])")
    state_delta: StateDelta
    relationship_delta: List[RelationshipDeltaItem] = Field(default_factory=list, description="주변 타인 에이전트 이름과 실시간 호감도 변동 가중치 리스트")
    subjective_perception: str = Field(..., description="변동된 호르몬 매트릭스가 실시간 반영되어 주관적으로 기만/왜곡 수용된 주변 환경 기술문 (페르소나 스타일 철저 적용)")
    internal_strategy: str = Field(..., description="왜곡된 인지 상태를 기반으로 유기체가 생존/목적 달성을 위해 수립한 단독 행동 및 대화 전략")
    action_call: ActionCall
    memories_to_save: List[MemoryTriplet] = Field(default_factory=list, description="Kuzu 그래프 데이터베이스에 영구 각인할 기억 시냅스 트리플렛 구조체 배열")