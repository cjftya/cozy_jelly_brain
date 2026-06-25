import random
import time
from typing import Any, Optional

import kuzu
import numpy as np

from log import Logger
from sim.core.embedding_service import EmbeddingService


class JellyMemory:
    embed_model: Optional[EmbeddingService]

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
            # 개체 노드(인물, 장소, 사물 아이디 등)
            self.conn.execute("CREATE NODE TABLE node (id STRING, PRIMARY KEY (id))")

            # 에피소드 중심 노드 스펙 신설 (메타데이터 및 고차원 서사 구조 속성 통합 바인딩)
            self.conn.execute("""
                CREATE NODE TABLE episode (
                    id STRING,
                    timestamp DOUBLE,
                    intensity DOUBLE,
                    sub_label STRING,
                    interpretation STRING,
                    emotional_imprint STRING,
                    importance DOUBLE,
                    valence DOUBLE,
                    embedding DOUBLE[],
                    PRIMARY KEY (id)
                )
            """)

            # 유기적 연결 관계 테이블 생성
            self.conn.execute(
                "CREATE REL TABLE triggered (FROM node TO episode, MANY_MANY)"
            )
            self.conn.execute(
                "CREATE REL TABLE target_object (FROM episode TO node, MANY_MANY)"
            )
        except Exception:
            pass

    def add_memory(self, triplets, state_delta):
        state_impact = (
            sum(abs(v) for v in state_delta.values() if isinstance(v, (int, float)))
            * 0.05
        )
        now = time.time()

        for i, t in enumerate(triplets):
            subj, rel, obj = t["subject"], t["relation"], t["object"]
            meta = t.get("metadata", {})

            importance = max(0.0, min(1.0, float(meta.get("importance", 0.5))))
            valence = max(-1.0, min(1.0, float(meta.get("valence", 0.0))))
            e_imprint = meta.get("emotional_imprint", "None")
            reason = str(meta.get("reason", ""))

            memory_intensity = (importance * self.imp_weight) + (
                state_impact * self.impact_weight
            )

            narrative_context = f"{subj}가 {obj}와 상호작용함 ({meta.get('label', rel)}). 상황 및 이유: {reason} | 정서: {e_imprint}"
            if self.embed_model is not None:
                rich_event_embedding = self.embed_model.encode(narrative_context).tolist()
            else:
                rich_event_embedding = [0.0] * 1024

            # 1. 엔티티 노드 무결성 유지
            self.conn.execute("MERGE (n:node {id: $id})", {"id": subj})
            self.conn.execute("MERGE (n:node {id: $id})", {"id": obj})

            # 2. 고유 에피소드 시냅스 스냅샷 노드 생성
            ep_id = f"EP_{int(now)}_{i}_{random.randint(1000, 9999)}"
            self.conn.execute(
                """
                CREATE (e:episode {
                    id: $ep_id,
                    timestamp: $now,
                    intensity: $intensity,
                    sub_label: $label,
                    interpretation: $reason,
                    emotional_imprint: $e_imprint,
                    importance: $importance,
                    valence: $valence,
                    embedding: $embedding
                })
            """,
                {
                    "ep_id": ep_id,
                    "now": now,
                    "intensity": memory_intensity,
                    "label": meta.get("label", rel),
                    "reason": reason,
                    "e_imprint": e_imprint,
                    "importance": importance,
                    "valence": valence,
                    "embedding": rich_event_embedding,
                },
            )

            # 3. 주체 및 객체 연쇄 관계 구조 매핑
            self.conn.execute(
                "MATCH (n:node {id: $subj}), (e:episode {id: $ep_id}) CREATE (n)-[:triggered]->(e)",
                {"subj": subj, "ep_id": ep_id},
            )
            self.conn.execute(
                "MATCH (e:episode {id: $ep_id}), (o:node {id: $obj}) CREATE (e)-[:target_object]->(o)",
                {"obj": obj, "ep_id": ep_id},
            )

    def retrieve_memory(self, agent_name, query, current_valence=0.0, top_k=3):
        if self.embed_model is None:
            return []
        query_emb = self.embed_model.encode(query).tolist()
        now = time.time()
        time_cutoff = now - (86400 * 30)

        # 에피소드 스키마 전용 패스 탐색 Cypher 패턴 개정 (에이전트별 DB가 격리되어 있으므로 노드 필터링 불필요)
        res: Any = self.conn.execute(
            """
            MATCH (n:node)-[r1:triggered]->(e:episode)-[r2:target_object]->(o:node)
            WHERE e.timestamp > $time_cutoff OR e.importance >= 0.2
            RETURN n.id, o.id, e.intensity, e.timestamp, e.sub_label, 
                   e.embedding, e.importance, e.valence, e.emotional_imprint, e.interpretation
        """,
            {"time_cutoff": time_cutoff},
        )

        candidates = []
        while res.has_next():
            row = res.get_next()
            (
                subj,
                obj,
                raw_intensity,
                raw_last_time,
                sub_label,
                rel_emb,
                raw_imp,
                raw_val,
                e_imprint,
                interpretation,
            ) = row

            intensity = float(raw_intensity) if raw_intensity is not None else 0.0
            last_time = float(raw_last_time) if raw_last_time is not None else 0.0
            imp = float(raw_imp) if raw_imp is not None else 0.0
            val = float(raw_val) if raw_val is not None else 0.0

            if rel_emb is None:
                continue

            sim = np.dot(query_emb, rel_emb) / (
                np.linalg.norm(query_emb) * np.linalg.norm(rel_emb)
            )
            if sim < self.sim_threshold:
                continue

            time_diff = now - last_time
            effective_decay = self.decay_rate / (1 + (imp * 15))

            # 에피소드는 고유 단일 스냅샷이므로 빈도(frequency) 가중치를 배제하고 시간 감쇄식으로 정밀화
            memory_strength = (intensity * (1 + imp)) / (
                1 + effective_decay * time_diff
            )

            mood_match = current_valence * val
            emotional_weight = 1 + abs(val) + (max(0, mood_match) * 0.8)

            final_score = sim * memory_strength * emotional_weight

            vivid_text = f"{subj} ──({sub_label})──> {obj}"
            if interpretation:
                vivid_text += f" (당시 맥락: {interpretation})"

            candidates.append(
                {
                    "score": final_score,
                    "text": vivid_text,
                    "imprint": e_imprint,
                    "importance": imp,
                    "valence": val,
                    "intensity": (
                        "VIVID" if final_score > self.vivid_threshold else "FAINT"
                    ),
                }
            )

        candidates.sort(key=lambda x: x["score"], reverse=True)

        result_texts = []
        for c in candidates[:top_k]:
            tag = f"[{c['intensity']}]"
            v_str = (
                "POS" if c["valence"] > 0.1 else "NEG" if c["valence"] < -0.1 else "NEU"
            )
            result_texts.append(
                f"- {tag} {c['text']} | 감정: {v_str} | 낙인: {c['imprint']} (Imp: {c['importance']:.1f})"
            )

        return "\n".join(result_texts) if result_texts else "연관된 기억 없음"

    def perform_brain_cleanup(self, strength_threshold=0.1):
        now = time.time()
        # 에피소드 스키마 전용 연쇄 삭제 클린업 쿼리 보정
        self.conn.execute(f"""
            MATCH (n:node)-[r1:triggered]->(e:episode)-[r2:target_object]->(o:node)
            WHERE (e.intensity * (1 + e.importance)) / (1 + {self.decay_rate} * ({now} - e.timestamp)) < {strength_threshold}
            DELETE r1, r2, e
        """)
        self.conn.execute(
            "MATCH (n:node) WHERE NOT (n)-[:triggered]-() AND NOT ()-[:target_object]->(n) DELETE n"
        )
        Logger.log_debug("[Memory]", "잠을 자며 불필요한 시냅스를 정리했습니다.")
