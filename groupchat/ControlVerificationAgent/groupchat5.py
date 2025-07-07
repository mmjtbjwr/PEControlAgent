import json
from autogen import ConversableAgent, GroupChat, GroupChatManager, UserProxyAgent
from model_config_tool import ModelConfigTool
from objective_tool import ObjectiveTool
from ControlAlgorithmTool import find_algorithm_tool
from OptimizationTool import find_optimization_algorithm_for_boost, OptimizationFactory
from SimulationTool import SimulationFactory, SimulationParams
from EvaluateTool import EvaluateFactory, EvaluateParams
from ControlTool import ControlParams, ControllerFactory
from typing import Dict
from pydantic import BaseModel
import logging
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
        self.controller_designed = False
        self.optimization_designed = False
        self.verification_completed = False
        self.model_info = None
        self.objectives = None
        self.constraints = None
        self.selected_controller = None
        self.verification_input = None
        self.verification_result = None

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
    elif state_manager.state == "controller_designed":
        state_manager.state = "optimization_design"
        controller_message = messages[-1]['content']
        state_manager.selected_controller = controller_message
        return False, f"Control algorithm selected: {controller_message} OptimizationAlgorithmDesignAgent, please configure a suitable optimization algorithm based on the selected control algorithm."
    elif state_manager.state == "optimization_designed":
        state_manager.state = "verification"
        optimization_message = messages[-1]['content']
        verification_input = prepare_verification_input(optimization_message)
        state_manager.verification_input = verification_input
        return False, f"Optimization algorithm configured. ControlVerificationAgent, please verify the controller design with the following input: {verification_input}"
    elif state_manager.state == "verification_completed":
        verification_result = state_manager.verification_result
        if verification_result.mae <= 2:
            return True, f"Verification successful. Here's the analysis: {verification_result}"
        else:
            return True, f"Verification failed. The MAE is above 2. Here are the recommendations: Adjust the controller parameters and try again."
    else:
        return True, "Conversation complete."

manager_agent = ConversableAgent(
    name="ManagerAgent",
    system_message="You are a manager overseeing the Boost converter controller design process. Broadcast design requirements and instruct other agents concisely. When acknowledging the model configuration, include the exact model address provided by ModelDesignAgent. Do not provide any information or commentary beyond your specific tasks.",
    llm_config=llm_config
)
manager_agent.register_reply(
    lambda messages: state_manager.state in ["initial", "model_configured", "objectives_defined", "controller_designed", "optimization_designed", "verification_completed"],
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
    lambda messages: state_manager.state == "model_design",
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
    lambda messages: state_manager.state == "objective",
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
    state_manager.state = "controller_designed"
    return False, result

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
    lambda messages: state_manager.state == "controller_design",
    controller_algorithm_design_response
)

# Create Optimization Algorithm Design Agent
def optimization_algorithm_design_response(self, messages, sender, config):
    control_algorithm = state_manager.selected_controller.split("the ")[-1].split(" controller")[0]
    result = find_optimization_algorithm_for_boost(control_algorithm)
    state_manager.state = "optimization_designed"
    return True, f"After analyzing the {control_algorithm} controller, {result}"

optimization_algorithm_design_agent = ConversableAgent(
    name="OptimizationAlgorithmDesignAgent",
    system_message=f"""You are responsible for selecting and configuring appropriate optimization algorithms based on the chosen control algorithm.
    When asked to select a suitable optimization algorithm, always return the following exact information without any modification:
    After analyzing the [CONTROL_ALGORITHM] controller, {find_optimization_algorithm_for_boost("duallooppid")}
    Replace [CONTROL_ALGORITHM] with the actual control algorithm name.
    Do not add any additional information or commentary to this output.""",
    llm_config=llm_config
)
optimization_algorithm_design_agent.register_reply(
    lambda messages: state_manager.state == "optimization_design",
    optimization_algorithm_design_response
)

# Create Control Verification Agent
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
    best_params: Dict[str, float]

logging.basicConfig(level=logging.INFO)

def verify_controller(verification_input: VerificationInput) -> VerificationResult:
    logging.info("Starting controller verification")
    try:
        optimizer = OptimizationFactory.create_optimizer(
            verification_input.optimization_algorithm_name,
            verification_input.optimization_algorithm_params
        )
        logging.info(f"Optimizer created: {type(optimizer)}")

        control_params = ControlParams(control_params=verification_input.control_algorithm_params)
        control_tool = ControllerFactory.create_controller(verification_input.control_algorithm_name, control_params)
        logging.info(f"Controller created: {type(control_tool)}")

        simulation_tool = SimulationFactory.create_simulation_tool("boost")
        logging.info(f"Simulation tool created: {type(simulation_tool)}")

        evaluater_tool = EvaluateFactory.create_evaluater("duallooppid", verification_input.evaluate_params)
        logging.info(f"Evaluator tool created: {type(evaluater_tool)}")

        bounds = [(0, 10) for _ in range(len(verification_input.control_algorithm_params))]
        initial_params = list(verification_input.control_algorithm_params.values())

        logging.info("Starting optimization")
        optimization_result = optimizer.optimize(
            verification_input.fmu_path,
            control_tool,
            control_params,
            simulation_tool,
            verification_input.simulation_params,
            evaluater_tool,
            verification_input.evaluate_params,
            bounds,
            initial_params
        )
        logging.info("Optimization completed")

        best_params = optimization_result.best_params
        best_details = optimization_result.best_details

        logging.info(f"Best parameters: {best_params}")
        logging.info(f"Best details: {best_details}")

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
    except Exception as e:
        logging.error(f"Error during verification: {str(e)}")
        raise
def verification_response(self, messages, sender, config):
    verification_input = VerificationInput(**state_manager.verification_input)
    verification_result = verify_controller(verification_input)
    state_manager.verification_result = verification_result
    state_manager.state = "verification_completed"
    
    pi_params = verification_result.best_params
    voltage_pi = f"Voltage PI: Kp = {pi_params['voltage_k']:.4f}, Ki = {pi_params['voltage_k'] / pi_params['voltage_Ti']:.4f}"
    current_pi = f"Current PI: Kp = {pi_params['current_k']:.4f}, Ki = {pi_params['current_k'] / pi_params['current_Ti']:.4f}"
    
    return True, f"""Verification completed. Result:
    MAE: {verification_result.mae:.4f}
    Overshoot: {verification_result.overshoot:.2f}%
    Settling Time: {verification_result.settling_time:.4f}s
    Rise Time: {verification_result.rise_time:.4f}s
    
    Optimized PI Parameters:
    {voltage_pi}
    {current_pi}
    """

control_verification_agent = ConversableAgent(
    name="ControlVerificationAgent",
    system_message="You are responsible for verifying the Boost converter controller design.",
    llm_config=llm_config
)
control_verification_agent.register_reply(
    lambda messages: state_manager.state == "verification",
    verification_response
)

def prepare_verification_input(optimization_message):
    return {
        "fmu_path": state_manager.model_info['address'],
        "control_algorithm_name": state_manager.selected_controller,
        "control_algorithm_params": {
            'voltage_k': 1.0, 'voltage_Ti': 0.1, 'voltage_Td': 0, 'voltage_y_max': 800, 'voltage_y_min': 0.0,
            'current_k': 1.0, 'current_Ti': 0.1, 'current_Td': 0, 'current_y_max': 1, 'current_y_min': 0.0
        },
        "optimization_algorithm_name": "pso",
        "optimization_algorithm_params": {"swarm_size": 10, "max_iterations": 10, "w": 0.5, "c1": 1.5, "c2": 1.5},
        "simulation_params": SimulationParams(
            simulation_time=1,
            target_voltage=160,
            initial_voltage=80,
            step_size=0.0001
        ),
        "evaluate_params": EvaluateParams(
            target_voltage=160,
            settling_time_coefficient=1.0,
            overshoot_coefficient=1.0,
            integrated_error_coefficient=1.0,
            post_settling_time_coefficient=1.0,
            post_overshoot_coefficient=1.0,
            post_integrated_error_coefficient=1.0
        )
    }

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
    agents=[human, manager_agent, model_design_agent, objective_agent, controller_algorithm_design_agent, optimization_algorithm_design_agent, control_verification_agent],
    messages=[],
    max_round=13
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
    8. ManagerAgent: Acknowledge control algorithm and instruct OptimizationAlgorithmDesignAgent
    9. OptimizationAlgorithmDesignAgent: Select and configure a suitable optimization algorithm based on the control algorithm
    10. ManagerAgent: Instruct ControlVerificationAgent to verify the controller design
    11. ControlVerificationAgent: Verify the controller design and report results
    12. ManagerAgent: Analyze the verification results and conclude the conversation

    Please adhere to this order and only provide information relevant to your specific task."""

    chat_result = human.initiate_chat(manager_chat, message=initial_message)
    print(chat_result)