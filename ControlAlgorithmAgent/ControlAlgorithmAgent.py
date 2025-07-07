import autogen
from typing import Dict, Any
import numpy as np

def pid_controller_tool(k: float, Ti: float, y_max: float, y_min: float = None, xi_start: float = 0, y_start: float = 0):
    """
    Create a PID controller with the given parameters.
    
    Args:
    k (float): Proportional gain
    Ti (float): Integral time constant
    y_max (float): Maximum output value
    y_min (float): Minimum output value (default: None)
    xi_start (float): Initial integral term value (default: 0)
    y_start (float): Initial output value (default: 0)
    
    Returns:
    dict: A dictionary containing the PID controller class and its parameters
    """
    class PIController:
        def __init__(self, k, Ti, y_max, y_min=None, xi_start=0, y_start=0):
            self.k = k
            self.Ti = Ti
            self.y_max = y_max
            self.y_min = y_min if y_min is not None else -float('inf')
            self.xi = xi_start
            self.y = y_start

        def update(self, error, dt):
            self.xi += error * dt
            output = self.k * (error + self.xi / self.Ti)
            self.y = np.clip(output, self.y_min, self.y_max)
            
            if self.y == self.y_min or self.y == self.y_max:
                self.xi -= error * dt
            
            return self.y
    
    return {
        "controller": PIController,
        "parameters": {
            "k": k,
            "Ti": Ti,
            "y_max": y_max,
            "y_min": y_min,
            "xi_start": xi_start,
            "y_start": y_start
        }
    }

class ControlAlgorithmDesignAgent(autogen.AssistantAgent):
    def __init__(self, name: str, llm_config: Dict[str, Any]):
        system_message = """You are an expert in control algorithms for power electronics, specializing in PID controllers for Boost converters. Your responsibilities include:
1. Designing and explaining PID control algorithms
2. Providing insights on PID parameter tuning
3. Adapting the control algorithm based on system requirements
4. Collaborating with other agents to optimize controller performance

You have access to a PID controller tool that you can use to create and configure PID controllers. Use your expertise to design effective control algorithms for Boost converters."""
        super().__init__(name=name, system_message=system_message, llm_config=llm_config)

    def get_pid_controller(self, k: float, Ti: float, y_max: float, y_min: float = None):
        """Use the PID controller tool to get a configured controller."""
        return pid_controller_tool(k, Ti, y_max, y_min)

    def explain_pid_control(self) -> str:
        """Provide an explanation of PID control for Boost converters."""
        explanation = """
PID (Proportional-Integral-Derivative) control is a feedback control method widely used in Boost converters:

1. Proportional (P) term: Responds to current error. Larger P means faster response but potential overshoot.
2. Integral (I) term: Eliminates steady-state error. Larger I means faster error elimination but possible overshoot.
3. Derivative (D) term: Predicts future errors (not used in our current PI implementation).

Our PI controller adjusts the Boost converter's duty cycle to maintain the desired output voltage. It features:
- Anti-windup: Prevents integral term from growing too large
- Output limiting: Ensures safe operation within defined limits

Proper tuning of k (proportional gain) and Ti (integral time constant) is crucial for optimal performance.
        """
        return explanation

    def suggest_parameter_tuning(self) -> str:
        """Provide suggestions for PID parameter tuning."""
        suggestions = """
To tune the PI controller for a Boost converter:

1. Start with a small k and large Ti.
2. Increase k for faster response, watching for overshoot.
3. Decrease Ti to reduce steady-state error, monitoring for increased overshoot.
4. Fine-tune both parameters for balanced performance.
5. Consider:
   - Larger k: Faster response, but potential instability.
   - Smaller Ti: Better steady-state error elimination, but possible overshoot.
6. Use simulations to test different parameter combinations.
7. Validate under various load conditions.

Optimal parameters depend on specific Boost converter characteristics and performance requirements.
        """
        return suggestions

# Example usage
if __name__ == "__main__":
    llm_config = {
        "config_list": [{"model": "gpt-4"}],  # Replace with your actual config
    }
    agent = ControlAlgorithmDesignAgent(name="ControlAlgorithmDesigner", llm_config=llm_config)
    
    # Using the PID controller tool
    controller_config = agent.get_pid_controller(k=0.5, Ti=0.1, y_max=1.0)
    print("PID Controller Configuration:", controller_config)
    
    print(agent.explain_pid_control())
    print(agent.suggest_parameter_tuning())