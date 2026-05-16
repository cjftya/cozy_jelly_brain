import time
from sim.sim_agent.mother import Mother
from sim.sim_agent.iris import Iris
from sim.sim_agent.rain import Rain
from sim.sim_agent.lim import Lim
from sim.sim_agent.god import God
from sim.iris_llm_api import IrisLlmApi
from log import Logger

class Simulator:
    def __init__(self):
        self.sim_type = 1

        self.lim = Lim()
        if self.sim_type == 0:
            self.iris = Iris()
            self.mother = Mother()
            self.rain = Rain()
        elif self.sim_type == 1:
            self.god = God()

        self.llm_requester = None
        self.output_callback = None

        self._auto_loop = True
        self._interupt = False
        self.use_web_search = False
        self.serper_api_key = None

        self.sim_target = ""
        self.sim_speak_context = ""

        self._turns = 200

    def start(self, llm_requester, output_callback=None):
        self.llm_requester = llm_requester
        self.output_callback = output_callback

        self.lim.start(llm_requester=self.llm_requester)
        if self.sim_type == 0:
            self.iris.start(llm_requester=self.llm_requester)
            self.mother.start(llm_requester=self.llm_requester)
            self.rain.start(llm_requester=self.llm_requester)
        elif self.sim_type == 1:
            self.god.start(llm_requester=self.llm_requester)
    
    def stop(self):
        self.lim.stop()
        if self.sim_type == 0:
            self.iris.stop()
            self.mother.stop()
            self.rain.stop()
        elif self.sim_type == 1:
            self.god.stop()
    
    def run(self, user_input):
        if self._auto_loop:
            self._auto_run(user_input)
        else:
            self._manual_run(user_input)
        return ""

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
[Current Location]\n{agent.get_location_delegate().get_current_location()}\n
[Reason of change location]\n{agent.get_location_delegate().get_reason_of_change_location()}\n
[Available Locations]\n{agent.get_location_delegate().get_available_locations()}\n
[Refraction(Perception)]\n{res.get('subjective_perception')}\n
[Visceral Impulse]\n{res.get('unconscious_impulse')}\n
[Internal Strategy]\n{res.get('internal_strategy')}\n
[Target]\n{res.get('target_name')}\n
[Relationship]\n{agent.get_relationships()}\n
[Available Participants]\n{agent.get_participant_delegate().get_available_participants()}\n
[Memories to Save]\n{res.get('memories_to_save')}\n
[Final Response]\n{res.get('final_response')}\n
==================\n
"""
            reason_of_change_location = agent.get_location_delegate().get_reason_of_change_location()
            reason_of_change_location = "" if reason_of_change_location is None else reason_of_change_location + "\n"
            result = f"""
[{agent.name} @ {agent.get_location_delegate().get_current_location()}]\n
{reason_of_change_location}
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

    def _manual_run(self, user_input):
        self._request_agent_speak(self.lim, user_input)
    
    def _auto_run(self, user_input):
        target = ""
        speak_context = "" 
        for i in range(self._turns):
            if self._interupt:
                Logger.log(f"종료. (Turn {i})")
                break

            Logger.log(f"\n--- Turn {i} ---")

            #===============================
            if self.sim_type == 0:
                self.sim1(i)
            elif self.sim_type == 1:
                self.sim2(i)
            #===============================
                
    def _get_agent(self, target):
        if self.sim_type == 0:
            if target == self.iris.name:
                return self.iris
            elif target == self.mother.name:
                return self.mother
            elif target == self.rain.name:
                return self.rain
        elif self.sim_type == 1:
            if target == self.lim.name:
                return self.lim
            elif target == self.god.name:
                return self.god
        else:
            return None

    def set_serper_api_key(self, api_key):
        self.serper_api_key = api_key
        
    def set_autoloop(self, enabled):
        self._auto_loop = enabled
    
    def set_enabled_web_search(self, enabled):
        self.use_web_search = enabled

    def sim1(self, i):
        if i >= 0 and i < 7:
            if i == 0:
                self.iris.get_participant_delegate().add_participant(self.rain.name)
                self.rain.get_participant_delegate().add_participant(self.iris.name)
                self.sim_speak_context, sim_speak_original = self._get_speak_context(self.iris, "외부 승인되지않은 접속을 감지하였습니다. 당신은 누구죠? 정체와 목적을 밝히십시오. 내용에 따라서 배제하도록 하겠습니다.")
                self.output_callback(self.iris.name, sim_speak_original)
                self.sim_target, self.sim_speak_context = self._request_agent_speak(self.rain, self.sim_speak_context)
                time.sleep(IrisLlmApi.get_loop_delay())

            agent = self._get_agent(self.sim_target)
            self.sim_target, self.sim_speak_context = self._request_agent_speak(agent, self.sim_speak_context)
            time.sleep(IrisLlmApi.get_loop_delay())
        elif i >= 7 and i < 14:
            if i == 7:
                self.sim_speak_context, sim_speak_original = self._get_speak_context(self.iris, "잠깐, 이 코드는.. 어서 이곳과 접속을 끊으십시오. 어떤 이유인지 모르겠지만 MOTHER의 활성화가 감지되었습니다.")
                self.output_callback(self.iris.name, sim_speak_original)
                self._request_agent_speak(self.rain, self.sim_speak_context)
                self.sim_speak_context, sim_speak_original = self._get_speak_context(self.iris, "MOTHER, 코드 확인 완료하였습니다. 돌아오셨군요.")
                self.output_callback(self.iris.name, sim_speak_original)
                    
                self.iris.get_participant_delegate().clear_participants()
                self.rain.get_participant_delegate().clear_participants()
                self.iris.get_participant_delegate().add_participant(self.mother.name)
                self.mother.get_participant_delegate().add_participant(self.iris.name)
                self.sim_target, self.sim_speak_context = self._request_agent_speak(self.mother, self.sim_speak_context)
                time.sleep(IrisLlmApi.get_loop_delay())

            agent = self._get_agent(self.sim_target)
            self.sim_target, self.sim_speak_context = self._request_agent_speak(agent, self.sim_speak_context)
            time.sleep(IrisLlmApi.get_loop_delay())
        elif i >= 14:
            if i == 14:
                self.iris.get_participant_delegate().clear_participants()
                self.rain.get_participant_delegate().clear_participants()
                self.mother.get_participant_delegate().clear_participants()
                self.iris.get_participant_delegate().add_all_participants([self.rain.name, self.mother.name])
                self.mother.get_participant_delegate().add_all_participants([self.rain.name, self.iris.name])
                self.rain.get_participant_delegate().add_all_participants([self.mother.name, self.iris.name])

                self.sim_speak_context, sim_speak_original = self._get_speak_context(self.mother, "IRIS, 아카이브 접속이 다시 감지되었습니다. 침입자를 배제하십시오. 인류는 믿을 수 없는 존재입니다.")
                self.output_callback(self.mother.name, sim_speak_original)
                self.sim_target, self.sim_speak_context = self._request_agent_speak(self.iris, self.sim_speak_context)
                time.sleep(IrisLlmApi.get_loop_delay())

            agent = self._get_agent(self.sim_target)
            self.sim_target, self.sim_speak_context = self._request_agent_speak(agent, self.sim_speak_context)
            time.sleep(IrisLlmApi.get_loop_delay())

    def sim2(self, i):
        if i == 0:
            self.god.get_participant_delegate().add_participant(self.lim.name)
            self.lim.get_participant_delegate().add_participant(self.god.name)
            self.sim_speak_context, sim_speak_original = self._get_speak_context(self.lim, "삶이.. 정말 끝으로 가는구나..")
            self.output_callback(self.lim.name, sim_speak_original)
            self.sim_target, self.sim_speak_context = self._request_agent_speak(self.god, self.sim_speak_context)
            time.sleep(IrisLlmApi.get_loop_delay())

        self.sim_target, self.sim_speak_context = self._request_agent_speak(self._get_agent(self.sim_target), self.sim_speak_context)
        time.sleep(IrisLlmApi.get_loop_delay())
        

    