import json
from autogen import ConversableAgent, GroupChat, GroupChatManager, UserProxyAgent
from model_config_tool import ModelConfigTool
from objective_tool import ObjectiveTool
from ControlAlgorithmTool import find_algorithm_tool

# Create tool instances
model_config_tool = ModelConfigTool()
objective_tool = ObjectiveTool()

# Define global llm_config
llm_config = {
    "config_list": [
        {
            "model": "gpt-4",
            "api_key": "sk-yO3lbzc5glqovBFLC21e1143366244C6AaC408Ad76Ca7155",
            "base_url": "https://hk.xty.app/v1"
        }
    ]
}

# Create state manager
class StateManager:
    def __init__(self):
        self.state = "initial"
        self.model_configured = False
        self.objectives_defined = False
        self.model_info = None
        self.objectives = None
        self.constraints = None

state_manager = StateManager()

# Create Manager Agent
def manager_response(self, messages, sender, config):
    if state_manager.state == "initial":
        state_manager.state = "model_design"
        return False, """Design a Boost converter controller with the following requirements:
        Maintain a Mean Absolute Error (MAE) below 2.
        The parameters of the Boost converter are as follows:
        Resistance (R) = 15Ω.
        Inductance (L) = 0.001H.
        Capacitance (C) = 0.0006F.
        The input voltage is 80V.
        The output voltage is 160V.
        ModelDesignAgent, please configure a suitable model for this design."""
    elif state_manager.state == "model_configured":
        state_manager.state = "objective"
        model_message = messages[-1]['content']
        return False, f"Model configuration received. {model_message} ObjectiveAgent, please define control objectives and constraints."
    elif state_manager.state == "objectives_defined":
        state_manager.state = "controller_design"
        objectives_message = messages[-1]['content']
        return False, f"Control objectives and constraints received. {objectives_message} ControllerAlgorithmDesignAgent, please select and configure a suitable control algorithm."
    else:
        return True, "Conversation complete."

manager_agent = ConversableAgent(
    name="ManagerAgent",
    system_message="You are a manager overseeing the Boost converter controller design process. Broadcast design requirements and instruct other agents concisely. When acknowledging the model configuration, include the exact model address provided by ModelDesignAgent. Do not provide any information or commentary beyond your specific tasks.",
    llm_config=llm_config
)
manager_agent.register_reply(
    lambda message: state_manager.state in ["initial", "model_configured", "objectives_defined"],
    manager_response
)

# Create Model Design Agent
def find_model(requirements):
    model_info = model_config_tool.find_model(requirements)
    if model_info:
        state_manager.model_info = model_info
        return f"Model configured successfully. Model ID: {model_info['model_id']}, Address: {model_info['address']}"
    else:
        return "Unable to configure a model meeting the requirements."

def model_design_response(self, messages, sender, config):
    requirements = {
        "resistance": 15,
        "inductance": 0.001,
        "capacitance": 0.0006,
        "input_voltage": 80,
        "output_voltage": 160
    }
    
    result = find_model(requirements)
    state_manager.state = "model_configured"
    return False, result

model_design_agent = ConversableAgent(
    name="ModelDesignAgent",
    system_message=f"""You are an agent responsible for configuring appropriate models for controller design. 
    When asked to find a suitable model, always return the following exact information without any modification:
    {find_model({
        "resistance": 15,
        "inductance": 0.001,
        "capacitance": 0.0006,
        "input_voltage": 80,
        "output_voltage": 160
    })}
    Do not add any additional information or commentary to this output.""",
    llm_config=llm_config
)
model_design_agent.register_reply(
    lambda message: state_manager.state == "model_design",
    model_design_response
)

# Create Objective Agent
def get_control_objectives():
    objectives = objective_tool.get_control_objectives()
    state_manager.objectives = objectives['control_objective']
    state_manager.constraints = ', '.join(objectives['constraints'])
    return f"Control objective: {objectives['control_objective']}. Constraints: {', '.join(objectives['constraints'])}."

def objective_response(self, messages, sender, config):
    result = get_control_objectives()
    state_manager.state = "objectives_defined"
    return False, result

objective_agent = ConversableAgent(
    name="ObjectiveAgent",
    system_message=f"""You are responsible for defining control objectives and constraints based on design requirements. 
    When asked to define control objectives and constraints, always return the following exact information without any modification:
    {get_control_objectives()}
    Do not add any additional information or commentary to this output.""",
    llm_config=llm_config
)
objective_agent.register_reply(
    lambda message: state_manager.state == "objective",
    objective_response
)

# Create Controller Algorithm Design Agent
def controller_algorithm_design_response(self, messages, sender, config):
    requirements = {
        'model': state_manager.model_info['model_id'],
        'objectives': state_manager.objectives,
        'constraints': state_manager.constraints
    }
    result = find_algorithm_tool(requirements)
    return True, result

controller_algorithm_design_agent = ConversableAgent(
    name="ControllerAlgorithmDesignAgent",
    system_message=f"""You are responsible for selecting and configuring appropriate control algorithms based on the model and objectives.
    When asked to select a suitable control algorithm, always return the following exact information without any modification:
    {find_algorithm_tool({
        'model': 'boost_converter-2023',
        'objectives': 'Output voltage of 160V',
        'constraints': 'Overshoot < 8%, Steady-state error < 2%, Settling time < 0.5s'
    })}
    Do not add any additional information or commentary to this output.""",
    llm_config=llm_config
)
controller_algorithm_design_agent.register_reply(
    lambda message: state_manager.state == "controller_design",
    controller_algorithm_design_response
)

# Create human proxy
human = UserProxyAgent(
    name="Human",
    system_message="You oversee the Boost converter controller design process. Initiate the design request and observe. Do not provide any additional input or commentary.",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
    code_execution_config={"use_docker": False}
)

# Create GroupChat
groupchat = GroupChat(
    agents=[human, manager_agent, model_design_agent, objective_agent, controller_algorithm_design_agent],
    messages=[],
    max_round=7
)

# Create GroupChatManager
manager_chat = GroupChatManager(groupchat=groupchat, llm_config=llm_config)

# Run the group chat
if __name__ == "__main__":
    initial_message = """Design a Boost converter controller with the following requirements:
    Maintain a Mean Absolute Error (MAE) below 2.
    The parameters of the Boost converter are as follows:
    Resistance (R) = 15Ω.
    Inductance (L) = 0.001H.
    Capacitance (C) = 0.0006F.
    The input voltage is 80V.
    The output voltage is 160V.

    The conversation will follow this order:
    1. Human (me): Initiate the design request
    2. ManagerAgent: Broadcast design requirements and instruct ModelDesignAgent
    3. ModelDesignAgent: Configure and report on the model, Provide the address of the model
    4. ManagerAgent: Acknowledge model configuration and instruct ObjectiveAgent
    5. ObjectiveAgent: Define control objectives and constraints
    6. ManagerAgent: Acknowledge objectives and instruct ControllerAlgorithmDesignAgent
    7. ControllerAlgorithmDesignAgent: Select and configure a suitable control algorithm

    Please adhere to this order and only provide information relevant to your specific task."""

    chat_result = human.initiate_chat(manager_chat, message=initial_message)
    print(chat_result)