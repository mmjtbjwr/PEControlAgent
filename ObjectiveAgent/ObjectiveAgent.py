from typing import Tuple

from pyswarm import pso
from autogen import ConversableAgent, register_function
from typing_extensions import Annotated
from pydantic import BaseModel, Field

import re


config_list = [
    {"model": "qwen2-72b-instruct", "api_key": " sk-33886890d3154f938ac26430eccb6ae8",
     "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1"},
]



class ObjectiveDesignAgent(ConversableAgent):
    def __init__(self, name="Objective_Designer", **kwargs):
        system_message = "You are responsible for determining control objectives and performance indicators for the power electronics system."
        super().__init__(name=name, system_message=system_message, **kwargs)

    def set_objectives(self, system_requirements):
        objectives = self.generate_response(
            f"Based on these system requirements, determine appropriate control objectives: {system_requirements}")
        return objectives


objective_agent = ObjectiveDesignAgent(llm_config={"config_list": config_list})