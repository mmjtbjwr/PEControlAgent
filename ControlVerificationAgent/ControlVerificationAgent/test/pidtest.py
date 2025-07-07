import numpy as np
import matplotlib.pyplot as plt
from pyfmi import load_fmu
from power_electronics_control import ControllerFactory, ControlParams

def simulate_boost_converter(fmu_path, controller, target_voltage, simulation_time, step_size):
    # 加载FMU
    model = load_fmu(fmu_path)
    
    # 初始化结果数组
    time = np.arange(0, simulation_time, step_size)
    voltage = np.zeros_like(time)
    current = np.zeros_like(time)
    duty_cycle = np.zeros_like(time)

    # 设置和初始化仿真
    model.setup_experiment(start_time=0)
    model.enter_initialization_mode()
    model.exit_initialization_mode()

    # 运行仿真
    for i, t in enumerate(time):
        if i > 0:
            model.do_step(t - step_size, step_size)
        
        # 获取当前状态
        actual_voltage = model.get('voltageSensor.v')[0]
        actual_current = model.get('currentSensor.i')[0]
        
        # 使用控制器计算新的占空比
        new_duty_cycle = controller.update(target_voltage, actual_voltage, actual_current, step_size)
        
        # 将新的占空比应用到模型
        model.set('const3.k', new_duty_cycle)

        # 记录结果
        voltage[i] = actual_voltage
        current[i] = actual_current
        duty_cycle[i] = new_duty_cycle

    model.terminate()
    return time, voltage, current, duty_cycle

def plot_results(time, voltage, current, duty_cycle, target_voltage):
    # 找到时间大于等于0.001秒的索引
    start_index = np.searchsorted(time, 0.001)
    
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 15))

    ax1.plot(time[start_index:], voltage[start_index:])
    ax1.axhline(y=target_voltage, color='r', linestyle='--')
    ax1.set_ylabel('Voltage (V)')
    ax1.set_title('Output Voltage')
    ax1.set_ylim(100, 200)  # 设置y轴范围为100V到200V
    ax1.legend(['Actual', 'Target'])

    ax2.plot(time[start_index:], current[start_index:])
    ax2.set_ylabel('Current (A)')
    ax2.set_title('Inductor Current')

    ax3.plot(time[start_index:], duty_cycle[start_index:])
    ax3.set_ylabel('Duty Cycle')
    ax3.set_xlabel('Time (s)')
    ax3.set_title('PWM Duty Cycle')

    # 设置所有子图的x轴起始点为0.001秒
    for ax in [ax1, ax2, ax3]:
        ax.set_xlim(0.001, time[-1])

    plt.tight_layout()
    plt.show()

def calculate_performance_metrics(time, voltage, target_voltage):
    settling_time = None
    overshoot = max(0, (max(voltage) - target_voltage) / target_voltage * 100)
    
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
    # FMU文件路径
    fmu_path = "C:\\Users\\17338\\Desktop\\Multi agent interaction\\ControlVerificationAgent\\ControlVerificationAgent\\boost_converternopid.fmu"

    # 仿真参数
    simulation_time = 1  # 秒
    step_size = 0.0001  # 秒
    target_voltage = 160  # 目标电压

    # 控制器参数
    control_params = ControlParams(control_params={
        'voltage_k': 9.771, 'voltage_Ti': 1.401, 'voltage_Td': 0, 'voltage_y_max': 160, 'voltage_y_min': 0.0,
        'current_k': 5.926, 'current_Ti': 6.850, 'current_Td': 0, 'current_y_max': 1.0, 'current_y_min': 0.0
    })

    # 创建控制器
    controller = ControllerFactory.create_controller("duallooppid", control_params)

    # 运行仿真
    time, voltage, current, duty_cycle = simulate_boost_converter(fmu_path, controller, target_voltage, simulation_time, step_size)

    # 绘制结果
    plot_results(time, voltage, current, duty_cycle, target_voltage)

    # 计算性能指标
    metrics = calculate_performance_metrics(time, voltage, target_voltage)

    print("Performance Metrics:")
    for key, value in metrics.items():
        print(f"{key}: {value}")