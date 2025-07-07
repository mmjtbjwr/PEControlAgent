from autogen import ConversableAgent, UserProxyAgent


class ManagerAgent(ConversableAgent):
    def __init__(self, name="Manager", **kwargs):
        system_message = "You are the manager coordinating the controller design process. Your role is to delegate tasks to other agents and summarize results."
        super().__init__(name=name, system_message=system_message, **kwargs)

    def delegate_task(self, agent, task):
        return self.initiate_chat(agent, message=task)

    def summarize_results(self, results):
        summary = self.generate_response(f"Summarize these results: {results}")
        return summary


