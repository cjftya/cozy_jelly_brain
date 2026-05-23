from llm_requester import LLMRequester
from sim.simulate import Simulator

class Engine:
    def __init__(self):
        self.llm_requester = None
        self.model_name = None
        self.simulator = None

    def start(self, 
              refresh_biometrics=None,
              refresh_world_detail=None,
              append_agent_chat_log=None,
              append_world_log=None,
              refresh_ascii_map=None,
              append_system_log=None):
        if self.llm_requester is None:
            self.llm_requester = LLMRequester()
            self.llm_requester.start_engine(full=True)
        if self.simulator is None:
            self.simulator = Simulator()
            self.simulator.start(
                self.llm_requester,
                refresh_biometrics=refresh_biometrics,
                refresh_world_detail=refresh_world_detail,
                append_agent_chat_log=append_agent_chat_log,
                append_world_log=append_world_log,
                refresh_ascii_map=refresh_ascii_map,
                append_system_log=append_system_log
            )

    def load(self, api_key, serper_api_key, use_web_search, auto_play):
        if self.llm_requester:
            self.llm_requester.init_client()
            self.llm_requester.set_api_key(api_key)
        
        if self.simulator:
            self.simulator.set_serper_api_key(serper_api_key)
            self.simulator.set_enabled_web_search(use_web_search)
            self.simulator.set_autoloop(auto_play)

    def stop(self):
        if self.llm_requester:
            self.llm_requester.stop_engine(full=True)
            self.llm_requester = None
        if self.simulator:
            self.simulator.stop()
            self.simulator = None

    def run(self, model_name, prompt):
        self.model_name = model_name
        self.llm_requester.set_model_name(self.model_name)

        response = self.simulator.run(prompt)
        return response

    def get_model_list(self):
        if self.llm_requester:
            return self.llm_requester.get_installed_models()
        return []