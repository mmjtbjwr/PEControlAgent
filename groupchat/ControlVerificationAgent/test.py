import autogen
from typing import Dict, List
from pydantic import BaseModel
from ControlTool import ControlParams, ControllerFactory
from OptimizationTool import OptimizationFactory
from SimulationTool import SimulationParams
from EvaluateTool import EvaluateParams

# 配置
config_list = [
   {"model": "qwen2-72b-instruct", "api_key": "sk-4869c2bfac6e4fe292d4496929b968ef",
                "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1"
}]

class VerificationInput(BaseModel):
    fmu_path: str
    control_algorithm_name: str
    control_algorithm_params: Dict[str, float]
    optimization_algorithm_name: str
    optimization_algorithm_params: Dict[str, float]
    simulation_params: SimulationParams
    evaluate_params: EvaluateParams

# 创建代理
manager = autogen.AssistantAgent(
    name="ManagerAgent",
    system_message="You are the manager of the control system optimization process. Your role is to coordinate the activities of other agents by assigning tasks and evaluating the final results. Start by assigning tasks to each agent in order.",
    llm_config={"config_list": config_list}
)

objective = autogen.AssistantAgent(
    name="ObjectiveAgent",
    system_message="You are responsible for setting reasonable control performance requirements. Provide specific, measurable objectives for the control system when asked by the ManagerAgent.",
    llm_config={"config_list": config_list}
)

control_algorithm = autogen.AssistantAgent(
    name="ControlAlgorithmAgent",
    system_message="You are an expert in control algorithms. Your task is to select and configure appropriate control tools based on the given requirements when asked by the ManagerAgent.",
    llm_config={"config_list": config_list}
)

control_parameter = autogen.AssistantAgent(
    name="ControlParameterAgent",
    system_message="You are specialized in optimization algorithms. Your role is to choose and configure suitable optimization tools for tuning control parameters when asked by the ManagerAgent.",
    llm_config={"config_list": config_list}
)

verification = autogen.AssistantAgent(
    name="ControlVerificationAgent",
    system_message="You are responsible for simulating the control system with optimized parameters and verifying if it meets the performance requirements when asked by the ManagerAgent.",
    llm_config={"config_list": config_list}
)

human = autogen.UserProxyAgent(
    name="Human",
    system_message="You are a human user overseeing the control system optimization process.",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
    code_execution_config={"use_docker": False}
)

# 创建 GroupChat
groupchat = autogen.GroupChat(
    agents=[human, manager, objective, control_algorithm, control_parameter, verification],
    messages=[],
    max_round=50
)

# 创建 GroupChatManager
manager_chat = autogen.GroupChatManager(groupchat=groupchat, llm_config={"config_list": config_list})

# 注册函数
def verify_controller_wrapper(input_dict: Dict) -> Dict:
    # 这里实现验证控制器的逻辑，类似于您之前的实现
    # 为简化示例，这里只返回一个模拟的结果
    return {
        "mae": 0.3,
        "overshoot": 5.2,
        "settling_time": 0.5,
        "rise_time": 0.2,
        "robustness_score": 0.8,
        "anti_interference_score": 0.7,
        "best_pid_params": {
            "voltage_k": 1.2,
            "voltage_Ti": 0.1,
            "current_k": 0.8,
            "current_Ti": 0.05
        }
    }

autogen.register_function(
    verify_controller_wrapper,
    caller=verification,
    executor=human,
    name="verify_controller",
    description="Verify and validate the performance of a power electronic device controller using FMU simulation and optimization.",
)

# 启动对话
initial_message = """
Let's optimize a control system for a power electronic device. ManagerAgent, please start by assigning tasks to each agent in the following order:
1. Assign ObjectiveAgent to set specific performance requirements for the control system.
2. Assign ControlAlgorithmAgent to choose an appropriate control algorithm based on the requirements.
3. Assign ControlParameterAgent to select an optimization algorithm for tuning the control parameters.
4. Assign ControlVerificationAgent to simulate the system with the chosen algorithms and verify the results.
5. Finally, evaluate the final results and decide if further optimization is needed.

Please proceed with assigning the first task.
"""

human.initiate_chat(manager_chat, message=initial_message)