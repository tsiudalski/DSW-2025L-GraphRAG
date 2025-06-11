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
        """
        Calculates the average (mean) of a specific numeric measurement for a given device (sensor) over a given time period.
        Example: 'What was the average <measurement> on <device> during the first week of <month> <year>?'
        Example: 'What was the average <measurement> level reported by <device> in the last month?'
        """
    )

    device: Optional[DeviceID] = Field(
        None,
        description="The name of the device to query, possible formats are R5_<number>, SmartSense_Multi_Sensor_<number>, Zigbee_Thermostat_<number>.",
    )
    property_type: Optional[PropertyType] = Field(
        None,
        description=f"The URI identifier of the measurement type to average, possible values are: {', '.join(Property._value2member_map_.keys())}.",
    )
    min_time: Optional[Timestamp] = Field(
        None, description="Starting time of the queried period in ISO format (YYYY-MM-DDTHH:MM:SS)."
    )
    max_time: Optional[Timestamp] = Field(
        None, description="Ending time of the queried period in ISO format (YYYY-MM-DDTHH:MM:SS)."
    )


class AvgMeasurementByFloor(BaseTemplate):
    """Calculates the average of a specific numeric measurement for all devices on a given floor over a given time period."""

    template_name: ClassVar[str] = "avg_measurement_by_floor"
    template_description: ClassVar[str] = (
        """
        Calculates the average (mean) of a specific numeric measurement for all devices on a given floor over a given time period.
        Example: 'What was the average <measurement> level on the <floor> during the first week of <month> <year>?'
        Example: 'What was the mean <measurement> level reported by devices on the <floor> in the last month?'
        """
    )

    floor: Optional[FloorID] = Field(
        None,
        description="The name of the floor to query in format VL_floor_<number> (e.g., VL_floor_7).",
    )
    property_type: Optional[PropertyType] = Field(
        None,
        description=f"The URI identifier of the measurement type to average, possible values are: {', '.join(Property._value2member_map_.keys())}.",
    )
    min_time: Optional[Timestamp] = Field(
        None, description="Starting time of the queried period in ISO format (YYYY-MM-DDTHH:MM:SS)."
    )
    max_time: Optional[Timestamp] = Field(
        None, description="Ending time of the queried period in ISO format (YYYY-MM-DDTHH:MM:SS)."
    )


class CountTypeOnFloor(BaseTemplate):
    """Counts the number of devices of a specific model/type that are located on a specific floor."""

    template_name: ClassVar[str] = "count_type_on_floor"
    template_description: ClassVar[str] = (
        """
        Counts the number of devices of a specific model/type that are located on a specific floor.
        Example: 'How many <device_type> devices are located on the <floor>?'
        Example: 'What is the total number of <device_type> devices on the <floor>?'
        """
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
        """
        Counts the total number of unique devices located on a specific floor.
        Example: 'How many devices are located on the <floor>?'
        Example: 'What is the total number of devices on the <floor>?'
        """
    )

    floor: Optional[FloorID] = Field(
        None,
        description="The name of the floor to query in format VL_floor_<number> (e.g., VL_floor_7).",
    )


class CountRoomsOnFloor(BaseTemplate):
    """Counts the total number of unique rooms located on a specific floor."""

    template_name: ClassVar[str] = "count_rooms_on_floor"
    template_description: ClassVar[str] = (
        """
        Counts the total number of unique rooms located on a specific floor.
        Example: 'How many rooms are located on the <floor>?'
        Example: 'What is the total number of rooms on the <floor>?'
        """
    )

    floor: Optional[FloorID] = Field(
        None,
        description="The name of the floor to query in format VL_floor_<number> (e.g., VL_floor_7).",
    )


class LatestMeasurementFromDevice(BaseTemplate):
    """Fetches the single most recent value of a specific numeric measurement from a single device."""

    template_name: ClassVar[str] = "latest_measurement_from_device"
    template_description: ClassVar[str] = (
        """
        Fetches the last (latest, most recent) value of a specific numeric measurement made by a given device.
        Example: 'What was the last reported <measurement> level from <device>?'
        Example: 'What is the latest reading of <measurement> reported by <device>?'
        """
    )

    device: Optional[DeviceID] = Field(
        None,
        description="The name of the device for which to fetch the last reported measurement, possible formats are R5_<number>, SmartSense_Multi_Sensor_<number>, Zigbee_Thermostat_<number>.",
    )
    property_type: Optional[PropertyType] = Field(
        None,
        description=f"The URI identifier of the measurement type to fetch, possible values are: {', '.join(Property._value2member_map_.keys())}.",
    )


class MaxMeasurementInBuilding(BaseTemplate):
    """Finds the highest value ever recorded for a specific numeric measurement across all devices."""

    template_name: ClassVar[str] = "max_measurement_in_building"
    template_description: ClassVar[str] = (
        """
        Finds the highest (top, maximum) value ever recorded (in all history) for a specific numeric measurement across all devices.
        Example: 'What was the highest <measurement> level ever recorded in the building?'
        Example: 'What is the maximum <measurement> level ever reported by any device?'
        """
    )

    property_type: Optional[PropertyType] = Field(
        None,
        description=f"The URI identifier of the measurement type to fetch, possible values are: {', '.join(Property._value2member_map_.keys())}.",
    )


class MinMeasurementInBuilding(BaseTemplate):
    """Finds the lowest value ever recorded for a specific numeric measurement across all devices."""

    template_name: ClassVar[str] = "min_measurement_in_building"
    template_description: ClassVar[str] = (
        """
        Finds the lowest (bottom, minimum) value ever recorded (in all history) for a specific numeric measurement across all devices.
        Example: 'What was the lowest <measurement> level ever recorded in the building?'
        Example: 'What is the minimum <measurement> level ever reported by any device?'
        """
    )

    property_type: Optional[PropertyType] = Field(
        None,
        description=f"The URI identifier of the measurement type to fetch, possible values are: {', '.join(Property._value2member_map_.keys())}.",
    )


class CountDevicesByStatus(BaseTemplate):
    """Counts the number of unique devices that reported a specific status within a given time period."""

    template_name: ClassVar[str] = "count_devices_by_status"
    template_description: ClassVar[str] = (
        """
        Counts the number of unique devices that reported a specific status within a given time period.
        Example: 'How many devices are currently active?'
        Example: 'How many devices were inactive during the last week?'
        """
    )

    status: Optional[DeviceStatus] = Field(
        None, description="The device status to count ('active' or 'inactive')."
    )
    min_time: Optional[Timestamp] = Field(
        None, description="Starting time of the queried period in ISO format (YYYY-MM-DDTHH:MM:SS)."
    )
    max_time: Optional[Timestamp] = Field(
        None, description="Ending time of the queried period in ISO format (YYYY-MM-DDTHH:MM:SS)."
    )


class WasWindowOpenedOnFloor(BaseTemplate):
    """Checks if a window (contact sensor) was opened on a floor during a time period."""

    template_name: ClassVar[str] = "was_window_opened_on_floor"
    template_description: ClassVar[str] = (
        """
        Checks if a window (contact sensor) was opened on a <floor> during a time period.
        Example: 'Was a window opened on the <floor> during the last week of <month> <year>?'
        """
    )

    floor: Optional[FloorID] = Field(
        None,
        description="The name of the floor to query in format VL_floor_<number> (e.g., VL_floor_7).",
    )
    min_time: Optional[Timestamp] = Field(
        None, description="Starting time of the queried period in ISO format (YYYY-MM-DDTHH:MM:SS)."
    )
    max_time: Optional[Timestamp] = Field(
        None, description="Ending time of the queried period in ISO format (YYYY-MM-DDTHH:MM:SS)."
    )


class CountWindowOpeningsOnFloor(BaseTemplate):
    """Counts how many times a window (contact sensor) was opened on a floor during a time period."""

    template_name: ClassVar[str] = "count_window_openings_on_floor"
    template_description: ClassVar[str] = (
        """
        Counts how many times a window (contact sensor) was opened on a floor during a time period.
        Example: 'How many times was a window opened on the <floor> during <month> of <year>?'
        Example: 'Count the number of window openings on the <floor> in the last week.'
        """
    )

    floor: Optional[FloorID] = Field(
        None,
        description="The name of the floor to query in format VL_floor_<number> (e.g., VL_floor_7).",
    )
    min_time: Optional[Timestamp] = Field(
        None, description="Starting time of the queried period in ISO format (YYYY-MM-DDTHH:MM:SS)."
    )
    max_time: Optional[Timestamp] = Field(
        None, description="Ending time of the queried period in ISO format (YYYY-MM-DDTHH:MM:SS)."
    )


class ListDeviceProperties(BaseTemplate):
    """Lists all measurement properties a given device is capable of, returned as a single comma-separated string."""

    template_name: ClassVar[str] = "list_device_properties"
    template_description: ClassVar[str] = (
        """
        Lists (enumerates) all measurement properties a given device is capable of, returned as a single comma-separated string.
        Example: 'What properties does the <device> support?'
        Example: 'What measurements can I get from <device>?'
        """
    )

    device: Optional[DeviceID] = Field(
        None,
        description="The name of the device to query, possible formats are R5_<number>, SmartSense_Multi_Sensor_<number>, Zigbee_Thermostat_<number>.",
    )

class ListDevicesAndTypesOnFloor(BaseTemplate):
    """Lists all devices and their types located on a specific floor."""
    # TODO: mark this template as multiple-row output, and handle differently
    template_name: ClassVar[str] = "list_devices_and_types_on_floor"
    template_description: ClassVar[str] = (
        """
        Lists all devices and their types located on a specific floor.
        Example: 'What devices are located on the <floor>?'
        Example: 'List all devices and their types on the <floor>.'
        """
    )

    floor: Optional[FloorID] = Field(
        None,
        description="The name of the floor to query in format VL_floor_<number> (e.g., VL_floor_7).",
    )
