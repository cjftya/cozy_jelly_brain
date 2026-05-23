import time
from sim.world.world_system_manager import WorldSystemManager
from log import Logger

class Simulator:
    def __init__(self):

        self.llm_requester = None
        
        # UI API Callbacks
        self.refresh_biometrics = None
        self.refresh_world_detail = None
        self.append_agent_chat_log = None
        self.append_world_log = None
        self.refresh_ascii_map = None
        self.append_system_log = None

        self._auto_loop = True
        self._interupt = False
        self.use_web_search = False
        self.serper_api_key = None

        self.world_system_manager = WorldSystemManager()

    def start(self, llm_requester,
              refresh_biometrics=None,
              refresh_world_detail=None,
              append_agent_chat_log=None,
              append_world_log=None,
              refresh_ascii_map=None,
              append_system_log=None):
        self.llm_requester = llm_requester
        
        self.refresh_biometrics = refresh_biometrics
        self.refresh_world_detail = refresh_world_detail
        self.append_agent_chat_log = append_agent_chat_log
        self.append_world_log = append_world_log
        self.refresh_ascii_map = refresh_ascii_map
        self.append_system_log = append_system_log
        
        self.world_system_manager.start(self.llm_requester,
            refresh_biometrics=refresh_biometrics,
            refresh_world_detail=refresh_world_detail,
            append_agent_chat_log=append_agent_chat_log,
            append_world_log=append_world_log,
            refresh_ascii_map=refresh_ascii_map,
            append_system_log=append_system_log
        )

    def stop(self):
        self._interupt = True
        self.world_system_manager.stop()
        self.llm_requester = None
        
        self.refresh_biometrics = None
        self.refresh_world_detail = None
        self.append_agent_chat_log = None
        self.append_world_log = None
        self.refresh_ascii_map = None
        self.append_system_log = None

    def run(self, user_input):
        if self._auto_loop:
            self._auto_run(user_input)
        else:
            self._manual_run(user_input)
        return ""

    def _manual_run(self, user_input):
        pass
    
    def _auto_run(self, user_input):
        while True:
            if self._interupt:
                Logger.log(f"종료.")
                break

            #===============================
            self.world_system_manager.tick()
            #===============================

    def set_serper_api_key(self, api_key):
        self.serper_api_key = api_key
        
    def set_autoloop(self, enabled):
        self._auto_loop = enabled
    
    def set_enabled_web_search(self, enabled):
        self.use_web_search = enabled