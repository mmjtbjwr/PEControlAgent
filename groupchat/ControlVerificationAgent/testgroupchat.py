import json
from autogen import ConversableAgent, GroupChat, GroupChatManager, UserProxyAgent
from model_config_tool import ModelConfigTool
from objective_tool import ObjectiveTool

# 创建工具实例
model_config_tool = ModelConfigTool()
objective_tool = ObjectiveTool()

# 定义全局llm_config
llm_config = {
    "config_list": [
        {
            "model": "gpt-4",
            "api_key": "sk-yO3lbzc5glqovBFLC21e1143366244C6AaC408Ad76Ca7155",
            "base_url": "https://hk.xty.app/v1"
        }
    ]
}

# 创建Manager Agent
def manager_response(self, messages, sender, config):
    return False, """Design a Boost converter controller with the following requirements:
    Maintain a Mean Absolute Error (MAE) below 2.
    The parameters of the Boost converter are as follows:
    Resistance (R) = 15Ω.
    Inductance (L) = 0.001H.
    Capacitance (C) = 0.0006F.
    The input voltage is 80V.
    The output voltage is 160V.
    ModelDesignAgent, please configure a suitable model for this design."""

manager_agent = ConversableAgent(
    name="ManagerAgent",
    system_message="You are a manager overseeing the design of a Boost converter controller. Your task 1 is broadcasting design requirements. Your task 2 is to instruct ModelDesignAgent to configure a suitable model. Your task 3 is to instruct ObjectiveAgent to define control objectives and constraints. Do not add any additional information or commentary.",
    llm_config=llm_config
)
manager_agent.register_reply(
    lambda message: True,
    manager_response
)

# 创建Model Design Agent
def model_design_response(self, messages, sender, config):
    requirements = {
        "resistance": 15,
        "inductance": 0.001,
        "capacitance": 0.0006,
        "input_voltage": 80,
        "output_voltage": 160
    }
    
    model_id, model_info = model_config_tool.find_model(requirements)
    
    if model_id and model_info:
        return True, f"模型已配置完成。模型ID: {model_id}, 位置: {model_info['address']}"
    else:
        return True, "无法配置满足要求的模型。"

model_design_agent = ConversableAgent(
    name="ModelDesignAgent",
    system_message="You are an agent responsible for configuring appropriate models for controller design. Your task is to report whether a suitable model has been configured, providing only the model ID and address if configured, or stating that no model could be configured. Do not provide any additional information or commentary.",
    llm_config=llm_config
)
model_design_agent.register_reply(
    lambda message: True,
    model_design_response
)

# 创建Objective Agent
def objective_response(self, messages, sender, config):
    objectives = objective_tool.get_control_objectives()
    return True, f"Control objective: {objectives['control_objective']}. Constraints: {', '.join(objectives['constraints'])}."

objective_agent = ConversableAgent(
    name="ObjectiveAgent",
    system_message="You are responsible for defining control objectives and constraints based on design requirements. Your task is to provide the control objectives and constraints. Do not provide any additional information or commentary.",
    llm_config=llm_config
)
objective_agent.register_reply(
    lambda message: True,
    objective_response
)

# 创建人类代理
human = UserProxyAgent(
    name="Human",
    system_message="You are a human overseeing the Boost converter controller design process. Your role is to initiate the design request and observe the process.",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
    code_execution_config={"use_docker": False}
)

# 创建GroupChat
groupchat = GroupChat(
    agents=[human, manager_agent, model_design_agent, objective_agent],
    messages=[],
    max_round=4
)

# 创建GroupChatManager
manager_chat = GroupChatManager(groupchat=groupchat, llm_config=llm_config)

# 运行群聊
if __name__ == "__main__":
    initial_message = """Design a Boost converter controller with the following requirements:
    Maintain a Mean Absolute Error (MAE) below 2.
    The parameters of the Boost converter are as follows:
    Resistance (R) = 15Ω.
    Inductance (L) = 0.001H.
    Capacitance (C) = 0.0006F.
    The input voltage is 80V.
    The output voltage is 160V."""

    # 使用人类代理启动对话
    chat_result = human.initiate_chat(manager_chat, message=initial_message)
    print(chat_result)