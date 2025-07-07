import os
from typing import Dict, Optional
from model_agent import modify_model, ModelInput

class ModelConfigTool:
    def __init__(self):
        self.models = {
            "boost_converter_controller": {
                "model_id": "boost_converter-2023",
                "template_file": "C:\\Users\\17338\\Desktop\\Multi agent interaction\\groupchat\\ControlVerificationAgent\\modelagent\\boost_converter_temp.mo",
                "description": "A model for controlling boost converters with MAE < 2",
                "parameters": {
                    "R": 15,
                    "L": 0.001,
                    "C": 0.0006,
                    "Vin": 80,
                    "Vout": 160
                }
            },
        }
    
    def find_or_create_model(self, requirements: Dict[str, float]) -> Optional[Dict]:
        for model_id, model_info in self.models.items():
            if self._check_requirements(model_info['parameters'], requirements):
                return model_info
        
        # If no matching model found, modify the template
        return self._modify_model(requirements)

    def _check_requirements(self, model_params: Dict[str, float], requirements: Dict[str, float]) -> bool:
        return all(
            abs(model_params.get(key, 0) - value) < 1e-6
            for key, value in requirements.items()
        )

    def _modify_model(self, requirements: Dict[str, float]) -> Optional[Dict]:
        template_model = self.models["boost_converter_controller"]  # Assuming we always start with this template
        
        input_data = ModelInput(
            modelica_name=os.path.basename(template_model["template_file"]),
            parameters={
                "R": requirements["resistance"],
                "L": requirements["inductance"],
                "C": requirements["capacitance"],
                "Vin": requirements["input_voltage"],
                "Vout": requirements["output_voltage"]
            }
        )
        
        modification_result = modify_model(input_data)
        
        if "Error" in modification_result or "FMU:" not in modification_result:
            print(f"Error modifying model: {modification_result}")
            return None
        
        try:
            new_model_name, fmu_path = modification_result.split(", FMU: ")
            new_model_name = new_model_name.split(": ")[1]
        except ValueError:
            print(f"Unexpected modification result format: {modification_result}")
            return None
        
        return {
            "model_id": f"modified-{template_model['model_id']}",
            "address": fmu_path,
            "description": f"Modified model based on {template_model['description']}",
            "parameters": input_data.parameters
        }