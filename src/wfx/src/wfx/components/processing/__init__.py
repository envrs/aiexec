"""Processing components for AiExec."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from wfx.components._importing import import_mod

if TYPE_CHECKING:
    from wfx.components.processing.alter_metadata import AlterMetadataComponent
    from wfx.components.processing.batch_run import BatchRunComponent
    from wfx.components.processing.combine_text import CombineTextComponent
    from wfx.components.processing.converter import TypeConverterComponent
    from wfx.components.processing.create_data import CreateDataComponent
    from wfx.components.processing.data_operations import DataOperationsComponent
    from wfx.components.processing.data_to_dataframe import DataToDataFrameComponent
    from wfx.components.processing.dataframe_operations import DataFrameOperationsComponent
    from wfx.components.processing.dataframe_to_toolset import DataFrameToToolsetComponent
    from wfx.components.processing.dynamic_create_data import DynamicCreateDataComponent
    from wfx.components.processing.extract_key import ExtractDataKeyComponent
    from wfx.components.processing.filter_data import FilterDataComponent
    from wfx.components.processing.filter_data_values import DataFilterComponent
    from wfx.components.processing.json_cleaner import JSONCleaner
    from wfx.components.processing.lambda_filter import LambdaFilterComponent
    from wfx.components.processing.llm_router import LLMRouterComponent
    from wfx.components.processing.merge_data import MergeDataComponent
    from wfx.components.processing.message_to_data import MessageToDataComponent
    from wfx.components.processing.parse_data import ParseDataComponent
    from wfx.components.processing.parse_dataframe import ParseDataFrameComponent
    from wfx.components.processing.parse_json_data import ParseJSONDataComponent
    from wfx.components.processing.parser import ParserComponent
    from wfx.components.processing.prompt import PromptComponent
    from wfx.components.processing.python_repl_core import PythonREPLComponent
    from wfx.components.processing.regex import RegexExtractorComponent
    from wfx.components.processing.select_data import SelectDataComponent
    from wfx.components.processing.split_text import SplitTextComponent
    from wfx.components.processing.structured_output import StructuredOutputComponent
    from wfx.components.processing.update_data import UpdateDataComponent

_dynamic_imports = {
    "AlterMetadataComponent": "alter_metadata",
    "BatchRunComponent": "batch_run",
    "CombineTextComponent": "combine_text",
    "TypeConverterComponent": "converter",
    "CreateDataComponent": "create_data",
    "DataOperationsComponent": "data_operations",
    "DataToDataFrameComponent": "data_to_dataframe",
    "DataFrameOperationsComponent": "dataframe_operations",
    "DataFrameToToolsetComponent": "dataframe_to_toolset",
    "DynamicCreateDataComponent": "dynamic_create_data",
    "ExtractDataKeyComponent": "extract_key",
    "FilterDataComponent": "filter_data",
    "DataFilterComponent": "filter_data_values",
    "JSONCleaner": "json_cleaner",
    "LambdaFilterComponent": "lambda_filter",
    "LLMRouterComponent": "llm_router",
    "MergeDataComponent": "merge_data",
    "MessageToDataComponent": "message_to_data",
    "ParseDataComponent": "parse_data",
    "ParseDataFrameComponent": "parse_dataframe",
    "ParseJSONDataComponent": "parse_json_data",
    "ParserComponent": "parser",
    "PromptComponent": "prompt",
    "PythonREPLComponent": "python_repl_core",
    "RegexExtractorComponent": "regex",
    "SelectDataComponent": "select_data",
    "SplitTextComponent": "split_text",
    "StructuredOutputComponent": "structured_output",
    "UpdateDataComponent": "update_data",
}

__all__ = [
    "AlterMetadataComponent",
    "BatchRunComponent",
    "CombineTextComponent",
    "CreateDataComponent",
    "DataFilterComponent",
    "DataFrameOperationsComponent",
    "DataFrameToToolsetComponent",
    "DataOperationsComponent",
    "DataToDataFrameComponent",
    "DynamicCreateDataComponent",
    "ExtractDataKeyComponent",
    "FilterDataComponent",
    "JSONCleaner",
    "LLMRouterComponent",
    "LambdaFilterComponent",
    "MergeDataComponent",
    "MessageToDataComponent",
    "ParseDataComponent",
    "ParseDataFrameComponent",
    "ParseJSONDataComponent",
    "ParserComponent",
    "PromptComponent",
    "PythonREPLComponent",
    "RegexExtractorComponent",
    "SelectDataComponent",
    "SplitTextComponent",
    "StructuredOutputComponent",
    "TypeConverterComponent",
    "UpdateDataComponent",
]


def __getattr__(attr_name: str) -> Any:
    """Lazily import processing components on attribute access."""
    if attr_name not in _dynamic_imports:
        msg = f"module '{__name__}' has no attribute '{attr_name}'"
        raise AttributeError(msg)
    try:
        result = import_mod(attr_name, _dynamic_imports[attr_name], __spec__.parent)
    except (ModuleNotFoundError, ImportError, AttributeError) as e:
        msg = f"Could not import '{attr_name}' from '{__name__}': {e}"
        raise AttributeError(msg) from e
    globals()[attr_name] = result
    return result


def __dir__() -> list[str]:
    return list(__all__)
