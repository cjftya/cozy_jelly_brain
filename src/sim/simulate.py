import time
from sim.iris_llm_api import IrisLlmApi
from sim.world.world_context_manager import WorldContextManager
from log import Logger

class Simulator:
    def __init__(self):

        self.llm_requester = None
        self.output_callback = None

        self._auto_loop = True
        self._interupt = False
        self.use_web_search = False
        self.serper_api_key = None

        self.world_context_manager = WorldContextManager()

        self._turns = 200

    def start(self, llm_requester, output_callback=None):
        self.llm_requester = llm_requester
        self.output_callback = output_callback
        self.world_context_manager.start(self.llm_requester, self.output_callback)

    def stop(self):
        self.world_context_manager.stop()
        self.llm_requester = None
        self.output_callback = None

    def run(self, user_input):
        if self._auto_loop:
            self._auto_run(user_input)
        else:
            self._manual_run(user_input)
        return ""

    def _manual_run(self, user_input):
        pass
    
    def _auto_run(self, user_input):
        for i in range(self._turns):
            if self._interupt:
                Logger.log(f"종료. (Turn {i})")
                break

            Logger.log(f"\n--- Turn {i} ---")

            #===============================
            self.world_context_manager.tick()

            time.sleep(IrisLlmApi.get_loop_delay())
            #===============================

    def set_serper_api_key(self, api_key):
        self.serper_api_key = api_key
        
    def set_autoloop(self, enabled):
        self._auto_loop = enabled
    
    def set_enabled_web_search(self, enabled):
        self.use_web_search = enabled