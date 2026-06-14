import time
from sim.world.world_system_manager import WorldSystemManager
from log import Logger

class Simulator:
    def __init__(self):
        self.llm_requester = None
        
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

    def run(self, user_input=None):
        while True:
            if self._interupt:
                Logger.log(f"종료.")
                break

            #===============================
            self.world_system_manager.tick()
            #===============================
        return ""

    def set_serper_api_key(self, api_key):
        self.serper_api_key = api_key
        if self.world_system_manager:
            self.world_system_manager.set_serper_api_key(api_key)
        
    def set_enabled_web_search(self, enabled):
        self.use_web_search = enabled