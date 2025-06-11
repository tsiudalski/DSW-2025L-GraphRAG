"""Module with parameter validators."""

import re
from enum import Enum
from typing import Any

from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema


class DeviceID(str):
    """Custom string type for validating device IDs.

    Possible devices names:
     - ic:R5_{number}
     - ic:SmartSense_Multi_Sensor_{number}
     - ic:Zigbee_Thermostat_{number}
    """

    DEVICE_REGEX = re.compile(
        r"^ic:(R5_\d+|SmartSense_Multi_Sensor_\d+|Zigbee_Thermostat_\d+)$"
    )

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
            if not cls.DEVICE_REGEX.match(value):
                raise ValueError(
                    "Device ID must match one of the patterns: 'R5_<number>', 'SmartSense_Multi_Sensor_<number>', or 'Zigbee_Thermostat_<number>'"
                )
            return value

        return core_schema.no_info_after_validator_function(
            validate_device_id, handler(str)
        )


class FloorID(str):
    """Custom string type for validating floor IDs.

    Floor must match the pattern 'ic:VL_floor_{number}'.
    """

    FLOOR_ID_REGEX = re.compile(r"^ic:VL_floor_\d+$")
    FLOOR_ID_REGEX_WITHOUT_VL = re.compile(r"^floor_\d+$")

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        """Return a core schema for validating floor IDs."""

        def validate_floor_id(value: str) -> str:
            value = value.strip()
            if not value:
                raise ValueError("Floor ID cannot be empty")
            if value.isdigit():
                value = f"ic:VL_floor_{value}"
            elif cls.FLOOR_ID_REGEX_WITHOUT_VL.match(value):
                value = f"ic:VL_{value}"
            elif not value.startswith("ic:"):
                value = f"ic:{value}"
            if not cls.FLOOR_ID_REGEX.match(value):
                raise ValueError(
                    "Floor ID must match the pattern 'VL_floor_<number>' (e.g., 'VL_floor_7')"
                )
            return value

        return core_schema.no_info_after_validator_function(
            validate_floor_id, handler(str)
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
                return value
            elif cls.DATE_ONLY_REGEX.match(value):
                return f"{value}T00:00:00"
            else:
                raise ValueError(
                    "Timestamp must be in format YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS"
                )

        return core_schema.no_info_after_validator_function(
            validate_timestamp, handler(str)
        )


class Property(Enum):
    """Enum for valid property types."""

    BATTERY = "ic:BatteryLevel"
    CO2 = "ic:CO2Level"
    CONTACT = "ic:Contact"
    DEVICE_STATUS = "ic:DeviceStatus"
    RUNNING_TIME = "ic:RunningTime"
    TEMPERATURE_SETPOINT = "ic:thermostatHeatingSetpoint"
    HUMIDITY = "saref:Humidity"
    MOTION = "saref:Motion"
    OCCUPANCY = "saref:Occupancy"
    POWER = "saref:Power"
    TEMPERATURE = "saref:Temperature"


class PropertyType(str):
    """Custom string type for validating property types."""

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        """Return a core schema for validating property types."""

        def validate_property_type(value: str) -> str:
            normalized_value = value.strip().replace(" ", "").lower()
            for member in Property:
                if member.value.lower() in [
                    normalized_value,
                    f"ic:{normalized_value}",
                    f"saref:{normalized_value}",
                ]:
                    value = member.value
                    return value
            raise ValueError(
                f"Invalid property type '{value}'. Must be one of: {', '.join(Property._value2member_map_.keys())}"
            )

        return core_schema.no_info_after_validator_function(
            validate_property_type, handler(str)
        )


class DeviceModel(Enum):
    """Enum for valid device models."""

    AIRWITS = "Airwits"
    SMART_THINGS = "SmartThings"
    SENSOR_HUB = "Sensor Hub"


class DeviceType(str):
    """Custom string type for validating device types."""

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        """Return a core schema for validating device types."""

        def validate_device_type(value: str) -> str:
            normalized_value = value.strip().replace(" ", "").lower()
            for member in DeviceModel:
                if member.value.replace(" ", "").lower() == normalized_value:
                    value = member.value
                    return value
            raise ValueError(
                f"Invalid device type '{value}'. Must be one of: {', '.join(DeviceType._value2member_map_.keys())}"
            )

        return core_schema.no_info_after_validator_function(
            validate_device_type, handler(str)
        )


class DeviceStatus(str):
    """Custom string type for validating device status."""

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        """Return a core schema for validating device status."""

        def validate_device_status(value: str) -> str:
            value = value.strip()
            if value in ["0", "1"]:
                return value
            if value.lower() == "active":
                return "1"
            if value.lower() == "inactive":
                return "0"
            raise ValueError("Device status must be '1', '0', 'active', or 'inactive'")

        return core_schema.no_info_after_validator_function(
            validate_device_status, handler(str)
        )
