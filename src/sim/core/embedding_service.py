import os
import threading

from sentence_transformers import SentenceTransformer


class EmbeddingService:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(EmbeddingService, cls).__new__(cls)
                cls._instance._model = None
                cls._instance._model_lock = threading.Lock()
        return cls._instance

    def get_model(self):
        with self._model_lock:
            if self._model is None:
                # Resolve the absolute path to the models directory relative to this file
                # src/sim/core/embedding_service.py -> src/models/bge-m3
                base_dir = os.path.dirname(os.path.abspath(__file__))
                model_path = os.path.abspath(
                    os.path.join(base_dir, "..", "..", "models", "bge-m3")
                )

                # Fallback to relative path if absolute path is not found
                if not os.path.exists(model_path):
                    model_path = "./models/bge-m3"

                self._model = SentenceTransformer(model_path)
            return self._model

    def encode(self, text):
        return self.get_model().encode(text)
