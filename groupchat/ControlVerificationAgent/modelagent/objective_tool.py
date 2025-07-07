class ObjectiveTool:
    @staticmethod
    def get_control_objectives():
        return {
            "control_objective": "Output voltage of 160V",
            "constraints": [
                "Overshoot less than 8%",
                "Steady-state error less than 2%",
                "Settling time less than 0.5s"
            ]
        }