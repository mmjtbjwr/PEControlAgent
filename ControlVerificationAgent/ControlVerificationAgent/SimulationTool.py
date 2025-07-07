import numpy as np
import matplotlib.pyplot as plt
from pyfmi import load_fmu
from typing import Type, Dict, List
from pydantic import BaseModel
from abc import ABC, abstractmethod
from ControlTool import ControlParams, ControllerFactory, BaseController

class SimulationFactory:
    @staticmethod
    def create_simulation_tool(simulation_type: str):
        if simulation_type.lower() == "boost":
            return BoostSimulationTool()
        else:
            raise ValueError(f"Unknown simulation type: {simulation_type}")

class SimulationResult(BaseModel):
    times: List[float]
    voltages: List[float]
    currents: List[float]
    duty_cycles: List[float]

class SimulationParams(BaseModel):
    simulation_time: float
    target_voltage: float
    initial_voltage: float
    step_size: float

class BaseSimulater(ABC):
    @abstractmethod
    def simulate(self, fmu_path: str, simulation_params: SimulationParams,
                 controller: BaseController) -> SimulationResult:
        pass

class BoostSimulationTool(BaseSimulater):
    def simulate(self, fmu_path: str, simulation_params: SimulationParams,
                 controller: BaseController):
        model = load_fmu(fmu_path)
        model.setup_experiment(start_time=0)
        model.enter_initialization_mode()
        model.exit_initialization_mode()

        time = np.arange(0, simulation_params.simulation_time, simulation_params.step_size)
        voltage = np.zeros_like(time)
        current = np.zeros_like(time)
        duty_cycle = np.zeros_like(time)

        for i, t in enumerate(time):
            model.do_step(t, simulation_params.step_size)
            
            actual_voltage = model.get('voltageSensor.v')[0]
            actual_current = model.get('currentSensor.i')[0]
            
            new_duty_cycle = controller.update(simulation_params.target_voltage, actual_voltage, actual_current, simulation_params.step_size)
            
            model.set('const3.k', [new_duty_cycle])

            voltage[i] = actual_voltage
            current[i] = actual_current
            duty_cycle[i] = new_duty_cycle

        model.terminate()
        return SimulationResult(times=time.tolist(), voltages=voltage.tolist(), 
                                currents=current.tolist(), duty_cycles=duty_cycle.tolist())

def visualize_simulation_results(simulation_result: SimulationResult, target_voltage: float):
    start_index = np.searchsorted(simulation_result.times, 0.001)
    
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 15))

    ax1.plot(simulation_result.times[start_index:], simulation_result.voltages[start_index:])
    ax1.axhline(y=target_voltage, color='r', linestyle='--')
    ax1.set_ylabel('Voltage (V)')
    ax1.set_title('Output Voltage')
    ax1.set_ylim(100, 200)  # Set y-axis range to 100V to 200V
    ax1.legend(['Actual', 'Target'])

    ax2.plot(simulation_result.times[start_index:], simulation_result.currents[start_index:])
    ax2.set_ylabel('Current (A)')
    ax2.set_title('Inductor Current')

    ax3.plot(simulation_result.times[start_index:], simulation_result.duty_cycles[start_index:])
    ax3.set_ylabel('Duty Cycle')
    ax3.set_xlabel('Time (s)')
    ax3.set_title('PWM Duty Cycle')

    for ax in [ax1, ax2, ax3]:
        ax.set_xlim(0.001, simulation_result.times[-1])
        ax.grid(True)

    plt.tight_layout()
    plt.show()

def calculate_performance_metrics(simulation_result: SimulationResult, target_voltage: float):
    voltage = np.array(simulation_result.voltages)
    time = np.array(simulation_result.times)

    overshoot = max(0, (max(voltage) - target_voltage) / target_voltage * 100)
    
    settling_time = None
    settled = False
    for t, v in zip(time, voltage):
        if not settled and abs(v - target_voltage) / target_voltage < 0.02:  # 2% settling time
            settling_time = t
            settled = True
            break
    
    steady_state_error = abs(voltage[-1] - target_voltage) / target_voltage * 100
    
    return {
        "Overshoot (%)": overshoot,
        "Settling Time (s)": settling_time,
        "Steady State Error (%)": steady_state_error
    }

if __name__ == "__main__":
    fmu_path = r"C:\Users\17338\Desktop\Multi agent interaction\ControlVerificationAgent\ControlVerificationAgent\boost_converternopid.fmu"
    
    simulation_params = SimulationParams(
        simulation_time=1.0,
        target_voltage=160,
        initial_voltage=80,
        step_size=0.0001
    )

    control_params = ControlParams(control_params={
        'voltage_k': 0.3, 'voltage_Ti': 0.006, 'voltage_Td': 0, 'voltage_y_max': 160, 'voltage_y_min': 0.0,
        'current_k': 0.3, 'current_Ti': 0.006, 'current_Td': 0, 'current_y_max': 1.0, 'current_y_min': 0.0
    })

    simulation_tool = SimulationFactory.create_simulation_tool("boost")
    controller = ControllerFactory.create_controller("duallooppid", control_params)

    simulation_result = simulation_tool.simulate(fmu_path, simulation_params, controller)

    print("Simulation completed. Visualizing results...")
    visualize_simulation_results(simulation_result, simulation_params.target_voltage)

    metrics = calculate_performance_metrics(simulation_result, simulation_params.target_voltage)
    print("\nPerformance Metrics:")
    for key, value in metrics.items():
        print(f"{key}: {value}")