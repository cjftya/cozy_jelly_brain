import queue
import threading
import time
from sim.core.jelly_llm_api import JellyLlmApi

class CognitiveWorker:
    def __init__(self, world_system_manager):
        self.world_system_manager = world_system_manager
        self.queue = queue.Queue()
        self.running = False
        self.thread = None

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        self.queue.put(None)
        if self.thread:
            self.thread.join(timeout=1.0)
            self.thread = None

    def queue_agent(self, agent):
        self.queue.put(agent)

    def _worker_loop(self):
        while self.running:
            try:
                agent = self.queue.get(timeout=0.5)
            except queue.Empty:
                continue

            if agent is None:
                break

            try:
                result = agent.think_tick()
                if result:
                    wvm = self.world_system_manager.world_view_manager
                    if hasattr(wvm, 'update_agent_light_log_view'):
                        agent_log = wvm.update_agent_light_log_view(agent, result)
                    else:
                        agent_log = wvm.update_agent_log_view(agent, result)
                    self.world_system_manager.log_agent_event(agent_log)
                    
                    time.sleep(JellyLlmApi.get_loop_delay())
            except Exception as e:
                self.world_system_manager.log_system_event(f"Error in cognitive worker for {agent.name}: {e}")
            finally:
                agent.is_thinking = False
                if hasattr(self.world_system_manager, 'log_agent_thinking_event'):
                    self.world_system_manager.log_agent_thinking_event(agent.name, None)
                self.queue.task_done()
