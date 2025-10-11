"""Helpers module for the wfx package.

This module automatically chooses between the full aiexec implementation
(when available) and the wfx implementation (when standalone).
"""

from wfx.utils.aiexec_utils import has_aiexec_memory

# Import the appropriate implementation
if has_aiexec_memory():
    try:
        # Import full aiexec implementation
        # Base Model
        from aiexec.helpers.base_model import (
            BaseModel,
            SchemaField,
            build_model_from_schema,
            coalesce_bool,
        )

        # Custom
        from aiexec.helpers.custom import (
            format_type,
        )

        # Data
        from aiexec.helpers.data import (
            clean_string,
            data_to_text,
            data_to_text_list,
            docs_to_data,
            safe_convert,
        )

        # Flow
        from aiexec.helpers.flow import (
            build_schema_from_inputs,
            get_arg_names,
            get_flow_inputs,
            list_flows,
            load_flow,
            run_flow,
        )
    except ImportError:
        # Fallback to wfx implementation if aiexec import fails
        # Base Model
        from wfx.helpers.base_model import (
            BaseModel,
            SchemaField,
            build_model_from_schema,
            coalesce_bool,
        )

        # Custom
        from wfx.helpers.custom import (
            format_type,
        )

        # Data
        from wfx.helpers.data import (
            clean_string,
            data_to_text,
            data_to_text_list,
            docs_to_data,
            safe_convert,
        )

        # Flow
        from wfx.helpers.flow import (
            build_schema_from_inputs,
            get_arg_names,
            get_flow_inputs,
            list_flows,
            load_flow,
            run_flow,
        )
else:
    # Use wfx implementation
    # Base Model
    from wfx.helpers.base_model import (
        BaseModel,
        SchemaField,
        build_model_from_schema,
        coalesce_bool,
    )

    # Custom
    from wfx.helpers.custom import (
        format_type,
    )

    # Data
    from wfx.helpers.data import (
        clean_string,
        data_to_text,
        data_to_text_list,
        docs_to_data,
        safe_convert,
    )

    # Flow
    from wfx.helpers.flow import (
        build_schema_from_inputs,
        get_arg_names,
        get_flow_inputs,
        list_flows,
        load_flow,
        run_flow,
    )

# Export the available functions
__all__ = [
    "BaseModel",
    "SchemaField",
    "build_model_from_schema",
    "build_schema_from_inputs",
    "clean_string",
    "coalesce_bool",
    "data_to_text",
    "data_to_text_list",
    "docs_to_data",
    "format_type",
    "get_arg_names",
    "get_flow_inputs",
    "list_flows",
    "load_flow",
    "run_flow",
    "safe_convert",
]
