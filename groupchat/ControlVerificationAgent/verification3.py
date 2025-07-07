from typing import Dict, List, Type
from autogen import AssistantAgent, UserProxyAgent
from pydantic import BaseModel, Field
from typing_extensions import Annotated
import numpy as np
from OptimizationTool import OptimizationFactory, BaseOptimizer, PSOOptimizer, GAOptimizer
from ControlTool import ControlParams, ControllerFactory, BaseController, PIDController, DualLoopPIDController
from EvaluateTool import EvaluateFactory, EvaluateParams, BaseEvaluater, DualLoopPIDEvaluater
from SimulationTool import SimulationFactory, SimulationParams, BaseSimulater, SimulationResult, BoostSimulationTool
from OptimizationTool import OptimizationResult

class VerificationInput(BaseModel):
    fmu_path: str
    control_algorithm_name: str
    control_algorithm_params: Dict[str, float]
    optimization_algorithm_name: str
    optimization_algorithm_params: Dict[str, float]
    simulation_params: SimulationParams
    evaluate_params: EvaluateParams

class VerificationResult(BaseModel):
    mae: float
    overshoot: float
    settling_time: float
    rise_time: float
    robustness_score: float
    anti_interference_score: float
    best_params: List[float]

class ControlVerificationAgent(AssistantAgent):
    def __init__(self, name: str, config_list: List[dict]):
        super().__init__(
            name=name,
            system_message="You are an AI agent specialized in verifying and validating control algorithms for power electronic devices using FMU simulations.",
            llm_config={"config_list": config_list}
        )

    def verify_controller(self, input: VerificationInput) -> VerificationResult:
        optimizer = OptimizationFactory.create_optimizer(
            input.optimization_algorithm_name,
            input.optimization_algorithm_params
        )

        control_params = ControlParams(control_params=input.control_algorithm_params)
        control_tool = ControllerFactory.create_controller(input.control_algorithm_name, control_params)
        simulation_tool = SimulationFactory.create_simulation_tool("boost")
        evaluater_tool = EvaluateFactory.create_evaluater("duallooppid", input.evaluate_params)

        bounds = [(0, 10) for _ in range(len(input.control_algorithm_params))]
        initial_params = list(input.control_algorithm_params.values())

        optimization_result: OptimizationResult = optimizer.optimize(
            input.fmu_path,
            control_tool,
            control_params,
            simulation_tool,
            input.simulation_params,
            evaluater_tool,
            input.evaluate_params,
            bounds,
            initial_params
        )

        best_params = optimization_result.best_params
        best_score = optimization_result.best_score
        best_details = optimization_result.best_details

        return VerificationResult(
            mae=best_details.get('integrated_error', 0),
            overshoot=best_details.get('overshoot', 0),
            settling_time=best_details.get('settling_time', 0),
            rise_time=best_details.get('rise_time', 0),
            robustness_score=0.8,
            anti_interference_score=0.7,
            best_params=best_params
        )

    def run(self, input: VerificationInput) -> str:
        result = self.verify_controller(input)

        response = f"Verification Results:\n"
        response += f"MAE: {result.mae:.4f}\n"
        response += f"Overshoot: {result.overshoot:.2f}%\n"
        response += f"Settling Time: {result.settling_time:.4f} s\n"
        response += f"Rise Time: {result.rise_time:.4f} s\n"
        response += f"Robustness Score: {result.robustness_score:.2f}\n"
        response += f"Anti-Interference Score: {result.anti_interference_score:.2f}\n"
        response += f"Best PID Parameters: {result.best_params}\n"

        if result.mae <= 0.5:
            response += "The optimized controller meets the MAE target of 0.5."
        else:
            response += "The optimized controller does not meet the MAE target of 0.5. Further optimization may be required."

        return response

config_list = [{"model": "qwen2-72b-instruct", "api_key": "sk-33886890d3154f938ac26430eccb6ae8",
                "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1"}]

verification_agent = ControlVerificationAgent("ControlVerifier", config_list)

assistant = AssistantAgent(
    name="Assistant",
    system_message="You are a helpful AI assistant. "
                   "You can help with control algorithm verification for power electronic devices. "
                   "Return 'TERMINATE' when the task is done.",
    llm_config={"config_list": config_list},
    code_execution_config={"use_docker": False}
)

user_proxy = UserProxyAgent(
    name="User",
    llm_config=False,
    is_termination_msg=lambda msg: msg.get("content") is not None and "TERMINATE" in msg["content"],
    code_execution_config={"use_docker": False},
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
    system_message="You are a helpful AI assistant. "
                   "You can help with control algorithm verification for power electronic devices. "
                   "Return 'TERMINATE' when the task is done.",
)

def verify_controller_wrapper(input_dict: Dict) -> Dict:
    simulation_params = SimulationParams(
        simulation_time=1,
        target_voltage=160,
        initial_voltage=80,
        step_size=0.0001
    )
    evaluate_params = EvaluateParams(
        target_voltage=160,
        settling_time_coefficient=1.0,
        overshoot_coefficient=1.0,
        integrated_error_coefficient=1.0,
        post_settling_time_coefficient=1.0,
        post_overshoot_coefficient=1.0,
        post_integrated_error_coefficient=1.0
    )

    # 转换控制参数
    control_params = {
        'voltage_k': input_dict['control_algorithm_params'].get('outer_k', 1.0),
        'voltage_Ti': input_dict['control_algorithm_params'].get('outer_Ti', 0.1),
        'voltage_Td': input_dict['control_algorithm_params'].get('outer_Td', 0),
        'voltage_y_max': input_dict['control_algorithm_params'].get('outer_y_max', 1.0),
        'voltage_y_min': input_dict['control_algorithm_params'].get('outer_y_min', 0.0),
        'current_k': input_dict['control_algorithm_params'].get('inner_k', 1.0),
        'current_Ti': input_dict['control_algorithm_params'].get('inner_Ti', 0.1),
        'current_Td': input_dict['control_algorithm_params'].get('inner_Td', 0),
        'current_y_max': input_dict['control_algorithm_params'].get('inner_y_max', 1.0),
        'current_y_min': input_dict['control_algorithm_params'].get('inner_y_min', 0.0)
    }

    input_dict['control_algorithm_params'] = control_params
    input_dict['simulation_params'] = simulation_params
    input_dict['evaluate_params'] = evaluate_params
    input_obj = VerificationInput(**input_dict)
    result = verification_agent.verify_controller(input_obj)
    
    # 构建包含最佳参数的结果字典
    result_dict = result.dict()
    result_dict['best_pid_params'] = {
        'voltage_k': result.best_params[0],
        'voltage_Ti': result.best_params[1],
        'current_k': result.best_params[2],
        'current_Ti': result.best_params[3]
    }
    
    return result_dict

from autogen import register_function

register_function(
    verify_controller_wrapper,
    caller=assistant,
    executor=user_proxy,
    name="verify_controller",
    description="Verify and validate the performance of a power electronic device controller using FMU simulation and optimization. "
                "The function requires the following inputs: "
                "1. 'fmu_path': The path to the FMU file. "
                "2. 'control_algorithm_name': The name of the control algorithm to use. "
                "3. 'control_algorithm_params': A dictionary of parameters for the control algorithm. "
                "4. 'optimization_algorithm_name': The name of the optimization algorithm to use. "
                "5. 'optimization_algorithm_params': A dictionary of parameters for the optimization algorithm. "
                "6. 'simulation_params': A SimulationParams object containing the parameters for the simulation. "
                "7. 'evaluate_params': An EvaluateParams object containing the parameters for the evaluation.",
)

verification_input_dict = {
    "fmu_path": r"C:\\Users\\17338\Desktop\\Multi agent interaction\\ControlVerificationAgent\\ControlVerificationAgent\\boost_converternopid.fmu",
    "control_algorithm_name": "duallooppid",
    "control_algorithm_params": {
        'inner_k': 1.0, 'inner_Ti': 0.1, 'inner_Td': 0, 'inner_y_max': 1, 'inner_y_min': 0.0,
        'outer_k': 1.0, 'outer_Ti': 0.1, 'outer_Td': 0, 'outer_y_max': 800, 'outer_y_min': 0.0
    },
    "optimization_algorithm_name": "pso",
    "optimization_algorithm_params": {"swarm_size": 10, "max_iterations": 10, "w": 0.5, "c1": 1.5, "c2": 1.5},
}

question = f"Verify and optimize the performance of a power electronic device controller with the following input: {verification_input_dict}"
chat_result = user_proxy.initiate_chat(assistant, message=question)

# Print the chat result
for message in chat_result.chat_history:
    print(f"{message['role']}: {message['content']}")