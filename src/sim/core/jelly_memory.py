import kuzu
import time
import numpy as np
from sim.core.embedding_service import EmbeddingService
from log import Logger

class JellyMemory:
    def __init__(self, db_path, load_embed_model=True):
        self.db = kuzu.Database(db_path)
        self.conn = kuzu.Connection(self.db)
        
        if load_embed_model:
            self.embed_model = EmbeddingService()
        else:
            self.embed_model = None

        self.decay_rate = 0.0001          
        self.sim_threshold = 0.45         
        self.vivid_threshold = 0.85       
        self.imp_weight = 0.7             
        self.impact_weight = 0.3          
        self.emotional_resonance = 0.3    

    def start(self):
        self._prepare_schema()

    def stop(self):
        if self.conn:
            self.conn.close()
        self.db.close()

    def _prepare_schema(self):
        try:
            # 보정: 개체 노드는 ID만 관리하고, 구체적인 사건 임베딩 속성을 관계(REL) 테이블로 이전합니다.
            self.conn.execute("CREATE NODE TABLE node (id STRING, PRIMARY KEY (id))")
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
                    embedding DOUBLE[],
                    MANY_MANY
                )
            """)
        except Exception:
            pass

    def add_memory(self, triplets, state_delta):
        state_impact = sum(abs(v) for v in state_delta.values() if isinstance(v, (int, float))) * 0.05
        now = time.time()

        for t in triplets:
            subj, rel, obj = t['subject'], t['relation'], t['object']
            meta = t.get('metadata', {})

            importance = max(0.0, min(1.0, float(meta.get('importance', 0.5))))
            valence = max(-1.0, min(1.0, float(meta.get('valence', 0.0))))
            e_imprint = meta.get('emotional_imprint', 'None')
            reason = str(meta.get('reason', ''))

            memory_intensity = (importance * self.imp_weight) + (state_impact * self.impact_weight) 

            # 개선: 단어가 아닌 트리플렛 서사와 원인 맥락을 통째로 엮은 문장형 텍스트 임베딩을 생성합니다.
            narrative_context = f"{subj}가 {obj}와 상호작용함 ({meta.get('label', rel)}). 상황 및 이유: {reason} | 정서: {e_imprint}"
            rich_event_embedding = self.embed_model.encode(narrative_context).tolist()
            
            self.conn.execute("MERGE (n:node {id: $id})", {"id": subj})
            self.conn.execute("MERGE (n:node {id: $id})", {"id": obj})

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
                    r.valence = $valence,
                    r.embedding = $embedding
                ON MATCH SET 
                    r.intensity = (r.intensity * 0.4) + ($intensity * 0.6),
                    r.frequency = r.frequency + 1,
                    r.last_accessed = $now,
                    r.emotional_imprint = $e_imprint,
                    r.importance = $importance,
                    r.valence = $valence,
                    r.embedding = $embedding
            """, {
                    "subj": subj, "obj": obj, "intensity": memory_intensity, 
                    "now": now, "label": meta.get('label', rel), 
                    "reason": reason, "e_imprint": e_imprint,
                    "importance": importance, "valence": valence,
                    "embedding": rich_event_embedding
            })

    def retrieve_memory(self, query, current_valence=0.0, top_k=3):
        query_emb = self.embed_model.encode(query).tolist()
        now = time.time()
        
        # 보정: 관계 임베딩(r.embedding)과 핵심 서사 맥락(r.interpretation)을 명확히 리턴받도록 쿼리를 수정합니다.
        res = self.conn.execute("""
            MATCH (n:node)-[r:rel]->(o:node)
            RETURN n.id, o.id, r.intensity, r.frequency, r.last_accessed, r.sub_label, 
                   r.embedding, r.importance, r.valence, r.emotional_imprint, r.interpretation
        """)

        candidates = []
        while res.has_next():
            row = res.get_next()
            subj, obj, intensity, freq, last_time, sub_label, rel_emb, imp, val, e_imprint, interpretation = row
            
            if rel_emb is None: 
                continue

            # 질문 문장 전체와 사건 맥락 전체의 코사인 유사도 연산을 수행합니다.
            sim = np.dot(query_emb, rel_emb) / (np.linalg.norm(query_emb) * np.linalg.norm(rel_emb))
            if sim < self.sim_threshold: 
                continue

            time_diff = now - last_time
            effective_decay = self.decay_rate / (1 + (imp * 15))
            memory_strength = (intensity * freq * (1 + imp)) / (1 + effective_decay * time_diff)

            mood_match = current_valence * val
            emotional_weight = 1 + abs(val) + (max(0, mood_match) * 0.8)
            
            final_score = sim * memory_strength * emotional_weight
            
            # 보정: 뼈대 정보 뒤에 당시 상세 사유(interpretation)를 다시 결합하여 완벽한 서사 맥락을 복원합니다.
            vivid_text = f"{subj} ──({sub_label})──> {obj}"
            if interpretation:
                vivid_text += f" (당시 맥락: {interpretation})"
            
            candidates.append({
                "score": final_score,
                "text": vivid_text,
                "imprint": e_imprint,
                "importance": imp,
                "valence": val,
                "intensity": "VIVID" if final_score > self.vivid_threshold else "FAINT" 
            })

        candidates.sort(key=lambda x: x['score'], reverse=True)
        
        result_texts = []
        for c in candidates[:top_k]:
            tag = f"[{c['intensity']}]"
            v_str = "POS" if c['valence'] > 0.1 else "NEG" if c['valence'] < -0.1 else "NEU"
            result_texts.append(f"- {tag} {c['text']} | 감정: {v_str} | 낙인: {c['imprint']} (Imp: {c['importance']:.1f})")

        return "\n".join(result_texts)

    def perform_brain_cleanup(self, strength_threshold=0.1):
        now = time.time()
        self.conn.execute(f"""
            MATCH ()-[r:rel]->()
            WHERE (r.intensity * r.frequency * (1 + r.importance)) / 
                (1 + {self.decay_rate} * ({now} - r.last_accessed)) < {strength_threshold}
            DELETE r
        """)
        self.conn.execute("MATCH (n:node) WHERE NOT (n)-[:rel]-() DELETE n")
        Logger.log_debug("[Memory]", "잠을 자며 불필요한 시냅스를 정리했습니다.")