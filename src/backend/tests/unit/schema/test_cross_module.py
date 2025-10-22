"""Unit tests for cross-module isinstance functionality.

These tests verify that isinstance checks work correctly when classes are
re-exported from different modules (e.g., wfx.schema.Message vs aiexec.schema.Message).
"""

from aiexec.schema import Data as AiexecData
from aiexec.schema import Message as AiexecMessage
from wfx.schema.data import Data as WfxData
from wfx.schema.message import Message as WfxMessage


class TestDuckTypingData:
    """Tests for duck-typing Data class across module boundaries."""

    def test_wfx_data_isinstance_aiexec_data(self):
        """Test that wfx.Data instance is recognized as aiexec.Data."""
        wfx_data = WfxData(data={"key": "value"})
        assert isinstance(wfx_data, AiexecData)

    def test_aiexec_data_isinstance_wfx_data(self):
        """Test that aiexec.Data instance is recognized as wfx.Data."""
        aiexec_data = AiexecData(data={"key": "value"})
        assert isinstance(aiexec_data, WfxData)

    def test_data_equality_across_modules(self):
        """Test that Data objects from different modules are equal."""
        wfx_data = WfxData(data={"key": "value"})
        aiexec_data = AiexecData(data={"key": "value"})
        assert wfx_data == aiexec_data

    def test_data_interchangeable_in_functions(self):
        """Test that Data from different modules work interchangeably."""

        def process_data(data: AiexecData) -> str:
            return data.get_text()

        wfx_data = WfxData(data={"text": "hello"})
        # Should not raise type error
        result = process_data(wfx_data)
        assert result == "hello"

    def test_data_model_dump_compatible(self):
        """Test that model_dump works across module boundaries."""
        wfx_data = WfxData(data={"key": "value"})
        aiexec_data = AiexecData(**wfx_data.model_dump())
        assert aiexec_data.data == {"key": "value"}


class TestDuckTypingMessage:
    """Tests for duck-typing Message class across module boundaries."""

    def test_wfx_message_isinstance_aiexec_message(self):
        """Test that wfx.Message instance is recognized as aiexec.Message."""
        wfx_message = WfxMessage(text="hello")
        assert isinstance(wfx_message, AiexecMessage)

    def test_aiexec_message_isinstance_wfx_message(self):
        """Test that aiexec.Message instance is recognized as wfx.Message."""
        aiexec_message = AiexecMessage(text="hello")
        assert isinstance(aiexec_message, WfxMessage)

    def test_message_equality_across_modules(self):
        """Test that Message objects from different modules are equal."""
        wfx_message = WfxMessage(text="hello", sender="user")
        aiexec_message = AiexecMessage(text="hello", sender="user")
        # Note: Direct equality might not work due to timestamps
        assert wfx_message.text == aiexec_message.text
        assert wfx_message.sender == aiexec_message.sender

    def test_message_interchangeable_in_functions(self):
        """Test that Message from different modules work interchangeably."""

        def process_message(msg: AiexecMessage) -> str:
            return f"Processed: {msg.text}"

        wfx_message = WfxMessage(text="hello")
        # Should not raise type error
        result = process_message(wfx_message)
        assert result == "Processed: hello"

    def test_message_model_dump_compatible(self):
        """Test that model_dump works across module boundaries."""
        wfx_message = WfxMessage(text="hello", sender="user")
        dump = wfx_message.model_dump()
        aiexec_message = AiexecMessage(**dump)
        assert aiexec_message.text == "hello"
        assert aiexec_message.sender == "user"

    def test_message_inherits_data_duck_typing(self):
        """Test that Message inherits duck-typing from Data."""
        wfx_message = WfxMessage(text="hello")
        # Should work as Data too
        assert isinstance(wfx_message, AiexecData)
        assert isinstance(wfx_message, WfxData)


class TestDuckTypingWithInputs:
    """Tests for duck-typing with input validation."""

    def test_message_input_accepts_wfx_message(self):
        """Test that MessageInput accepts wfx.Message."""
        from wfx.inputs.inputs import MessageInput

        wfx_message = WfxMessage(text="hello")
        msg_input = MessageInput(name="test", value=wfx_message)
        assert isinstance(msg_input.value, (WfxMessage, AiexecMessage))

    def test_message_input_converts_cross_module(self):
        """Test that MessageInput handles cross-module Messages."""
        from wfx.inputs.inputs import MessageInput

        aiexec_message = AiexecMessage(text="hello")
        msg_input = MessageInput(name="test", value=aiexec_message)
        # Should recognize it as a Message
        assert msg_input.value.text == "hello"

    def test_data_input_accepts_wfx_data(self):
        """Test that DataInput accepts wfx.Data."""
        from wfx.inputs.inputs import DataInput

        wfx_data = WfxData(data={"key": "value"})
        data_input = DataInput(name="test", value=wfx_data)
        assert data_input.value == wfx_data


class TestDuckTypingEdgeCases:
    """Tests for edge cases in cross-module isinstance checks."""

    def test_different_class_name_not_cross_module(self):
        """Test that objects with different class names are not recognized as cross-module compatible."""
        from wfx.schema.cross_module import CrossModuleModel

        class CustomModel(CrossModuleModel):
            value: str

        custom = CustomModel(value="test")
        # Should not be considered a Data
        assert not isinstance(custom, WfxData)
        assert not isinstance(custom, AiexecData)

    def test_non_pydantic_model_not_cross_module(self):
        """Test that non-Pydantic objects are not recognized as cross-module compatible."""

        class FakeData:
            def __init__(self):
                self.data = {}

        fake = FakeData()
        assert not isinstance(fake, WfxData)
        assert not isinstance(fake, AiexecData)

    def test_missing_fields_not_cross_module(self):
        """Test that objects missing required fields are not recognized as cross-module compatible."""
        from wfx.schema.cross_module import CrossModuleModel

        class PartialData(CrossModuleModel):
            text_key: str

        partial = PartialData(text_key="text")
        # Should not be considered a full Data (missing data field)
        assert not isinstance(partial, WfxData)
        assert not isinstance(partial, AiexecData)


class TestDuckTypingInputMixin:
    """Tests for cross-module isinstance checks in BaseInputMixin and subclasses."""

    def test_base_input_mixin_is_cross_module(self):
        """Test that BaseInputMixin uses CrossModuleModel."""
        from wfx.inputs.input_mixin import BaseInputMixin
        from wfx.schema.cross_module import CrossModuleModel

        # Check that BaseInputMixin inherits from CrossModuleModel
        assert issubclass(BaseInputMixin, CrossModuleModel)

    def test_input_subclasses_inherit_cross_module(self):
        """Test that all input types inherit cross-module support."""
        from wfx.inputs.inputs import (
            BoolInput,
            DataInput,
            FloatInput,
            IntInput,
            MessageInput,
            StrInput,
        )
        from wfx.schema.cross_module import CrossModuleModel

        for input_class in [StrInput, IntInput, FloatInput, BoolInput, DataInput, MessageInput]:
            assert issubclass(input_class, CrossModuleModel)

    def test_input_instances_work_across_modules(self):
        """Test that input instances work with duck-typing."""
        from wfx.inputs.inputs import MessageInput

        # Create with wfx Message
        wfx_msg = WfxMessage(text="hello")
        input1 = MessageInput(name="test1", value=wfx_msg)

        # Create with aiexec Message
        aiexec_msg = AiexecMessage(text="world")
        input2 = MessageInput(name="test2", value=aiexec_msg)

        # Both should work
        assert input1.value.text == "hello"
        assert input2.value.text == "world"
