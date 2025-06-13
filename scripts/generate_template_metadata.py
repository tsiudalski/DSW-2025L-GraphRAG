import json
import os
import sys
from typing import Any, Dict, List, Type, get_origin, get_args, Optional
from enum import Enum

# Add the project root to the sys.path to allow imports from app.models
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models import TEMPLATE_REGISTRY  # Corrected import path
from app.models.templates import BaseTemplate
from app.models import params # Explicitly import params module
# No need to import individual param types if we're not hardcoding checks for them
# from app.models.params import (
#     DeviceID,
#     DeviceModel,
#     DeviceStatus,
#     FloorID,
#     Property,
#     PropertyType,
#     Timestamp,
# )

OUTPUT_FILE = "app/data/template_metadata.json"

def get_param_info(param_type: Type) -> str:
    """Extracts detailed information for custom parameter types dynamically.
    Relies on docstrings and Enum introspection.
    """
    # Handle Optional types first
    origin = get_origin(param_type)
    args = get_args(param_type)
    is_optional = False
    if origin is Optional and args:
        param_type = args[0] # Get the actual type inside Optional
        is_optional = True

    info_parts = []

    # 1. Get info from docstring of the custom type
    if hasattr(param_type, '__doc__') and param_type.__doc__:
        doc_lines = [line.strip() for line in param_type.__doc__.split('\n') if line.strip()]
        if doc_lines:
            info_parts.append(doc_lines[0]) # Use the first line of the docstring
            if len(doc_lines) > 1:
                info_parts.append(' '.join(doc_lines[1:])) # Append subsequent lines as general info

    # 2. Dynamically get possible values from Enum types
    if issubclass(param_type, Enum): # Check if the type itself is an Enum
        possible_values = ', '.join([f"'{m.value}'" for m in param_type])
        info_parts.append(f"Possible values: {possible_values}.")
    
    # Add regex patterns from custom param types if they have them via a property/classmethod
    if hasattr(param_type, 'regex_pattern') and isinstance(param_type.regex_pattern, str):
        info_parts.append(f"Matches regex: '{param_type.regex_pattern}'.")
    elif hasattr(param_type, 'DEVICE_REGEX') and hasattr(param_type.DEVICE_REGEX, 'pattern'):
        info_parts.append(f"Matches regex: '{param_type.DEVICE_REGEX.pattern}'.")
    elif hasattr(param_type, 'FLOOR_ID_REGEX') and hasattr(param_type.FLOOR_ID_REGEX, 'pattern'):
        info_parts.append(f"Matches regex: '{param_type.FLOOR_ID_REGEX.pattern}'.")
    elif hasattr(param_type, 'FULL_TIMESTAMP_REGEX') and hasattr(param_type.FULL_TIMESTAMP_REGEX, 'pattern'):
        info_parts.append(f"Matches regex: '{param_type.FULL_TIMESTAMP_REGEX.pattern}'.")

    final_info = '; '.join(filter(None, info_parts)).strip()
    if is_optional:
        final_info = f"(Optional) {final_info}"
    
    return final_info if final_info else str(getattr(param_type, '__name__', str(param_type))) # Fallback

def generate_template_metadata():
    """Generates template metadata from BaseTemplate subclasses."""
    metadata = []
    
    for template_name, template_class in TEMPLATE_REGISTRY.items():
        if issubclass(template_class, BaseTemplate) and template_class is not BaseTemplate:
            # required_params = [] # This will be removed
            param_details = {}

            for field_name, field_info in template_class.model_fields.items():
                # if field_info.is_required(): # This logic is no longer needed if required_parameters is removed
                #     required_params.append(field_name)
                
                description = field_info.description or (field_info.json_schema_extra and field_info.json_schema_extra.get("description")) or ""

                if not description:
                    param_details[field_name] = get_param_info(field_info.annotation)
                else:
                    param_details[field_name] = description

            metadata.append({
                "id": template_class.template_name,
                "file": f"{template_class.template_name}.rq.j2",
                "description": template_class.template_description,
                # "required_parameters": required_params, # This will be removed from the output
                "params": param_details # Renamed from parameter_descriptions
            })

    output_dir = os.path.dirname(OUTPUT_FILE)
    os.makedirs(output_dir, exist_ok=True)
    
    with open(OUTPUT_FILE, 'w') as f:
        json.dump({"templates": metadata}, f, indent=4)
    
    print(f"Generated template metadata and saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_template_metadata() 