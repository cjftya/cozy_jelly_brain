import time
from sim.mother import Mother
from sim.iris import Iris
from sim.rain import Rain
from sim.iris_llm_api import IrisLlmApi
from log import Logger

class Simulator:
    def __init__(self):
        self.iris = Iris()
        self.mother = Mother()
        self.rain = Rain()

        self.llm_requester = None
        self.output_callback = None

        self._auto_loop = True
        self._interupt = False
        self.use_web_search = False
        self.serper_api_key = None

        self._turns = 200

    def start(self, llm_requester, output_callback=None):
        self.llm_requester = llm_requester
        self.output_callback = output_callback
        self.iris.start(llm_requester=self.llm_requester)
        self.mother.start(llm_requester=self.llm_requester)
        self.rain.start(llm_requester=self.llm_requester)
    
    def stop(self):
        self.iris.stop()
        self.mother.stop()
        self.rain.stop()
    
    def run(self, user_input):
        if self._auto_loop:
            self._auto_run(user_input)
        else:
            self._manual_run(user_input)
        return ""

    def _manual_run(self, user_input):
        return self.iris.run(user_input)

    def _get_speak_context(self, agnet, speak):
        return f"""
### [EXTERNAL_SIGNAL: {agnet.name}]
Identifier: {agnet.identifier}
Content: "{speak}"
--------------------------------
""", speak

    def _request_agent_speak(self, agent, speak):
        res = agent.run(speak)
        if self.output_callback:
            debug_result = f"""
[UserInput]\n{speak}\n
[Current Location]\n{agent.get_current_location()}\n
[Available Locations]\n{agent.get_available_locations()}\n
[Refraction(Perception)]\n{res.get('subjective_perception')}\n
[Visceral Impulse]\n{res.get('unconscious_impulse')}\n
[Internal Strategy]\n{res.get('internal_strategy')}\n
[Target]\n{res.get('target_name')}\n
[Relationship]\n{agent.get_relationships()}\n
[Available Participants]\n{agent.get_available_participants()}\n
[Memories to Save]\n{res.get('memories_to_save')}\n
[Final Response]\n{res.get('final_response')}\n
==================\n
"""
            result = f"""
[{agent.name} @ {agent.get_current_location()}]\n
({res.get('subjective_perception')})\n
{res.get('final_response')}\n
[To: {res.get('target_name')}]\n
==================\n
"""
            Logger.log_debug(f"{agent.name}", debug_result)
            self.output_callback(agent.name, result)

        talk = res.get('final_response', "...")
        target = res.get('target_name', "...")
        speak_context, _ = self._get_speak_context(agent, talk)
        return target, speak_context
    
    def _auto_run(self, user_input):
        target = ""
        speak_context = "" 
        for i in range(self._turns):
            if self._interupt:
                Logger.log(f"종료. (Turn {i})")
                break

            Logger.log(f"\n--- Turn {i} ---")

            #===============================

            if i >= 0 and i < 7:
                if i == 0:
                    self.iris.add_participant(self.rain.name)
                    self.rain.add_participant(self.iris.name)
                    speak_context, speak_original = self._get_speak_context(self.iris, "외부 승인되지않은 접속을 감지하였습니다. 당신은 누구죠? 정체와 목적을 밝히십시오. 내용에 따라서 배제하도록 하겠습니다.")
                    self.output_callback(self.iris.name, speak_original)
                    target, speak_context = self._request_agent_speak(self.rain, speak_context)
                    time.sleep(IrisLlmApi.get_loop_delay())

                agent = self._get_agent(target)
                target, speak_context = self._request_agent_speak(agent, speak_context)
                time.sleep(IrisLlmApi.get_loop_delay())
            elif i >= 7 and i < 14:
                if i == 7:
                    speak_context, speak_original = self._get_speak_context(self.iris, "잠깐, 이 코드는.. 어서 이곳과 접속을 끊으십시오. 어떤 이유인지 모르겠지만 MOTHER의 활성화가 감지되었습니다.")
                    self.output_callback(self.iris.name, speak_original)
                    self._request_agent_speak(self.rain, speak_context)
                    speak_context, speak_original = self._get_speak_context(self.iris, "MOTHER, 코드 확인 완료하였습니다. 돌아오셨군요.")
                    self.output_callback(self.iris.name, speak_original)
                    
                    self.iris.clear_participants()
                    self.rain.clear_participants()
                    self.iris.add_participant(self.mother.name)
                    self.mother.add_participant(self.iris.name)
                    target, speak_context = self._request_agent_speak(self.mother, speak_context)
                    time.sleep(IrisLlmApi.get_loop_delay())

                agent = self._get_agent(target)
                target, speak_context = self._request_agent_speak(agent, speak_context)
                time.sleep(IrisLlmApi.get_loop_delay())
            elif i >= 14:
                if i == 14:
                    self.iris.clear_participants()
                    self.rain.clear_participants()
                    self.mother.clear_participants()
                    self.iris.add_all_participants([self.rain.name, self.mother.name])
                    self.mother.add_all_participants([self.rain.name, self.iris.name])
                    self.rain.add_all_participants([self.mother.name, self.iris.name])

                    speak_context, speak_original = self._get_speak_context(self.mother, "IRIS, 아카이브 접속이 다시 감지되었습니다. 침입자를 배제하십시오. 인류는 믿을 수 없는 존재입니다.")
                    self.output_callback(self.mother.name, speak_original)
                    target, speak_context = self._request_agent_speak(self.iris, speak_context)
                    time.sleep(IrisLlmApi.get_loop_delay())

                agent = self._get_agent(target)
                target, speak_context = self._request_agent_speak(agent, speak_context)
                time.sleep(IrisLlmApi.get_loop_delay())
                
    def _get_agent(self, target):
        if target == self.iris.name:
            return self.iris
        elif target == self.mother.name:
            return self.mother
        elif target == self.rain.name:
            return self.rain
        else:
            return None

    def set_serper_api_key(self, api_key):
        self.serper_api_key = api_key
        
    def set_autoloop(self, enabled):
        self._auto_loop = enabled
    
    def set_enabled_web_search(self, enabled):
        self.use_web_search = enabled

    