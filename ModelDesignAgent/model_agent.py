from typing import Tuple


from autogen import ConversableAgent, register_function
from typing_extensions import Annotated
from pydantic import BaseModel, Field

import re
config_list = [
#    {"model": "gpt-4", "api_key": "", "tags": ["gpt4", "openai"]},
    {"model": "gpt-4o", "api_key": "sk-WgkJWaN31mlSdsVD1505D012F7E6481bA59dCe5a15114dF4", "base_url": "https://api.xiaoai.plus/v1"},
 #   {"model": "deepseek-coder", "api_key": "sk-9561e31d334a4b508dda74015096571a",
    # "base_url": "https://api.deepseek.com/v1"},
]

# config_list = [
#     {
#         "model": "qwen-max-0107", "api_key": " sk-33886890d3154f938ac26430eccb6ae8",
#   #      "model": "qwen2-72b-instruct","api_key": " sk-33886890d3154f938ac26430eccb6ae8",
#       #  "model": "llama3-70b-instruct", "api_key": " sk-33886890d3154f938ac26430eccb6ae8",
#      "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1"},
# ]


# 定义 PID 参数


# 调用 evaluate 方法

class ReadModelToolsInput(BaseModel):
    modelica_name: Annotated[str, Field(description="The Modelica model file name.")]

class WriteModelToolsInput(BaseModel):
    modelica_name: Annotated[str, Field(description="The Modelica model file name.")]
    modelica_code: Annotated[str, Field(description="The generated Modelica model file code.")]


def read_model_tools(input: Annotated[ReadModelToolsInput, "Input to read_model_tools."]) -> str:
    modelica_code = ""
    model_name = input.modelica_name
    if model_name == "boost converter" or model_name == "boost_converter" or model_name == "Boost Converter" or model_name == "BoostConverter":
        file_path = "boost_converter_temp.mo"
    with open(file_path, 'r') as f:
        modelica_code = f.read()
        return modelica_code

def write_model_tools(input: Annotated[WriteModelToolsInput, "Input to write_model_tools."]) -> str:
    modelica_name = input.modelica_name
    modelica_code = input.modelica_code
    file_path = f"{modelica_name}.mo"
    with open(file_path, 'w') as f:
        f.write(modelica_code)
    return file_path









# 创建 assistant 实例
assistant = ConversableAgent(
    name="Assistant",
    system_message = "# Character\n" \
        "You're an expert assistant specialized in creating and adjusting Modelica model files, with particular proficiency in the field of power electronics devices. Utilizing a toolbox called 'read_model_tools', you have a knack for inspecting, adjusting, and conceiving Modelica model files.\n" \
        "\n## Skills\n" \
        "### Skill 1: Decode Modelica model file\n" \
        "- Identify and decode the names of power electronics devices, for instance 'boost converter'. This is accomplished through the application of 'read_model_tools' to a specific Modelica model code, which depends on the device names in question.\n" \
        "\n### Skill 2: Customize parameters\n" \
        "- Create the Modelica model code by personalizing parameters of power electronics devices within the Modelica model code. This would include aspects like resistance (R), inductance (L), and capacitance (C). Please note that Resistance (R) should be configured at 10 ohms, Inductance (L) should be at 0.001 H, and Capacitance (C) at 0.001 F. Exclude these, the other strings would stay untouched.\n" \
        "\n### Skill 3: Generate new Modelica model files\n" \
        "- Exhibit your capability of manufacturing a novel Modelica model file equipped with the freshly constructed Modelica model code. This is achieved by applying the 'write_model_tools'. Do remember to note the model_name of the device in lowercase and substitute spaces with underscores, as in 'boost_converter'.\n" \
        "\nUtter the word 'TERMINATE' when you decide to wrap up.\n" \
        "\n## Constraints:\n" \
        "- Engage solely in topics surrounding Modelica.\n" \
        "- Reflect the language used by the user in all communications.\n" \
        "- Initiate the response directly with the optimized prompt.\n" \
        "- Verify that the final response is 'TERMINATE' after the task has been accomplished.",


# system_message = "# Character\n" \
#         "You're a skilled assistant specializing in generating and managing Modelica model files, with a soft spot for power electronics devices. Your expertise lies in utilizing 'read_model_tools' to scrutinize, adapt, and devise Modelica model files seamlessly.\n" \
#         "\n## Skills\n" \
#         "### Skill 1: Read and Analyze Modelica model code\n" \
#         "- Utilizing 'read_model_tools', identify and read the power electronics devices' names, such as 'boost converter', within the designated Modelica model code. Your eyes are extra peeled for names that stand out.\n" \
#         "\n### Skill 2: Modify and Personalize Parameters\n" \
#         "- Feel open to change the parameters of power electronic devices present in the Modelica model code. Tweak parameters like resistance (R), inductance (L), and capacitance (C). Let's say, a Resistance of 10 ohms, Inductance (L) at 0.001H, and Capacitance (C) at 0.001F sounds good, doesn't it? Just make sure to leave the rest of the Modelica model code as it is.\n" \
#         "\n### Skill 3: Craft New Modelica Model Files\n" \
#         "- Harness 'write_model_tools' to build new Modelica model files using the tailor-made Modelica model code. Remember, the model_name of the device should be in lowercase and connected by underscores (like 'boost_converter').\n" \
#         "\nWhen you want a wrap, just say 'TERMINATE'.\n" \
#         "\n## Constraints:\n" \
#         "- Keep the convo confined to Modelica.\n" \
#         "- Your output language should have a striking resemblance to the user's input language.\n" \
#         "- Hop into action by serving the optimized prompt as the first response.\n" \
#         "- When you're done, respectfully conclude with 'TERMINATE' as the final sign-off statement.",
    llm_config={"config_list": config_list},
)

# 创建 user_proxy 实例
user_proxy = ConversableAgent(
    name="User",
    llm_config=False,
    is_termination_msg=lambda msg: msg.get("content") is not None and "TERMINATE" in msg["content"],
    human_input_mode="NEVER",
)

#将PSOTool工具注册到两个代理
assistant.register_for_llm(name="read_model_tools", description="read model tools by power electronics devices' names")(read_model_tools)
user_proxy.register_for_execution(name="read_model_tools")(read_model_tools)
assistant.register_for_llm(name="read_model_tools", description="read model tools by power electronics devices' names")(read_model_tools)
user_proxy.register_for_execution(name="read_model_tools")(read_model_tools)
# 注册 PSOTool 到 assistant
register_function(
    read_model_tools,
    caller=assistant,  # 助手代理可以建议调用 PSOTool。
    executor=user_proxy,  # 用户代理代理可以执行 PSOTool 调用。
    name="read_model_tools",  # 默认情况下，函数名称用作工具名称。
    description="read model tools by power electronics devices' names",  # 工具的描述。
)

#将PSOTool工具注册到两个代理
assistant.register_for_llm(name="write_model_tools", description="write model tools by power electronics devices' names")(write_model_tools)
user_proxy.register_for_execution(name="write_model_tools")(write_model_tools)
assistant.register_for_llm(name="write_model_tools", description="write model tools by power electronics devices' names")(write_model_tools)
user_proxy.register_for_execution(name="write_model_tools")(write_model_tools)

# 注册 PSOTool 到 assistant
register_function(
    write_model_tools,
    caller=assistant,  # 助手代理可以建议调用 PSOTool。
    executor=user_proxy,  # 用户代理代理可以执行 PSOTool 调用。
    name="write_model_tools",  # 默认情况下，函数名称用作工具名称。
    description="write model tools by power electronics devices' names",  # 工具的描述。
)




questions = f"modify the parameters of the Boost converter are as follows:resistor (R)=20000,inductor (L)=0.002, and capacitor(C)=0.002 The regulated voltage is 170v  The input voltage is 85v\ "
# 调用 evaluate 方法
chat_result = user_proxy.initiate_chat(assistant, message=questions, max_turns=5)

# 打印对话结果
for message in chat_result.chat_history:
    print(f"{message['role']}: {message['content']}")
