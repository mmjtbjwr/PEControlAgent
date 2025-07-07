import json
import os
from autogen import ConversableAgent, GroupChat, GroupChatManager, UserProxyAgent
from typing import Dict
from pydantic import BaseModel
from SimulationTool import SimulationParams
from EvaluateTool import EvaluateParams
from OptimizationTool import OptimizationFactory
from ControlTool import ControlParams, ControllerFactory
from SimulationTool import SimulationFactory
from EvaluateTool import EvaluateFactory

llm_config = {
    "config_list": [
        {
            "model": "gpt-4",
            "api_key": "sk-yO3lbzc5glqovBFLC21e1143366244C6AaC408Ad76Ca7155",
            "base_url": "https://hk.xty.app/v1"
        }
    ]
}

class StateManager:
    def __init__(self):
        self.state = "initial"
        self.verification_input = None
        self.verification_result = None

state_manager = StateManager()

class VerificationInput(BaseModel):
    fmu_path: str
    control_algorithm_name: str
    control_algorithm_params: Dict[str, float]
    optimization_algorithm_name: str
    optimization_algorithm_params: Dict[str, float]
    simulation_params: Dict[str, float]
    evaluate_params: Dict[str, float]

class VerificationResult(BaseModel):
    mae: float
    overshoot: float
    settling_time: float
    rise_time: float
    best_params: Dict[str, float]

def verify_controller(verification_input: VerificationInput) -> VerificationResult:
    optimizer = OptimizationFactory.create_optimizer(
        verification_input.optimization_algorithm_name,
        verification_input.optimization_algorithm_params
    )

    control_params = ControlParams(control_params=verification_input.control_algorithm_params)
    control_tool = ControllerFactory.create_controller(verification_input.control_algorithm_name, control_params)

    simulation_tool = SimulationFactory.create_simulation_tool("boost")

    evaluater_tool = EvaluateFactory.create_evaluater("duallooppid", EvaluateParams(**verification_input.evaluate_params))

    bounds = [(0, 10) for _ in range(len(verification_input.control_algorithm_params))]
    initial_params = list(verification_input.control_algorithm_params.values())

    optimization_result = optimizer.optimize(
        verification_input.fmu_path,
        control_tool,
        control_params,
        simulation_tool,
        SimulationParams(**verification_input.simulation_params),
        evaluater_tool,
        EvaluateParams(**verification_input.evaluate_params),
        bounds,
        initial_params
    )

    best_params = optimization_result.best_params
    best_details = optimization_result.best_details

    return VerificationResult(
        mae=best_details.get('integrated_error', 0),
        overshoot=best_details.get('overshoot', 0),
        settling_time=best_details.get('settling_time', 0),
        rise_time=best_details.get('rise_time', 0),
        best_params={
            'voltage_k': best_params[0],
            'voltage_Ti': best_params[1],
            'current_k': best_params[2],
            'current_Ti': best_params[3]
        }
    )

def manager_response(self, messages, sender, config):
    if state_manager.state == "initial":
        state_manager.state = "verification"
        verification_input = {
            "fmu_path": os.path.abspath("C:/Users/17338/Desktop/Multi agent interaction/groupchat/ControlVerificationAgent/boost_converternopid.fmu"),
            "control_algorithm_name": "duallooppid",
            "control_algorithm_params": {
                'voltage_k': 1.0, 'voltage_Ti': 0.1, 'voltage_Td': 0, 'voltage_y_max': 800, 'voltage_y_min': 0.0,
                'current_k': 1.0, 'current_Ti': 0.1, 'current_Td': 0, 'current_y_max': 1, 'current_y_min': 0.0
            },
            "optimization_algorithm_name": "pso",
            "optimization_algorithm_params": {"swarm_size": 5, "max_iterations": 5, "w": 0.5, "c1": 1.5, "c2": 1.5},
            "simulation_params": {
                "simulation_time": 1,
                "target_voltage": 160,
                "initial_voltage": 80,
                "step_size": 0.0001
            },
            "evaluate_params": {
                "target_voltage": 160,
                "settling_time_coefficient": 1.0,
                "overshoot_coefficient": 1.0,
                "integrated_error_coefficient": 1.0,
                "post_settling_time_coefficient": 1.0,
                "post_overshoot_coefficient": 1.0,
                "post_integrated_error_coefficient": 1.0
            }
        }
        state_manager.verification_input = verification_input
        return False, f"控制验证智能体，请根据以下输入验证控制器设计：{json.dumps(verification_input)}"
    elif state_manager.state == "verification_completed":
        verification_result = state_manager.verification_result
        analysis = f"""
        验证结果分析：
        1. 平均绝对误差 (MAE): {verification_result.mae:.4f}
           目标: 低于 2
           状态: {'通过' if verification_result.mae < 2 else '未通过'}

        2. 过冲: {verification_result.overshoot:.2f}%
           目标: 低于 8%
           状态: {'通过' if verification_result.overshoot < 8 else '未通过'}

        3. 调节时间: {verification_result.settling_time:.4f}秒
           目标: 低于 0.5秒
           状态: {'通过' if verification_result.settling_time < 0.5 else '未通过'}

        4. 上升时间: {verification_result.rise_time:.4f}秒

        5. 优化后的控制器参数:
           电压 PI: Kp = {verification_result.best_params['voltage_k']:.4f}, Ki = {verification_result.best_params['voltage_k'] / verification_result.best_params['voltage_Ti']:.4f}
           电流 PI: Kp = {verification_result.best_params['current_k']:.4f}, Ki = {verification_result.best_params['current_k'] / verification_result.best_params['current_Ti']:.4f}

        总体评估:
        {'所有要求都满足。控制器设计成功。' if all([verification_result.mae < 2, verification_result.overshoot < 8, verification_result.settling_time < 0.5]) else '部分要求未满足。可能需要进一步优化或重新设计。'}
        """
        return True, analysis
    else:
        return True, "对话完成。"

manager_agent = ConversableAgent(
    name="ManagerAgent",
    system_message="你是监督Boost转换器控制器设计过程的经理。指示控制验证智能体并分析验证结果。不要生成具体的步骤只是告诉验证智能体开始验证。",
    llm_config=llm_config
)
manager_agent.register_reply(
    lambda messages: state_manager.state in ["initial", "verification_completed"],
    manager_response
)

def verification_response(self, messages, sender, config):
    verification_input = VerificationInput(**state_manager.verification_input)
    verification_result = verify_controller(verification_input)
    state_manager.verification_result = verification_result
    state_manager.state = "verification_completed"
    
    return True, f"验证完成。结果：{verification_result.dict()}"

control_verification_agent = ConversableAgent(
    name="ControlVerificationAgent",
    system_message="你负责验证Boost转换器控制器设计。",
    llm_config=llm_config
)
control_verification_agent.register_reply(
    lambda messages: state_manager.state == "verification",
    verification_response
)

human = UserProxyAgent(
    name="Human",
    system_message="你监督Boost转换器控制器设计过程。启动验证过程。",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=3,
    code_execution_config={"use_docker": False}
)

groupchat = GroupChat(
    agents=[human, manager_agent, control_verification_agent],
    messages=[],
    max_round=4
)

manager_chat = GroupChatManager(groupchat=groupchat, llm_config=llm_config)

if __name__ == "__main__":
    initial_message = "请开始控制器验证过程。"
    chat_result = human.initiate_chat(manager_chat, message=initial_message)
    print(chat_result)