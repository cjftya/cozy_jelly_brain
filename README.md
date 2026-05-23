# UPDATE HISTORY
Update: v6

# UNIVERSAL ORGANIC COGNITIVE ENGINE (CozyJelly Brain)

본 프로젝트는 주입된 페르소나를 생존 도구로 사용하는 유기적 자율 인지 지능 에이전트 시뮬레이션 프레임워크입니다. 에이전트는 외부 자극을 객관적으로 처리하지 않으며, 현재의 호르몬 상태(Matrix), 생체적 결핍(Desires), 그리고 성별 바이어스에 따라 세계를 주관적으로 왜곡(Refraction)하여 수용하고 자율적인 행동을 집행합니다.

---

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