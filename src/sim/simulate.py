import time
from sim.world.world_system_manager import WorldSystemManager
from log import Logger

class Simulator:
    def __init__(self, support_pygame=False):
        self.support_pygame = support_pygame
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

    def start(self, llm_requester):
        self.llm_requester = llm_requester
        
        self.world_system_manager.start(self.llm_requester)
        self.world_system_manager.set_serper_api_key(self.serper_api_key)

    def stop(self):
        self._interupt = True
        self.world_system_manager.stop()
        self.llm_requester = None

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
        
    def set_enabled_web_search(self, enabled):
        self.use_web_search = enabled