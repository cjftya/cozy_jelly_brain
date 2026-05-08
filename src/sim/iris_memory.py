import kuzu
import time
import numpy as np
from sentence_transformers import SentenceTransformer
from log import Logger

class IrisMemory:
    def __init__(self, db_path="iris_brain_db", load_embed_model=True):
        # 그래프 데이터베이스 및 연결 초기화
        self.db = kuzu.Database(db_path)
        self.conn = kuzu.Connection(self.db)
        
        # 의미론적 검색을 위한 로컬 임베딩 모델 로드 (BGE-M3)
        if load_embed_model:
            self.embed_model = SentenceTransformer("./models/bge-m3") 
        else:
            self.embed_model = None

        # --- 유기적 인지 매개변수 (Organic Parameters) ---
        self.decay_rate = 0.0001          # 기본 망각 속도
        self.sim_threshold = 0.45         # 유사도 임계값 (노이즈 필터링)
        self.vivid_threshold = 0.85       # [VIVID] 판정 기준 점수
        self.imp_weight = 0.7             # 주관적 중요도 반영 비중
        self.impact_weight = 0.3          # 시스템적 충격량(Matrix 변화량) 반영 비중

    def start(self):
        self._prepare_schema()

    def stop(self):
        if self.conn:
            self.conn.close()
        self.db.close()

    def _prepare_schema(self):
        try:
            # 스키마에 emotional_imprint 필드 추가 (기존 interpretation 활용 가능하나 명시적 분리 권장)
            self.conn.execute("CREATE NODE TABLE node (id STRING, embedding DOUBLE[], PRIMARY KEY (id))")
            self.conn.execute("""
                CREATE REL TABLE rel (
                    FROM node TO node, 
                    intensity DOUBLE,
                    last_accessed DOUBLE,
                    frequency INT64,
                    sub_label STRING,
                    interpretation STRING,
                    emotional_imprint STRING,
                    importance DOUBLE,
                    valence DOUBLE,
                    MANY_MANY
                )
            """)
        except Exception:
            pass

    def add_memory(self, triplets, state_delta):
        """새로운 대화 파편을 뇌(DB)에 새깁니다."""
        # 충격량 계산 (절대값 합산)
        state_impact = sum(abs(v) for v in state_delta.values() if isinstance(v, (int, float)))
        now = time.time()

        for t in triplets:
            subj, rel, obj = t['subject'], t['relation'], t['object']
            meta = t.get('metadata', {})

            importance = float(meta.get('importance', 0.5))
            valence = float(meta.get('valence', 0.0))
            e_imprint = meta.get('emotional_imprint', 'None') # 정서적 낙인 추출

            # 2. 각인 강도(Intensity) 결정
            # 공식: $Intensity = (Importance \times 0.7) + (Impact \times 0.3)$
            memory_intensity = (importance * self.imp_weight) + (state_impact * self.impact_weight)
            
            # 임베딩 생성
            subj_emb = self.embed_model.encode(subj).tolist()
            obj_emb = self.embed_model.encode(obj).tolist()
            
            # 3. 노드 MERGE (개체 등록)
            self.conn.execute(
                "MERGE (n:node {id: $id}) SET n.embedding = $emb", 
                {"id": subj, "emb": subj_emb}
            )
            self.conn.execute(
                "MERGE (n:node {id: $id}) SET n.embedding = $emb", 
                {"id": obj, "emb": obj_emb}
            )

            # 4. 시냅스 연결 (관계 저장 및 업데이트)
            self.conn.execute(f"""
                MATCH (s:node {{id: $subj}}), (o:node {{id: $obj}})
                MERGE (s)-[r:rel]->(o)
                ON CREATE SET 
                    r.intensity = $intensity,
                    r.frequency = 1,
                    r.last_accessed = $now,
                    r.sub_label = $label,
                    r.interpretation = $reason,
                    r.emotional_imprint = $e_imprint,
                    r.importance = $importance,
                    r.valence = $valence
                ON MATCH SET 
                    r.intensity = (r.intensity * 0.4) + ($intensity * 0.6),
                    r.frequency = r.frequency + 1,
                    r.last_accessed = $now,
                    r.emotional_imprint = $e_imprint,
                    r.importance = $importance,
                    r.valence = $valence
            """, {
                    "subj": subj, "obj": obj, "intensity": memory_intensity, 
                    "now": now, "label": meta.get('label', rel), 
                    "reason": str(meta.get('reason', '')),
                    "e_imprint": e_imprint,
                    "importance": importance, "valence": valence
            })

    def retrieve_memory(self, query, current_valence=0.0, top_k=3):
        """현재의 감정 상태와 굴절률에 따라 기억을 인출합니다."""
        query_emb = self.embed_model.encode(query).tolist()
        now = time.time()
        
        # 전체 관계 조회 (소규모 DB 기준, 대규모 시 Vector Index 활용 권장)
        res = self.conn.execute("""
            MATCH (n:node)-[r:rel]->(o:node)
            RETURN n.id, o.id, r.intensity, r.frequency, r.last_accessed, r.sub_label, 
                   n.embedding, r.importance, r.valence, r.emotional_imprint
        """)

        candidates = []
        while res.has_next():
            row = res.get_next()
            subj, obj, intensity, freq, last_time, sub_label, node_emb, imp, val, e_imprint = row
            
            # 1. 의미적 유사도 (Cosine Similarity)
            sim = np.dot(query_emb, node_emb) / (np.linalg.norm(query_emb) * np.linalg.norm(node_emb))
            if sim < self.sim_threshold: continue

            # 2. 유기적 망각 곡선 적용
            # 중요도가 높을수록(imp) 망각 저항력이 기하급수적으로 커짐
            time_diff = now - last_time
            effective_decay = self.decay_rate / (1 + (imp * 15))
            memory_strength = (intensity * freq * (1 + imp)) / (1 + effective_decay * time_diff)

            # 3. 감정 일치 효과 (Mood Congruence)
            # 현재 기분과 기억의 정서가 일치할 때 회상 확률 증폭
            mood_match = current_valence * val
            emotional_weight = 1 + abs(val) + (max(0, mood_match) * 0.8)
            
            # 최종 회상 점수 계산
            final_score = sim * memory_strength * emotional_weight
            
            candidates.append({
                "score": final_score,
                "text": f"{subj} --({sub_label})--> {obj}",
                "imprint": e_imprint,
                "importance": imp,
                "valence": val,
                "intensity": "VIVID" if final_score > self.vivid_threshold else "FAINT" 
            })

        # 점수 순 정렬
        candidates.sort(key=lambda x: x['score'], reverse=True)
        
        result_texts = []
        for c in candidates[:top_k]:
            tag = f"[{c['intensity']}]"
            v_str = "POS" if c['valence'] > 0.1 else "NEG" if c['valence'] < -0.1 else "NEU"
            # 정서적 낙인을 텍스트에 포함하여 프롬프트에 전달
            result_texts.append(f"- {tag} {c['text']} | 감정: {v_str} | 낙인: {c['imprint']} (Imp: {c['importance']:.1f})")

        return "\n".join(result_texts)

    def perform_brain_cleanup(self, strength_threshold=0.1):
        """[GC] 흐릿해진 기억(시냅스)을 정리하여 인지 효율을 높입니다."""
        now = time.time()
        
        # 망각 곡선에 의해 극도로 약해진 관계 삭제
        self.conn.execute(f"""
            MATCH ()-[r:rel]->()
            WHERE (r.intensity * r.frequency * (1 + r.importance)) / 
                (1 + {self.decay_rate} * ({now} - r.last_accessed)) < {strength_threshold}
            DELETE r
        """)
        
        # 고립된 노드(기억 파편) 정리
        self.conn.execute("MATCH (n:node) WHERE NOT (n)-[:rel]-() DELETE n")
        Logger.log_debug("[Memory]", "잠을 자며 불필요한 시냅스를 정리했습니다.")

    def get_visual_data(self):
        """도트 게임 등 시각화 엔진을 위한 그래프 데이터 추출"""
        try:
            nodes_res = self.conn.execute("MATCH (n:node) RETURN n.id") 
            nodes = [{"id": str(row[0])} for row in nodes_res]

            links_res = self.conn.execute("""
                MATCH (s:node)-[r:rel]->(o:node) 
                RETURN s.id, o.id, r.intensity, r.sub_label, r.importance, r.valence, r.emotional_imprint
            """)
            links = []
            while links_res.has_next():
                s, o, inten, label, imp, val, emp = links_res.get_next()
                links.append({
                    "source": str(s), "target": str(o), "intensity": float(inten),
                    "label": str(label), "importance": float(imp), 
                    "valence": float(val), "emotional_imprint": str(emp)
                })
            return {"nodes": nodes, "links": links}
        except Exception as e:
            return {"nodes": [], "links": []}

    def inspect_iris_brain(self):
        """뇌 내부 상태 정밀 진단 로그"""
        try:
            Logger.log("\n" + "═"*100)
            Logger.log("🧠 [Project Iris] Neural Links Diagnostic")
            Logger.log("═"*100)
            
            res = self.conn.execute("""
                MATCH (s:node)-[r:rel]->(o:node) 
                RETURN s.id, r.sub_label, o.id, r.importance, r.valence, r.emotional_imprint, r.interpretation
            """)
            
            Logger.log(f"{'Neural Link (S -> Rel -> O)':<50} | {'Imp':<4} | {'Val':<4} | {'Imprint':<15} | {'Interpretation'}")
            Logger.log("─"*100)

            while res.has_next():
                s, l, o, imp, val, emp, reason = res.get_next()
                link = f"{s} → {l} → {o}"
                Logger.log(f"{link:<50} | {imp:<4.1f} | {val:<4.1f} | {str(emp):<15} | {reason}")
            Logger.log("═"*100)
        except Exception as e:
            Logger.log("Error", f"Brain inspection failed: {e}")