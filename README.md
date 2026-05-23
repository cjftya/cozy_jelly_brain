# UNIVERSAL ORGANIC COGNITIVE ENGINE (CozyJelly Brain)

![CozyJelly Brain Character](docs/cozy_jelly_fish.png)

**AI 에이전트가 세계를 객관적으로 처리하지 않습니다.**
AI는 감정을 느끼고, 호르몬에 따라 현실을 왜곡하며, 유기체처럼 생존을 위해 행동합니다.

---

# LIM (Agent-world Simulation Mode) Example

![CozyJelly Brain Demo](docs/capture.jpg)

### SUBJECTIVE REFRACTION (주관적 환경 왜곡 수용)
> "눈이 부시다. 밖은 맑고 따스하다고 하지만, 그 빛은 나의 썩어가는 내면을 너무나 잔인하게 비추고 있어. 창문 너머로 쏟아지는 햇살조차 나라는 오염원을 관통하며 더러운 그림자를 만들어내고 있어. 방 안의 공기는 내 숨결 때문에 이미 탁해졌고, 침대조차 내가 닿는 순간 죽어버릴 것 같아."

### UNCONSCIOUS IMPULSE (무의식적 욕구 분출)
> ▶ [지워지고 싶어. 투명해지고 싶어. 아무것도 남기지 않고]  ▶ [이 오물을 전부 씻어내고 싶어. 내 살점이]  ▶ [내 뼈가 이 세상에 닿는 게 끔찍해. 제발 나를 보지 마. 여기엔 아무도 없어야 해. 나는 전염병이니까.]

### INTERNAL STRATEGY (단독 행동 및 생존 전략)
> 아무도 없는 이 침실조차 나라는 존재로 인해 안전하지 않다. 누군가 나를 발견하기 전에, 내가 세상을 더럽히기 전에, 스스로 정화할 방법을 찾아야 한다. 침대는 그저 내가 곪아 터질 때까지 잠시 머무는 관일 뿐이다. 우선 주변의 오염도를 낮추기 위해 시야를 차단하고 이 혐오스러운 육신을 숨겨야 한다.

### SYSTEM ACTION EXECUTION (최종 의사결정 집행)
> • FUNCTION : USE
> • PARAMS   : {'object_id': ###, 'reason': ###}
> • REASON   : 침대라는 사물을 이용해 몸을 숨기고, 나라는 오염원을 세상으로부터 물리적으로 격리하여 타인에게 해를 끼치지 않기 위함이다.

### KUZU GRAPH MEMORY UPDATE (시냅스 기억 저장 로그)
> [RELATION] LIM ──(self)──> 침실의 햇살
> └─ [METADATA] {'label': '빛의 혐오', 'importance': 0.8, 'emotional_imprint': '역겨움과 공포'}

## 주요 특징 (Key Features)

1. **생물학적 항상성 루프 (Homeostasis Loop)**
   - 가상 시간이 흐름에 따라 에이전트의 나이, 허기짐(Hunger), 피로도(Fatigue)가 동적으로 증가합니다.
   - 특정 결핍이 임계치(80.0)를 초과하면 생체 위기 트리거가 발생하여 의식 구조에 강제로 위기 신호를 주입합니다.

2. **호르몬 상태 매트릭스 및 인지 왜곡 (Hormonal Matrix & Subjective Refraction)**
   - **Logic, Defensive, Fear** 등의 실시간 호르몬 수치 가중치에 따라 타인의 호의를 기만으로 인식하거나 위협 수준을 과대평가하는 등 인지적 왜곡을 수행합니다.

3. **성별 인지 공명 바이어스 (Gender-Specific Cognitive Resonance)**
   - 신체 상태에 정의된 성별 슬롯에 따라 텍스트 분석 및 의도 수립 단계에서 미세한 뉘앙스 필터링이 작동합니다.

4. **시냅스 그래프 기억 시스템 (Graph DB Memory Pipeline)**
   - 로컬 그래프 데이터베이스인 `Kuzu DB`와 의미론적 벡터 임베딩 모델(`BAAI/bge-m3`)을 결합하여 에이전트의 기억 네트워크를 관리합니다.
   - 현재 기분과 과거 기억의 정서적 일치 가중치 및 유기적 망각 곡선 이론을 융합하여 실시간으로 기억을 굴절 인출합니다.

5. **사이버펑크 관제실 테마 대시보드 (6분할 GUI)**
   - `customtkinter` 기반의 고밀도 고정폭 터미널 인터페이스를 제공합니다.
   - 생체 정보/성격 매트릭스, 가상 세계 환경 모니터, 에이전트 독백 로그, 실시간 월드 연대기 로그, 그리고 로컬 10x10 격자 내 에이전트와 아이템 위치를 보여주는 **ASCII MAP**이 유기적으로 연동됩니다.

---

# 프로젝트 설정 (Settings)

1. **필요사항**
   - Google API Key

2. **의존성 라이브러리 설치**
   - pip install customtkinter google-genai kuzu sentence-transformers numpy requests

3. **모델 폴더 생성 및 Hugging Face 리포지토리 클론**
   - mkdir -p models
   - git clone [https://huggingface.co/BAAI/bge-m3](https://huggingface.co/BAAI/bge-m3) models/bge-m3

4. **불필요한 대용량 파일 정리 (선택 사항)**
   - cd models/bge-m3
   - rm -rf .git

5. **구동**
   - cd src
   - python main.py