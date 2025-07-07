import autogen
from typing import Annotated
from pydantic import BaseModel, Field

# 导入所有agent
from ManagerAgent.ManagerAgent import ManagerAgent
from ObjectiveAgent.ObjectiveAgent import ObjectiveDesignAgent
from ModelDesignAgent.ModelDesignAgent import ModelDesignAgent
from ControlAlgorithmAgent.ControlAlgorithmAgent import ControlAlgorithmAgent, pid_controller_tool
from ControlParameterAgent.ControlParameterAgent import ControlParameterAgent, pso_optimize_tool
from ControlVerificationAgent.ControlVerificationAgent import ControlVerificationAgent

# 配置
config_list = [
    {
        "model": "qwen2-72b-instruct",
        "api_key": "sk-33886890d3154f938ac26430eccb6ae8",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1"
    },
]

llm_config = {"config_list": config_list}

# 创建所有agent实例
manager = ManagerAgent(name="Manager", llm_config=llm_config)
objective_agent = ObjectiveDesignAgent(name="Objective_Designer", llm_config=llm_config)
model_agent = ModelDesignAgent(name="Model_Designer", llm_config=llm_config)
algorithm_agent = ControlAlgorithmAgent(name="Algorithm_Designer", llm_config=llm_config)
parameter_agent = ControlParameterAgent(name="Parameter_Designer", llm_config=llm_config)
verification_agent = ControlVerificationAgent(name="Verification_Agent", llm_config=llm_config)

# 创建用户代理
user_proxy = autogen.UserProxyAgent(
    name="User",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda x: x.get("content", "") and "TERMINATE" in x["content"],
)

# 注册PID控制器工具和PSO优化工具
autogen.register_function(pid_controller_tool, caller=algorithm_agent, executor=user_proxy)
autogen.register_function(pso_optimize_tool, caller=parameter_agent, executor=user_proxy)

# 定义PIDMAE类，用于PSO优化
class PIDMAE(BaseModel):
    mae: Annotated[float, Field(description="The Mean Absolute Error.")]

def main():
    # 初始化群聊
    groupchat = autogen.GroupChat(
        agents=[manager, objective_agent, model_agent, algorithm_agent, parameter_agent, verification_agent, user_proxy],
        messages=[],
        max_round=50
    )
    manager_chat = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)
    
    # 开始任务
    user_proxy.initiate_chat(
        manager_chat,
        message="""
Task: Design a Boost converter controller that can maintain a Mean Absolute Error (MAE) of 0.5.

Instructions:

Control Objectives:
Agent 1: Define the specific control objectives for the Boost converter. Consider parameters such as voltage regulation, efficiency, and response time.

Model Selection:
Agent 2: Research and select an appropriate mathematical model for the Boost converter. Justify your choice based on accuracy and ease of implementation.

Control Algorithm Generation:
Agent 3: Develop a control algorithm to achieve the defined control objectives. Provide a step-by-step outline of the algorithm.

Control Parameter Optimization:
Agent 4: Optimize the control parameters to minimize the Mean Absolute Error (MAE) to 0.5. Describe the optimization techniques used.

Controller Performance Verification:
Agent 5: Verify the performance of the Boost converter controller. Include simulation results, error analysis, and any potential improvements.

Results Summary:
Agent 6: Summarize the design process, key findings, and overall performance of the Boost converter controller.

Coordination:
Each agent should collaborate and share their progress regularly. Ensure all design steps align with the main objective of maintaining a MAE of 0.5. Provide detailed documentation and justify each decision made during the design process.

Final Summary:
After completing all steps, provide a comprehensive summary of the Boost converter controller design process and results, highlighting key achievements and any challenges encountered.
        """
    )

if __name__ == "__main__":
    main()