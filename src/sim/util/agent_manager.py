class AgentManager:
    def __init__(self):
        self.agent_set = set()

    def add_agent(self, agent):
        self.agent_set.add(agent)

    def remove_agent(self, agent):
        self.agent_set.remove(agent)

    def get_agent_by_id(self, agent_id):
        for agent in self.agent_set:
            if agent.id == agent_id:
                return agent
        return None

    def get_agent_by_name(self, agent_name):
        for agent in self.agent_set:
            if agent.name == agent_name:
                return agent
        return None

    def get_agents(self):
        return list(self.agent_set)

    def clear_agents(self):
        self.agent_set.clear()