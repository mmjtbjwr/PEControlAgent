import autogen
from autogen import AssistantAgent, UserProxyAgent
from autogen.agentchat import GroupChat, GroupChatManager

# 定义乘法工具
def multiplication_tool(a: int, b: int) -> int:
    return a * b

# 配置API密钥
config_list = [
    {
       "model": "qwen2-72b-instruct", "api_key": "sk-4869c2bfac6e4fe292d4496929b968ef",
                "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1"
    }
]

# 创建函数调用配置
function_map = {
    "multiplication_tool": multiplication_tool
}

# 创建代理
def create_agent(name, system_message, is_human=False):
    if is_human:
        return UserProxyAgent(
            name=name,
            system_message=system_message,
            human_input_mode="NEVER",
            max_consecutive_auto_reply=10,
            code_execution_config={"work_dir": "coding", "use_docker": False},
            function_map=function_map,
            is_termination_msg=lambda x: x.get("content", "") and "对话结束" in x["content"]
        )
    else:
        return AssistantAgent(
            name=name,
            system_message=system_message,
            llm_config={
                "config_list": config_list,
                "temperature": 0,
                "functions": [
                    {
                        "name": "multiplication_tool",
                        "description": "执行两个数字的乘法运算",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "a": {"type": "integer", "description": "第一个乘数"},
                                "b": {"type": "integer", "description": "第二个乘数"}
                            },
                            "required": ["a", "b"]
                        }
                    }
                ]
            }
        )

leader = create_agent("Leader", "你是团队的领导。你需要分配任务给下属，并评估他们的工作。完成评估后，请说'任务完成'。")
subordinate1 = create_agent("Subordinate1", "你是一名下属。你需要完成领导分配的任务并报告结果。使用multiplication_tool函数来执行乘法运算。")
subordinate2 = create_agent("Subordinate2", "你是一名下属。你需要完成领导分配的任务并报告结果。使用multiplication_tool函数来执行乘法运算。")
human = create_agent("Human", "你是人类用户，负责启动对话并观察结果。当看到'任务完成'时，请说'对话结束'。", is_human=True)

# 创建GroupChat
groupchat = GroupChat(
    agents=[human, leader, subordinate1, subordinate2],
    messages=[],
    max_round=10,
    speaker_selection_method="round_robin",
    allow_repeat_speaker=False
)

# 创建GroupChatManager
manager = GroupChatManager(groupchat=groupchat, llm_config={"config_list": config_list})

# 初始化消息
initial_message = """请按以下步骤进行对话：
    1. Leader: 要求Subordinate1使用multiplication_tool完成10*10的计算任务
    2. Subordinate1: 使用multiplication_tool完成任务并报告结果
    3. Leader: 要求Subordinate2使用multiplication_tool完成20*20的计算任务
    4. Subordinate2: 使用multiplication_tool完成任务并报告结果
    5. Leader: 收集两个下属的计算结果，并对他们的工作进行评价。评价完成后，说"任务完成"。
    6. Human: 看到"任务完成"后，说"对话结束"。
    请确保每个步骤都由指定的角色完成。"""

# 启动对话
result = human.initiate_chat(
    manager,
    message=initial_message
)

# 检查结果
if result == "TERMINATE":
    print("对话已成功完成并终止。")
else:
    print("对话未正常终止。")