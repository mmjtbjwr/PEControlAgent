import re
import os
from typing import Dict
from pydantic import BaseModel, Field
from mo2fmu import mo2fmu

class ModelInput(BaseModel):
    modelica_name: str = Field(..., description="The Modelica model file name.")
    parameters: Dict[str, float] = Field(..., description="The parameters to be modified.")

class WriteModelToolsInput(BaseModel):
    modelica_name: str
    modelica_code: str

def read_model_tools(modelica_name: str) -> str:
    base_path = r"C:\Users\17338\Desktop\Multi agent interaction\groupchat\ControlVerificationAgent\modelagent"
    file_path = os.path.join(base_path, "boost_converter_temp.mo")
    
    print(f"Attempting to read file: {file_path}")  # Debug print
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            print(f"Successfully read file: {file_path}")  # Debug print
            return content
    except FileNotFoundError:
        print(f"Warning: File {file_path} not found. Creating a new file with default content.")
        default_content = """
model boost_converter
  parameter Real R = 15.0 "Resistance (Ohm)";
  parameter Real L = 0.001 "Inductance (H)";
  parameter Real C = 0.0006 "Capacitance (F)";
  parameter Real Vin = 80.0 "Input voltage (V)";
  parameter Real Vout = 160.0 "Output voltage (V)";
  // Add other necessary components and equations here
equation
  // Add your equations here
end boost_converter;
"""
        with open(file_path, 'w') as f:
            f.write(default_content)
        print(f"Created new file: {file_path}")  # Debug print
        return default_content

def write_model_tools(input: WriteModelToolsInput) -> str:
    base_path = r"C:\Users\17338\Desktop\Multi agent interaction\groupchat\ControlVerificationAgent\modelagent"
    file_path = os.path.join(base_path, "boost_converter.mo")
    with open(file_path, 'w') as f:
        f.write(input.modelica_code)
    print(f"Written to file: {file_path}")  # Debug print
    return file_path

def generate_fmu(mo_file: str) -> str:
    base_path = r"C:\Users\17338\Desktop\Multi agent interaction\groupchat\ControlVerificationAgent\modelagent"
    fmu_name = os.path.splitext(mo_file)[0]  # 使用文件名作为模型名
    output_dir = base_path
    
    mo_path = os.path.join(base_path, mo_file)
    print(f"Generating FMU for: {mo_path}")  # Debug print
    
    result = mo2fmu(
        mo=mo_path,
        outdir=output_dir,
        fmumodelname=fmu_name,
        load=None,
        type='cs',
        version=None,
        dymola=r'C:\Program Files\Dymola 2023\bin64',
        dymolapath=r'C:\Program Files\Dymola 2023\bin64\dymola.exe',
        dymolaegg=r'C:\Program Files\Dymola 2023\Modelica\Library\python_interface\dymola.egg',
        verbose=True,
        force=True
    )
    
    if not result:
        raise Exception("FMU generation failed")
    
    fmu_path = os.path.join(output_dir, f"{fmu_name}.fmu")
    if not os.path.exists(fmu_path):
        raise Exception(f"FMU file not found at {fmu_path}")
    
    print(f"FMU generated: {fmu_path}")  # Debug print
    return fmu_path

def modify_model(input: ModelInput) -> str:
    print(f"Modifying model: {input.modelica_name}")  # Debug print
    modelica_code = read_model_tools(input.modelica_name)
    
    for param, value in input.parameters.items():
        modelica_code = re.sub(
            rf'({param}\s*=\s*)([0-9.e+-]+)',
            rf'\g<1>{value}',
            modelica_code
        )
    
    write_model_tools(WriteModelToolsInput(modelica_name="boost_converter.mo", modelica_code=modelica_code))
    
    try:
        # Generate FMU
        fmu_path = generate_fmu("boost_converter.mo")
        return f"Model modified successfully. New model: boost_converter.mo, FMU: {fmu_path}"
    except Exception as e:
        return f"Error generating FMU: {str(e)}"

# For testing purposes
if __name__ == "__main__":
    test_input = ModelInput(
        modelica_name="boost_converter.mo",
        parameters={
            "R": 15,
            "L": 0.001,
            "C": 0.0006,
            "Vin": 80,
            "Vout": 160
        }
    )
    result = modify_model(test_input)
    print(result)