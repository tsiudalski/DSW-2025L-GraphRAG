"""Template models for validating and managing template parameters."""

from typing import Any, ClassVar, Dict, List, Optional, Tuple

from pydantic import BaseModel, Field, ConfigDict, ValidationError

from .params import (
    DeviceID,
    DeviceModel,
    DeviceStatus,
    DeviceType,
    FloorID,
    Property,
    PropertyType,
    Timestamp,
)


class BaseTemplate(BaseModel):
    """Base class for validating template parameters."""

    template_name: ClassVar[str]
    template_description: ClassVar[str]

    model_config = ConfigDict(
        validate_assignment=True,
    )

    @property
    def template_path(self) -> str:
        """Return the path to the template file."""
        return f"{self.template_name}.rq.j2"

    @classmethod
    def get_fields(cls) -> List[str]:
        """Return a list of field names for the template."""
        return list(cls.__pydantic_fields__.keys())

    @classmethod
    def get_fields_info(cls) -> Dict[str, str]:
        """Return a dictionary of field names and their descriptions."""
        fields_info = {}
        for field_name, field in cls.__pydantic_fields__.items():
            fields_info[field_name] = field.description or ""
        return fields_info

    @classmethod
    def create_and_validate(
        cls, data: Dict[str, Any]
    ) -> Tuple[Optional["BaseTemplate"], Dict[str, str], List[str]]:
        """
        Attempts to create a validated model instance from input data.

        Returns a tuple containing:
        1. The validated model instance (or None if validation fails).
        2. A dictionary of validation errors keyed by field name.
        3. A list of any missing required fields.
        """
        errors: Dict[str, str] = {}
        missing_fields: List[str] = []

        try:
            instance = cls.model_validate(data)
            return instance, {}, []

        except ValidationError as e:
            for error in e.errors():
                field_name = str(error["loc"][0]) if error["loc"] else "__root__"

                if error["type"] == "missing":
                    missing_fields.append(field_name)
                else:
                    errors[field_name] = error["msg"]

            return None, errors, missing_fields


class AvgMeasurementByDevice(BaseTemplate):
    """Calculates the average of a specific numeric measurement for a single device over a given time period."""

    template_name: ClassVar[str] = "avg_measurement_by_device"
    template_description: ClassVar[str] = (
        "Calculates the average of a specific numeric measurement for a single device over a given time period."
    )

    device: Optional[DeviceID] = Field(
        None,
        description="The name of the device to query, possibe formats are R5_<number>, SmartSense_Multi_Sensor_<number>, Zigbee_Thermostat_<number>.",
    )
    property_type: Optional[PropertyType] = Field(
        None,
        description=f"The URI of the measurement type to average, possibe values are: {', '.join(Property._value2member_map_.keys())}.",
    )
    min_time: Optional[Timestamp] = Field(
        None, description="Start time in ISO format (YYYY-MM-DDTHH:MM:SS)."
    )
    max_time: Optional[Timestamp] = Field(
        None, description="End time in ISO format (YYYY-MM-DDTHH:MM:SS)."
    )


class AvgMeasurementByFloor(BaseTemplate):
    """Calculates the average of a specific numeric measurement for all devices on a given floor over a given time period."""

    template_name: ClassVar[str] = "avg_measurement_by_floor"
    template_description: ClassVar[str] = (
        "Calculates the average of a specific numeric measurement for all devices on a given floor over a given time period."
    )

    floor: Optional[FloorID] = Field(
        None,
        description="The name of the floor to query in format VL_floor_<number> (e.g., VL_floor_7).",
    )
    property_type: Optional[PropertyType] = Field(
        None,
        description=f"The URI of the measurement type to average, possibe values are: {', '.join(Property._value2member_map_.keys())}.",
    )
    min_time: Optional[Timestamp] = Field(
        None, description="Start time in ISO format (YYYY-MM-DDTHH:MM:SS)."
    )
    max_time: Optional[Timestamp] = Field(
        None, description="End time in ISO format (YYYY-MM-DDTHH:MM:SS)."
    )


class CountTypeOnFloor(BaseTemplate):
    """Counts the number of devices of a specific model/type that are located on a specific floor."""

    template_name: ClassVar[str] = "count_type_on_floor"
    template_description: ClassVar[str] = (
        "Counts the number of devices of a specific model/type that are located on a specific floor."
    )

    floor: Optional[FloorID] = Field(
        None,
        description="The name of the floor to query in format VL_floor_<number> (e.g., VL_floor_7).",
    )
    device_type: Optional[DeviceType] = Field(
        None,
        description=f"The string representing the device model/type, possible values are: {', '.join(DeviceModel._value2member_map_.keys())}.",
    )


class CountDevicesOnFloor(BaseTemplate):
    """Counts the total number of unique devices located on a specific floor."""

    template_name: ClassVar[str] = "count_devices_on_floor"
    template_description: ClassVar[str] = (
        "Counts the total number of unique devices located on a specific floor."
    )

    floor: Optional[FloorID] = Field(
        None,
        description="The name of the floor to query in format VL_floor_<number> (e.g., VL_floor_7).",
    )


class CountRoomsOnFloor(BaseTemplate):
    """Counts the total number of unique rooms located on a specific floor."""

    template_name: ClassVar[str] = "count_rooms_on_floor"
    template_description: ClassVar[str] = (
        "Counts the total number of unique rooms located on a specific floor."
    )

    floor: Optional[FloorID] = Field(
        None,
        description="The name of the floor to query in format VL_floor_<number> (e.g., VL_floor_7).",
    )


class LatestMeasurementFromDevice(BaseTemplate):
    """Fetches the single most recent value of a specific numeric measurement from a single device."""

    template_name: ClassVar[str] = "latest_measurement_from_device"
    template_description: ClassVar[str] = (
        "Fetches the single most recent value of a specific numeric measurement from a single device."
    )

    device: Optional[DeviceID] = Field(
        None,
        description="The name of the device to query, possibe formats are R5_<number>, SmartSense_Multi_Sensor_<number>, Zigbee_Thermostat_<number>.",
    )
    property_type: Optional[PropertyType] = Field(
        None,
        description=f"The URI of the measurement type to average, possibe values are: {', '.join(Property._value2member_map_.keys())}.",
    )


class MaxMeasurementInBuilding(BaseTemplate):
    """Finds the highest value ever recorded for a specific numeric measurement across all devices."""

    template_name: ClassVar[str] = "max_measurement_in_building"
    template_description: ClassVar[str] = (
        "Finds the highest value ever recorded for a specific numeric measurement across all devices."
    )

    property_type: Optional[PropertyType] = Field(
        None,
        description=f"The URI of the measurement type to average, possibe values are: {', '.join(Property._value2member_map_.keys())}.",
    )


class MinMeasurementInBuilding(BaseTemplate):
    """Finds the lowest value ever recorded for a specific numeric measurement across all devices."""

    template_name: ClassVar[str] = "min_measurement_in_building"
    template_description: ClassVar[str] = (
        "Finds the lowest value ever recorded for a specific numeric measurement across all devices."
    )

    property_type: Optional[PropertyType] = Field(
        None,
        description=f"The URI of the measurement type to average, possibe values are: {', '.join(Property._value2member_map_.keys())}.",
    )


class CountDevicesByStatus(BaseTemplate):
    """Counts the number of unique devices that reported a specific status within a given time period."""

    template_name: ClassVar[str] = "count_devices_by_status"
    template_description: ClassVar[str] = (
        "Counts the number of unique devices that reported a specific status within a given time period."
    )

    status: Optional[DeviceStatus] = Field(
        None, description="The device status to count ('active' or 'inactive')."
    )
    min_time: Optional[Timestamp] = Field(
        None, description="Start time in ISO format (YYYY-MM-DDTHH:MM:SS)."
    )
    max_time: Optional[Timestamp] = Field(
        None, description="End time in ISO format (YYYY-MM-DDTHH:MM:SS)."
    )


class WasWindowOpenedOnFloor(BaseTemplate):
    """Checks if a window (contact sensor) was opened on a floor during a time period."""

    template_name: ClassVar[str] = "was_window_opened_on_floor"
    template_description: ClassVar[str] = (
        "Checks if a window (contact sensor) was opened on a floor during a time period."
    )

    floor: Optional[FloorID] = Field(
        None,
        description="The name of the floor to query in format VL_floor_<number> (e.g., VL_floor_7).",
    )
    min_time: Optional[Timestamp] = Field(
        None, description="Start time in ISO format (YYYY-MM-DDTHH:MM:SS)."
    )
    max_time: Optional[Timestamp] = Field(
        None, description="End time in ISO format (YYYY-MM-DDTHH:MM:SS)."
    )


class CountWindowOpeningsOnFloor(BaseTemplate):
    """Counts how many times a window (contact sensor) was opened on a floor during a time period."""

    template_name: ClassVar[str] = "count_window_openings_on_floor"
    template_description: ClassVar[str] = (
        "Counts how many times a window (contact sensor) was opened on a floor during a time period."
    )

    floor: Optional[FloorID] = Field(
        None,
        description="The name of the floor to query in format VL_floor_<number> (e.g., VL_floor_7).",
    )
    min_time: Optional[Timestamp] = Field(
        None, description="Start time in ISO format (YYYY-MM-DDTHH:MM:SS)."
    )
    max_time: Optional[Timestamp] = Field(
        None, description="End time in ISO format (YYYY-MM-DDTHH:MM:SS)."
    )


class ListDeviceProperties(BaseTemplate):
    """Lists all measurement properties a given device is capable of, returned as a single comma-separated string."""

    template_name: ClassVar[str] = "list_device_properties"
    template_description: ClassVar[str] = (
        "Lists all measurement properties a given device is capable of, returned as a single comma-separated string."
    )

    device: Optional[DeviceID] = Field(
        None,
        description="The name of the device to query, possibe formats are R5_<number>, SmartSense_Multi_Sensor_<number>, Zigbee_Thermostat_<number>.",
    )


class ListDevicesAndTypesOnFloor(BaseTemplate):
    """Lists all devices and their types located on a specific floor."""

    # TODO: mark this template as multiple-row output, and handle differently
    template_name: ClassVar[str] = "list_devices_and_types_on_floor"
    template_description: ClassVar[str] = (
        "Lists all devices and their types located on a specific floor."
    )

    floor: Optional[FloorID] = Field(
        None,
        description="The name of the floor to query in format VL_floor_<number> (e.g., VL_floor_7).",
    )
