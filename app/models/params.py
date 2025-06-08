"""Module with parameter validators."""

import re
from typing import Any

from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema


class DeviceID(str):
    """Custom string type for validating device IDs."""

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        
        """Return a core schema for validating device IDs."""
        def validate_device_id(value: str) -> str:
            value = value.strip()
            if not value:
                raise ValueError("Device ID cannot be empty")
            if not value.startswith("ic:"):
                value = f"ic:{value}"
            return value

        return core_schema.no_info_after_validator_function(
            validate_device_id,
            handler(str)

        )
    
class FloorID(str):
    """Custom string type for validating floor IDs."""

    FLOOR_ID_REGEX = re.compile(r"^ic:*floor\d+$")

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        """Return a core schema for validating floor IDs."""
        
        def validate_floor_id(value: str) -> str:
            value = value.strip()
            if not value:
                raise ValueError("Floor ID cannot be empty")
            if not value.startswith("ic:"):
                value = f"ic:{value}"
            if not cls.FLOOR_ID_REGEX.match(value):
                raise ValueError("Floor ID must match the pattern 'ic:floor<number>' (e.g., 'ic:floor1')")
            return value

        return core_schema.no_info_after_validator_function(
            validate_floor_id,
            handler(str)
        )

class Timestamp(str):
    """Custom string type for validating timestamps."""

    FULL_TIMESTAMP_REGEX = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$")
    DATE_ONLY_REGEX = re.compile(r"^\d{4}-\d{2}-\d{2}$")

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        """Return a core schema for validating timestamps."""

        def validate_timestamp(value: str) -> str:
            value = value.strip()
            if not value:
                raise ValueError("Timestamp cannot be empty")

            if cls.FULL_TIMESTAMP_REGEX.match(value):
                print(value)
                return value
            elif cls.DATE_ONLY_REGEX.match(value):
                print(value)
                return f"{value}T00:00:00"
            else:
                raise ValueError(
                    "Timestamp must be in format YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS"
                )

        return core_schema.no_info_after_validator_function(
            validate_timestamp,
            handler(str)
        )
