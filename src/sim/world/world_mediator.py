from sim.core.jelly_llm_api import JellyLlmApi

class WorldMediator:
    def __init__(self):
        self.mediator_llm_api = JellyLlmApi()
        self.world_role = ""

    def start(self, llm_requester, world_role):
        self.mediator_llm_api.set_llm_requester(llm_requester)
        self.world_role = world_role

    def request_new_skill(self, agent_name, invented_tool, skill_type, description, current_location, available_objects, available_agent_inventory):
        system_prompt = ""
        return self._send_request(system_prompt)

    def request_craft_object(self, agent_name, target_creation, materials):
        system_prompt = ""
        return self._send_request(system_prompt)

    def request_transform_object(self, agent_name, target_object, target_tool, materials):
        system_prompt = ""
        return self._send_request(system_prompt)

    def _send_request(self, system_prompt):
        context = [{"role": "system", "content": system_prompt}, {"role": "user", "content": "위의 의도를 심사하여 JSON으로 출력하라."}]
        response = self.mediator_llm_api.request(context=context)
        content = response.get('message', {}).get('content', "") if isinstance(response, dict) else str(response)
        return self.mediator_llm_api.parse_llm_response(content)