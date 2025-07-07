# boost_converter.py

import numpy as np

class BoostConverter:
    def __init__(self, L, C, R, V_in, sample_time):
        self.L = L  # 电感值
        self.C = C  # 电容值
        self.R = R  # 负载电阻
        self.V_in = V_in  # 输入电压
        self.sample_time = sample_time  # 采样时间
        self.current = 0.0  # 电流
        self.voltage = 0.0  # 输出电压

    def update(self, duty_cycle):
        delta_I = (self.V_in - (1 - duty_cycle) * self.voltage) * self.sample_time / self.L  # 计算电流增量
        delta_V = ((1 - duty_cycle) * self.current - self.voltage / self.R) * self.sample_time / self.C  # 计算电压增量
        
        self.current += delta_I  # 更新电流
        self.voltage += delta_V  # 更新电压

        return self.voltage  # 返回当前输出电压
