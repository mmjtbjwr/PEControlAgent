from typing import Type, Dict
from pydantic import BaseModel
from SimulationTool import SimulationResult

class EvaluateParams(BaseModel):
    target_voltage: float
    settling_time_coefficient: float
    overshoot_coefficient: float
    integrated_error_coefficient: float
    post_settling_time_coefficient: float
    post_overshoot_coefficient: float
    post_integrated_error_coefficient: float

from abc import ABC, abstractmethod
from typing import Tuple, Dict

class BaseEvaluater(ABC):
    @abstractmethod
    def evaluate(self, simulation_result: SimulationResult) -> Tuple[float, Dict[str, float]]:
        pass

class EvaluateFactory(BaseEvaluater):
    @staticmethod
    def create_evaluater(name: str, params: EvaluateParams):
        if name.lower() == "duallooppid":
            return DualLoopPIDEvaluater(params)
        else:
            raise ValueError(f"Unknown Evaluate method: {name}")

class DualLoopPIDEvaluater:
    def __init__(self, params: EvaluateParams):
        self.params = params

    def evaluate(self, simulation_result: SimulationResult):
        voltages = simulation_result.voltages
        times = simulation_result.times

        settling_time = 0
        overshoot = 0
        integrated_error = 0
        post_settling_time = 0
        post_overshoot = 0
        post_integrated_error = 0

        target_voltage = self.params.target_voltage

        # 找到0.5秒对应的索引
        load_switch_index = next(i for i, t in enumerate(times) if t >= 0.5)

        settled = False
        for i, v in enumerate(voltages[:load_switch_index]):
            if not settled and abs(v - target_voltage) / target_voltage <= 0.02:
                settling_time = times[i]
                settled = True

            overshoot = max(overshoot, (v - target_voltage) / target_voltage)
            integrated_error += abs(v - target_voltage) / target_voltage * (times[1] - times[0])

        post_switch_voltages = voltages[load_switch_index:]
        post_switch_times = [t - 0.5 for t in times[load_switch_index:]]

        settled = False
        for i, v in enumerate(post_switch_voltages):
            if not settled and abs(v - target_voltage) / target_voltage <= 0.02:
                post_settling_time = post_switch_times[i]
                settled = True

            post_overshoot = max(post_overshoot, (v - target_voltage) / target_voltage)
            post_integrated_error += abs(v - target_voltage) / target_voltage * (
                    post_switch_times[1] - post_switch_times[0])

        score = settling_time * self.params.settling_time_coefficient \
                + post_settling_time * self.params.post_settling_time_coefficient \
                + overshoot * self.params.overshoot_coefficient \
                + post_overshoot * self.params.post_overshoot_coefficient \
                + integrated_error * self.params.integrated_error_coefficient \
                + post_integrated_error * self.params.post_integrated_error_coefficient

        return score, {
            'settling_time': settling_time,
            'overshoot': overshoot,
            'integrated_error': integrated_error,
            'post_settling_time': post_settling_time,
            'post_overshoot': post_overshoot,
            'post_integrated_error': post_integrated_error
        }

if __name__ == "__main__":
    # 创建模拟的SimulationResult对象用于测试
    import numpy as np
    
    times = np.linspace(0, 1, 10001)  # 0到1秒，步长0.0001
    voltages = 160 + 10 * np.sin(2 * np.pi * times)  # 模拟波动的电压
    voltages[5000:] += 5  # 在0.5秒后增加5V模拟负载变化
    currents = np.ones_like(times)  # 假设电流恒定
    duty_cycles = np.ones_like(times) * 0.5  # 假设占空比恒定

    simulation_result = SimulationResult(
        times=times.tolist(),
        voltages=voltages.tolist(),
        currents=currents.tolist(),
        duty_cycles=duty_cycles.tolist()
    )

    # 创建EvaluateParams对象
    evaluate_params = EvaluateParams(
        target_voltage=160,
        settling_time_coefficient=1.0,
        overshoot_coefficient=1.0,
        integrated_error_coefficient=1.0,
        post_settling_time_coefficient=1.0,
        post_overshoot_coefficient=1.0,
        post_integrated_error_coefficient=1.0
    )

    # 创建DualLoopPIDEvaluater对象
    evaluater = EvaluateFactory.create_evaluater("duallooppid", params=evaluate_params)

    # 调用evaluate方法
    score, details = evaluater.evaluate(simulation_result)

    # 打印结果
    print(f"Score: {score}")
    print(f"Details: {details}")