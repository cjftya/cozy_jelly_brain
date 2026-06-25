from typing import Any, Optional, List, Dict


class BaseClient:
    def start_engine(self) -> None:
        pass

    def stop_engine(self) -> None:
        pass

    def get_installed_models(self) -> List[str]:
        return []

    def set_model_name(self, model_name: str) -> None:
        pass

    def set_api_key(self, api_key: str) -> None:
        pass

    def get_context_size(self) -> int:
        return 0

    def request(self, context: Any, model: Optional[str] = None, options: Optional[Dict[str, Any]] = None, chunk_callback: Any = None) -> Any:
        pass

    def get_options(self) -> Dict[str, Any]:
        return {}
