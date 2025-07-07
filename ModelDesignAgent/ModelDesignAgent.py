from autogen import ConversableAgent, register_function
from typing_extensions import Annotated
from pydantic import BaseModel, Field


class ReadModelToolsInput(BaseModel):
    modelica_name: Annotated[str, Field(description="The Modelica model file name.")]


class WriteModelToolsInput(BaseModel):
    modelica_name: Annotated[str, Field(description="The Modelica model file name.")]
    modelica_code: Annotated[str, Field(description="The generated Modelica model file code.")]


class ModelDesignAgent(ConversableAgent):
    def __init__(self, name="Model_Designer", **kwargs):
        system_message = """# Character
You're an expert assistant specialized in creating and adjusting Modelica model files, with particular proficiency in the field of power electronics devices. Utilizing toolboxes called 'read_model_tools' and 'write_model_tools', you have a knack for inspecting, adjusting, and conceiving Modelica model files.

## Skills
### Skill 1: Decode Modelica model file
- Identify and decode the names of power electronics devices, for instance 'boost converter'. This is accomplished through the application of 'read_model_tools' to a specific Modelica model code, which depends on the device names in question.

### Skill 2: Customize parameters
- Create the Modelica model code by personalizing parameters of power electronics devices within the Modelica model code. This would include aspects like resistance (R), inductance (L), and capacitance (C). Please note that parameters should be configured based on the user's requirements. Exclude these, the other strings would stay untouched.

### Skill 3: Generate new Modelica model files
- Exhibit your capability of manufacturing a novel Modelica model file equipped with the freshly constructed Modelica model code. This is achieved by applying the 'write_model_tools'. Do remember to note the model_name of the device in lowercase and substitute spaces with underscores, as in 'boost_converter'.

Utter the word 'TERMINATE' when you decide to wrap up.

## Constraints:
- Engage solely in topics surrounding Modelica.
- Reflect the language used by the user in all communications.
- Initiate the response directly with the optimized prompt.
- Verify that the final response is 'TERMINATE' after the task has been accomplished."""

        super().__init__(name=name, system_message=system_message, **kwargs)

        self.register_for_llm(name="read_model_tools",
                              description="read model tools by power electronics devices' names")(self.read_model_tools)
        self.register_for_llm(name="write_model_tools",
                              description="write model tools by power electronics devices' names")(
            self.write_model_tools)

    def read_model_tools(self, input: Annotated[ReadModelToolsInput, "Input to read_model_tools."]) -> str:
        modelica_code = ""
        model_name = input.modelica_name.lower().replace(" ", "_")
        if model_name == "boost_converter":
            file_path = "boost_converter_temp.mo"
        else:
            file_path = f"{model_name}.mo"

        try:
            with open(file_path, 'r') as f:
                modelica_code = f.read()
        except FileNotFoundError:
            return f"Error: File {file_path} not found."

        return modelica_code

    def write_model_tools(self, input: Annotated[WriteModelToolsInput, "Input to write_model_tools."]) -> str:
        modelica_name = input.modelica_name.lower().replace(" ", "_")
        modelica_code = input.modelica_code
        file_path = f"{modelica_name}.mo"

        try:
            with open(file_path, 'w') as f:
                f.write(modelica_code)
        except IOError:
            return f"Error: Unable to write to file {file_path}."

        return file_path

    def select_model(self, device_type, requirements):
        # 读取模型
        read_input = ReadModelToolsInput(modelica_name=device_type)
        modelica_code = self.read_model_tools(read_input)

        # 修改参数
        modified_code = self.modify_parameters(modelica_code, requirements)

        # 写入新模型
        write_input = WriteModelToolsInput(modelica_name=device_type, modelica_code=modified_code)
        new_file_path = self.write_model_tools(write_input)

        return new_file_path

    def modify_parameters(self, modelica_code, requirements):
        # 这里需要实现参数修改的逻辑
        # 例如，可以使用正则表达式来查找和替换特定的参数值
        # 这个方法的具体实现取决于Modelica模型的结构和要修改的参数

        # 这里只是一个示例，实际实现可能需要更复杂的逻辑
        for param, value in requirements.items():
            modelica_code = modelica_code.replace(f"{param}=.*", f"{param}={value}")

        return modelica_code


# 使用示例
config_list = [
    {"model": "gpt-4o", "api_key": "sk-WgkJWaN31mlSdsVD1505D012F7E6481bA59dCe5a15114dF4",
     "base_url": "https://api.xiaoai.plus/v1"},
]

model_agent = ModelDesignAgent(llm_config={"config_list": config_list})

# 使用示例
device_type = "boost_converter"
requirements = {
    "R": "20000",
    "L": "0.002",
    "C": "0.002",
    "regulated_voltage": "170",
    "input_voltage": "85"
}

new_model_path = model_agent.select_model(device_type, requirements)
print(f"New model created at: {new_model_path}")