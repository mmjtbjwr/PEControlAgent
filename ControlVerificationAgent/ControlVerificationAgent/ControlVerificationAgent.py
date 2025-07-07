from typing import Dict, List, Type
from autogen import ConversableAgent

from autogen import AssistantAgent, UserProxyAgent
from pydantic import BaseModel, Field
from typing_extensions import Annotated
import numpy as np


class ControlAlgorithm(BaseModel):
    name: str
    params: Dict[str, float]

class OptimizationAlgorithm(BaseModel):
    name: str
    params: Dict[str, float]

class VerificationInput(BaseModel):
    fmu_path: str
    control_algorithm_name: str
    control_algorithm_params: Dict[str, float]
    optimization_algorithm_name: str
    optimization_algorithm_params: Dict[str, float]

class VerificationResult(BaseModel):
    mae: float
    overshoot: float
    settling_time: float
    rise_time: float
    robustness_score: float
    anti_interference_score: float

class OptimizationFactory:
    @staticmethod
    def create_optimizer(name: str, params: Dict[str, float]):
        if name.lower() == "pso":
            return PSOOptimizer(**params)
        elif name.lower() == "ga":
            return GAOptimizer(**params)
        else:
            raise ValueError(f"Unknown optimization algorithm: {name}")

class BaseOptimizer:
    def optimize(self, objective_function, bounds):
        raise NotImplementedError("Subclasses must implement optimize method")

class PSOOptimizer(BaseOptimizer):
    def __init__(self, swarm_size: int, max_iterations: int):
        self.swarm_size = swarm_size
        self.max_iterations = max_iterations

    def optimize(self, objective_function, bounds):
        # Implement PSO algorithm here
        pass

class GAOptimizer(BaseOptimizer):
    def __init__(self, population_size: int, max_generations: int):
        self.population_size = population_size
        self.max_generations = max_generations

    def optimize(self, objective_function, bounds):
        # Implement GA algorithm here
        pass

class ControlVerificationAgent(ConversableAgent):
    def __init__(self, name: str, config_list: List[dict]):
        super().__init__(
            name=name,
            system_message="You are an AI agent specialized in verifying and validating control algorithms for power electronic devices using FMU simulations.",
            llm_config={"config_list": config_list}
        )
        # self.register_function(
        #     function=self.verify_controller,
        #     name="verify_controller",
        #     description="Verify and validate control algorithm performance using FMU simulation and optimization"
        # )

    def verify_controller(self, input: VerificationInput) -> VerificationResult:
        # Create optimizer
        optimizer = OptimizationFactory.create_optimizer(
            input.optimization_algorithm_name,
            input.optimization_algorithm_params
        )

        # Define objective function
        def objective_function(params):
            control_algorithm = ControlAlgorithm(
                name=input.control_algorithm_name,
                params=dict(zip(input.control_algorithm_params.keys(), params))
            )
            time, output, setpoint = self.simulate_fmu(input.fmu_path, control_algorithm)
            mae = self.calculate_mae(output, setpoint)
            return mae

        # Define bounds for optimization
        bounds = [(0, 10) for _ in range(len(input.control_algorithm_params))]  # Example bounds, adjust as needed

        # Optimize control parameters
        best_params = optimizer.optimize(objective_function, bounds)

        # Simulate with optimized parameters
        optimized_control_algorithm = ControlAlgorithm(
            name=input.control_algorithm_name,
            params=dict(zip(input.control_algorithm_params.keys(), best_params))
        )
        time, output, setpoint = self.simulate_fmu(input.fmu_path, optimized_control_algorithm)

        # Calculate performance metrics
        mae = self.calculate_mae(output, setpoint)
        overshoot = self.calculate_overshoot(output, setpoint)
        settling_time = self.calculate_settling_time(time, output, setpoint)
        rise_time = self.calculate_rise_time(time, output, setpoint)

        # Assess robustness and anti-interference
        robustness_score = self.assess_robustness(input)
        anti_interference_score = self.assess_anti_interference(input)

        return VerificationResult(
            mae=mae,
            overshoot=overshoot,
            settling_time=settling_time,
            rise_time=rise_time,
            robustness_score=robustness_score,
            anti_interference_score=anti_interference_score
        )

    # ... (other methods remain the same)

    def run(self, input: VerificationInput) -> str:
        result = self.verify_controller(input)

        response = f"Verification Results:\n"
        response += f"MAE: {result.mae:.4f}\n"
        response += f"Overshoot: {result.overshoot:.2f}%\n"
        response += f"Settling Time: {result.settling_time:.4f} s\n"
        response += f"Rise Time: {result.rise_time:.4f} s\n"
        response += f"Robustness Score: {result.robustness_score:.2f}\n"
        response += f"Anti-Interference Score: {result.anti_interference_score:.2f}\n"

        if result.mae <= 0.5:
            response += "The optimized controller meets the MAE target of 0.5."
        else:
            response += "The optimized controller does not meet the MAE target of 0.5. Further optimization may be required."

        return response




# Usage example
config_list = [{"model": "qwen2-72b-instruct", "api_key": "sk-33886890d3154f938ac26430eccb6ae8",
                "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1"}]

verification_agent = ControlVerificationAgent("ControlVerifier", config_list)

# Create assistant and user_proxy instances
assistant = ConversableAgent(
    name="Assistant",
    system_message="You are a helpful AI assistant. "
                   "You can help with control algorithm verification for power electronic devices. "
                   "Return 'TERMINATE' when the task is done.",
    llm_config={"config_list": config_list},
)

user_proxy = ConversableAgent(
    name="User",
    llm_config=False,
    is_termination_msg=lambda msg: msg.get("content") is not None and "TERMINATE" in msg["content"],
    human_input_mode="NEVER",
)

# Register the ControlVerificationAgent's verify_controller function
from autogen import register_function

# Register the ControlVerificationAgent's verify_controller function
def verify_controller_wrapper(input_dict: Dict):
    input_obj = VerificationInput(**input_dict)
    result = verification_agent.verify_controller(input_obj)
    return result.dict()

from autogen import register_function

register_function(
    verify_controller_wrapper,
    caller=assistant,
    executor=user_proxy,
    name="verify_controller",
    description="Verify and validate control algorithm performance using FMU simulation and optimization",
)

# Example usage
# verification_input = VerificationInput(
#     fmu_path=r"H:\project_code\pso-pid\boosttwopid\boost_converternopid.fmu",
#     control_algorithm_name="PID",
#     control_algorithm_params={"Kp": 1.5, "Ki": 0.1, "Kd": 0.05},
#     optimization_algorithm_name="PSO",
#     optimization_algorithm_params={"swarm_size": 10, "max_iterations": 100}
# )

verification_input_dict = {
    "fmu_path": r"H:\project_code\pso-pid\boosttwopid\boost_converternopid.fmu",
    "control_algorithm_name": "PID",
    "control_algorithm_params": {"Kp": 1.5, "Ki": 0.1, "Kd": 0.05},
    "optimization_algorithm_name": "PSO",
    "optimization_algorithm_params": {"swarm_size": 10, "max_iterations": 100}
}

verify_controller_wrapper(verification_input_dict)


# question = f"Verify and optimize the performance of a power electronic device controller with the following input: {verification_input}"
# chat_result = user_proxy.initiate_chat(assistant, message=question)
#
# # Print the chat result
# for message in chat_result.chat_history:
#     print(f"{message['role']}: {message['content']}")