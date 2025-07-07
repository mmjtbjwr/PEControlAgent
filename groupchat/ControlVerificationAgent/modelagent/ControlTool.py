from abc import ABC, abstractmethod
from typing import Dict
from pydantic import BaseModel, Field, validator

class ControlParams(BaseModel):
    control_params: Dict[str, float] = Field(..., description="Control parameters")

    class Config:
        extra = "forbid"

    @validator('control_params')
    def check_params(cls, v):
        required_prefixes = {'voltage_', 'current_'}
        required_suffixes = {'k', 'Ti', 'Td', 'y_max', 'y_min'}
        
        for prefix in required_prefixes:
            for suffix in required_suffixes:
                param = f"{prefix}{suffix}"
                if param not in v:
                    raise ValueError(f"Missing required parameter: {param}")
        return v

class ControllerFactory:
    @staticmethod
    def create_controller(controller_name: str, params: ControlParams) -> 'BaseController':
        if controller_name.lower() == "pid":
            return PIDController(params)
        if controller_name.lower() == "duallooppid":
            return DualLoopPIDController(params)
        else:
            raise ValueError(f"Unknown controller type: {controller_name}")

class BaseController(ABC):
    @abstractmethod
    def update(self, error: float, dt: float) -> float:
        pass

    @abstractmethod
    def reset(self):
        pass

class PIDController(BaseController):
    def __init__(self, params: Dict[str, float]):
        self.k = params['k']
        self.Ti = params['Ti']
        self.Td = params['Td']
        self.y_max = params['y_max']
        self.y_min = params['y_min']
        self.xi = 0
        self.last_error = 0
        self.y = 0

    def update(self, error: float, dt: float) -> float:
        self.xi += error * dt
        derivative = (error - self.last_error) / dt if dt > 0 else 0
        self.y = self.k * (error + self.xi / self.Ti + self.Td * derivative)
        self.y = max(min(self.y, self.y_max), self.y_min)
        self.last_error = error
        return self.y

    def reset(self):
        self.xi = 0
        self.last_error = 0
        self.y = 0

class DualLoopPIDController(BaseController):
    def __init__(self, params: ControlParams):
        voltage_params = {k[8:]: v for k, v in params.control_params.items() if k.startswith('voltage_')}
        current_params = {k[8:]: v for k, v in params.control_params.items() if k.startswith('current_')}
        self.voltage_controller = PIDController(voltage_params)  # 外环：电压控制
        self.current_controller = PIDController(current_params)  # 内环：电流控制

    def update(self, target_voltage: float, actual_voltage: float, actual_current: float, dt: float) -> float:
        # 外环：电压控制
        voltage_error = target_voltage - actual_voltage
        current_reference = self.voltage_controller.update(voltage_error, dt)
        
        # 内环：电流控制
        current_error = current_reference - actual_current
        duty_cycle = self.current_controller.update(current_error, dt)
        
        return duty_cycle

    def reset(self):
        self.voltage_controller.reset()
        self.current_controller.reset()

# 测试代码
if __name__ == "__main__":
    # 创建控制器参数
    control_params = ControlParams(control_params={
        'voltage_k': 1.0, 'voltage_Ti': 0.1, 'voltage_Td': 0.01, 'voltage_y_max': 10.0, 'voltage_y_min': 0.0,
        'current_k': 5.0, 'current_Ti': 0.01, 'current_Td': 0.001, 'current_y_max': 1.0, 'current_y_min': 0.0
    })

    # 测试创建双环PID控制器
    controller = ControllerFactory.create_controller("duallooppid", control_params)
    
    print("ControllerFactory exists:", "ControllerFactory" in globals())
    print("DualLoopPIDController created successfully:", isinstance(controller, DualLoopPIDController))