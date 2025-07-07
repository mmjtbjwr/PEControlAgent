from typing import Dict
from ControlTool import ControlParams, ControllerFactory
from SimulationTool import SimulationParams, SimulationFactory, visualize_simulation_results
from EvaluateTool import EvaluateParams, EvaluateFactory
from OptimizationTool import OptimizationFactory

def evaluate_pi_controller(fmu_path: str, Kp_voltage: float, Ti_voltage: float, Kp_current: float, Ti_current: float):
    # 创建控制参数
    control_params = ControlParams(control_params={
        'voltage_k': Kp_voltage,
        'voltage_Ti': Ti_voltage,
        'voltage_Td': 0,
        'voltage_y_max': 800,
        'voltage_y_min': 0.0,
        'current_k': Kp_current,
        'current_Ti': Ti_current,
        'current_Td': 0,
        'current_y_max': 1.0,
        'current_y_min': 0.0
    })

    # 创建控制器
    controller = ControllerFactory.create_controller("duallooppid", control_params)

    # 创建仿真参数
    simulation_params = SimulationParams(
        simulation_time=1.0,
        target_voltage=160,
        initial_voltage=80,
        step_size=0.0001
    )

    # 创建仿真工具
    simulation_tool = SimulationFactory.create_simulation_tool("boost")

    # 运行仿真
    simulation_result = simulation_tool.simulate(fmu_path, simulation_params, controller)

    # 创建评估参数
    evaluate_params = EvaluateParams(
        target_voltage=160,
        settling_time_coefficient=1.0,
        overshoot_coefficient=1.0,
        integrated_error_coefficient=1.0,
        post_settling_time_coefficient=1.0,
        post_overshoot_coefficient=1.0,
        post_integrated_error_coefficient=1.0
    )

    # 创建评估工具
    evaluater = EvaluateFactory.create_evaluater("duallooppid", evaluate_params)

    # 评估性能
    score, details = evaluater.evaluate(simulation_result)  # 修改这里，直接传入 simulation_result

    # 可视化仿真结果
    visualize_simulation_results(simulation_result, simulation_params.target_voltage)

    return score, details

if __name__ == "__main__":
    fmu_path = r"C:\Users\17338\Desktop\Multi agent interaction\ControlVerificationAgent\ControlVerificationAgent\boost_converternopid.fmu"  # 请替换为您的FMU文件路径

    # 测试不同的PI参数
    test_params = [
        (0.3, 0.006, 0.3, 0.006),  # (Kp_voltage, Ti_voltage, Kp_current, Ti_current)
        (1.0, 0.2, 2.0, 0.1),
        (0.8342, 0.0009, 0.8937, 0.1678)
    ]

    for params in test_params:
        Kp_voltage, Ti_voltage, Kp_current, Ti_current = params
        print(f"\nEvaluating PI controller with:")
        print(f"Voltage loop: Kp={Kp_voltage}, Ti={Ti_voltage}")
        print(f"Current loop: Kp={Kp_current}, Ti={Ti_current}")

        score, details = evaluate_pi_controller(fmu_path, Kp_voltage, Ti_voltage, Kp_current, Ti_current)

        print(f"Score: {score}")
        print("Details:")
        for key, value in details.items():
            print(f"  {key}: {value}")