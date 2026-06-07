import threading

class EventType:
    BIOMETRICS_UPDATED = "biometrics_updated"
    WORLD_DETAIL_UPDATED = "world_detail_updated"
    AGENT_CHAT_LOG_APPENDED = "agent_chat_log_appended"
    WORLD_LOG_APPENDED = "world_log_appended"
    ASCII_MAP_UPDATED = "ascii_map_updated"
    SYSTEM_LOG_APPENDED = "system_log_appended"
    AGENT_POSITION_UPDATED = "agent_position_updated"
    WORLD_TICKED = "world_ticked"
    AGENT_THINKING_LOG_APPENDED = "agent_thinking_log_appended"
    AGENT_PERCEPTION_UPDATED = "agent_perception_updated"

class EventBus:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(EventBus, cls).__new__(cls)
                cls._instance._subscribers = {}
                cls._instance._subscribers_lock = threading.Lock()
        return cls._instance

    def subscribe(self, event_type, callback):
        with self._subscribers_lock:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            self._subscribers[event_type].append(callback)

    def unsubscribe(self, event_type, callback):
        with self._subscribers_lock:
            if event_type in self._subscribers:
                try:
                    self._subscribers[event_type].remove(callback)
                except ValueError:
                    pass

    def publish(self, event_type, *args, **kwargs):
        with self._subscribers_lock:
            callbacks = list(self._subscribers.get(event_type, []))
        for callback in callbacks:
            try:
                callback(*args, **kwargs)
            except Exception as e:
                import sys
                print(f"Error executing callback for event {event_type}: {e}", file=sys.stderr)
