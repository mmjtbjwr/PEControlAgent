# find_algorithm_tool.py

import sys
import inspect
from abc import ABC, abstractmethod

class BaseController(ABC):
    @abstractmethod
    def update(self, error: float, dt: float) -> float:
        pass

    @abstractmethod
    def reset(self):
        pass

class ControllerAlgorithmTool:
    def find_algorithm(self, requirements):
        # 动态搜索当前模块中的所有类
        available_controllers = self._get_available_controllers()
        
        if "DualLoopPIDController" in available_controllers:
            return "选择使用双闭环pid控制器，代码已配置完成"
        return "未找到合适的控制算法"

    def _get_available_controllers(self):
        # 获取当前模块中定义的所有类
        current_module = sys.modules[__name__]
        classes = inspect.getmembers(current_module, inspect.isclass)
        
        # 筛选出控制器类（假设所有控制器类都继承自BaseController）
        controller_classes = {name: cls for name, cls in classes 
                              if inspect.isclass(cls) and issubclass(cls, BaseController) and cls != BaseController}
        
        return controller_classes

# 创建工具实例
controller_algorithm_tool = ControllerAlgorithmTool()

def find_algorithm_tool(requirements):
    return controller_algorithm_tool.find_algorithm(requirements)

# 测试代码
if __name__ == "__main__":
    result = find_algorithm_tool({})
    print(result)
    print("Available controllers:", controller_algorithm_tool._get_available_controllers().keys())