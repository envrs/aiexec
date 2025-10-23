# from wfx.field_typing import Data
from wfx.custom.custom_component.component import Component
from wfx.io import MessageTextInput, Output
from wfx.schema.data import Data


class CustomComponent(Component):
    display_name = "Custom Component"
    description = "Use as a template to create your own component."
    documentation: str = "https://aiexec-docs.khulnasoft.com/components-custom-components"
    icon = "code"
    name = "CustomComponent"

    inputs = [
        MessageTextInput(
            name="input_value",
            display_name="Input Value",
            info="This is a custom component Input",
            value="Hello, World!",
            tool_mode=True,
        ),
    ]

    outputs = [
        Output(display_name="Output", name="output", method="build_output"),
    ]

    def build_output(self) -> Data:
        data = Data(value=self.input_value)
        self.status = data
        return data
