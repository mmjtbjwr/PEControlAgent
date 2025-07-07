class ModelConfigTool:
    def __init__(self):
        self.models = {
            "boost_converter_controller": {
                "model_id": "boost_converter-2023",
                "address": "C:\\Users\\17338\\Desktop\\Multi agent interaction\\groupchat\\ControlVerificationAgent\\boost_converternopid.fmu",
                "description": "A model for controlling boost converters with MAE < 2",
                "parameters": {
                    "resistance": 15,
                    "inductance": 0.001,
                    "capacitance": 0.0006,
                    "input_voltage": 80,
                    "output_voltage": 160
                }
            },
        }
    
    def find_model(self, requirements):
        for model_id, model_info in self.models.items():
            if self._check_requirements(model_info['parameters'], requirements):
                return model_info
        return None

    def _check_requirements(self, model_params, requirements):
        return all(
            abs(model_params.get(key, 0) - value) < 1e-6
            for key, value in requirements.items()
        )