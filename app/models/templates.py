"""Template models for validating and managing template parameters."""

from datetime import datetime
from typing import ClassVar, Dict, List, Optional, Tuple, get_args

from pydantic import BaseModel, Field, TypeAdapter

from .params import DeviceID, DeviceStatus, DeviceType, FloorID, PropertyType, Timestamp


class BaseTemplate(BaseModel):
    """Base class for validating template parameters."""

    template_name: ClassVar[str]
    template_description: ClassVar[str]

    @property
    def template_path(self) -> str:
        """Return the path to the template file."""
        return f"{self.template_name}.rq.j2"

    @classmethod
    def get_fields_info(cls) -> Dict[str, str]:
        """Return a dictionary of field names and their descriptions."""
        fields_info = {}
        for field_name, field in cls.__pydantic_fields__.items():
            fields_info[field_name] = field.description or ""
        return fields_info

    def validate_fields(self) -> Tuple[Dict[str, str], List[str]]:
        errors = {}
        missing_fields = []

        for field_name, field in self.__pydantic_fields__.items():
            value = getattr(self, field_name)
            if value is None:
                missing_fields.append(field_name)
            else:
                try:
                    # FIXME Assuming the Template model fields are of type Optional[T]
                    sub_types = [t for t in get_args(field.annotation) if t is not type(None)]
                    annotation = sub_types[0]
                    TypeAdapter(annotation).validate_python(value)
                except Exception as e:
                    msg = e.errors()[0].get("msg", str(e))
                    errors[field_name] = str(msg)

        return errors, missing_fields

    def is_valid(self) -> bool:
        errors, missing_fields = self.validate_fields()
        return not errors and not missing_fields

    def get_errors(self) -> Dict[str, str]:
        errors, _ = self.validate_fields()
        return errors

    def get_missing_fields(self) -> List[str]:
        _, missing_fields = self.validate_fields()
        return missing_fields


class Template1(BaseTemplate):
    """Template for retrieving average temperature measurements for a specific device within a time range."""

    template_name: ClassVar[str] = "template1"
    template_description: ClassVar[str] = "Retrieves average temperature measurements for a specific device within a time range"

    device: Optional[DeviceID] = Field(
        None,
        description="The URI of the device to query",
    )
    min_time: Optional[Timestamp] = Field(
        None,
        description="Start time in ISO format (YYYY-MM-DDTHH:MM:SS)",
    )
    max_time: Optional[Timestamp] = Field(
        None,
        description="End time in ISO format (YYYY-MM-DDTHH:MM:SS)",
    )

    def validate_fields(self):
        errors, missing_fields = super().validate_fields()

        invalid_fields = list(errors.keys()) + missing_fields
        if "min_time" not in invalid_fields and "max_time" not in invalid_fields:
            min_dt = datetime.fromisoformat(self.min_time)
            max_dt = datetime.fromisoformat(self.max_time)

            if min_dt > max_dt:
                errors["min_time"] = "min_time must be before max_time"
                errors["max_time"] = "max_time must be after min_time"
        return errors, missing_fields


class Template2(BaseTemplate):
    """Template for retrieving the number of devices of each type on a specific floor."""

    template_name: ClassVar[str] = "template2"
    template_description: ClassVar[str] = "Counts devices by type for a specific floor"

    floor: Optional[FloorID] = Field(
        None,
        description="The URI of the floor to query (format: ic:floor<number>, e.g., ic:VL_floor_7)",
    )


class AvgMeasurementByDevice(BaseTemplate):
    """Calculates the average of a specific numeric measurement for a single device over a given time period."""

    template_name: ClassVar[str] = "avg_measurement_by_device"
    template_description: ClassVar[str] = "Calculates the average of a specific numeric measurement for a single device over a given time period."

    device: Optional[DeviceID] = Field(None, description="The URI of the device to query.")
    property_type: Optional[PropertyType] = Field(
        None,
        description="The URI of the measurement type to average (e.g., saref:Temperature, ic:BatteryLevel, ic:CO2Level, saref:Humidity).",
    )
    min_time: Optional[Timestamp] = Field(None, description="Start time in ISO format (YYYY-MM-DDTHH:MM:SS).")
    max_time: Optional[Timestamp] = Field(None, description="End time in ISO format (YYYY-MM-DDTHH:MM:SS).")


class AvgMeasurementByFloor(BaseTemplate):
    """Calculates the average of a specific numeric measurement for all devices on a given floor over a given time period."""

    template_name: ClassVar[str] = "avg_measurement_by_floor"
    template_description: ClassVar[str] = "Calculates the average of a specific numeric measurement for all devices on a given floor over a given time period."

    floor: Optional[FloorID] = Field(None, description="The URI of the floor to query (e.g., ic:VL_floor_7).")
    property_type: Optional[PropertyType] = Field(
        None,
        description="The URI of the measurement type to average (e.g., saref:Temperature, ic:BatteryLevel, ic:CO2Level, saref:Humidity).",
    )
    min_time: Optional[Timestamp] = Field(None, description="Start time in ISO format (YYYY-MM-DDTHH:MM:SS).")
    max_time: Optional[Timestamp] = Field(None, description="End time in ISO format (YYYY-MM-DDTHH:MM:SS).")


class CountTypeOnFloor(BaseTemplate):
    """Counts the number of devices of a specific model/type that are located on a specific floor."""

    template_name: ClassVar[str] = "count_type_on_floor"
    template_description: ClassVar[str] = "Counts the number of devices of a specific model/type that are located on a specific floor."

    floor: Optional[FloorID] = Field(None, description="The URI of the floor to query (e.g., ic:VL_floor_7).")
    device_type: Optional[DeviceType] = Field(None, description="The string representing the device model/type (e.g., 'R5').")


class CountDevicesOnFloor(BaseTemplate):
    """Counts the total number of unique devices located on a specific floor."""

    template_name: ClassVar[str] = "count_devices_on_floor"
    template_description: ClassVar[str] = "Counts the total number of unique devices located on a specific floor."

    floor: Optional[FloorID] = Field(None, description="The URI of the floor to query (e.g., ic:VL_floor_7).")


class CountRoomsOnFloor(BaseTemplate):
    """Counts the total number of unique rooms located on a specific floor."""

    template_name: ClassVar[str] = "count_rooms_on_floor"
    template_description: ClassVar[str] = "Counts the total number of unique rooms located on a specific floor."

    floor: Optional[FloorID] = Field(None, description="The URI of the floor to query (e.g., ic:VL_floor_7).")


class LatestMeasurementFromDevice(BaseTemplate):
    """Fetches the single most recent value of a specific numeric measurement from a single device."""

    template_name: ClassVar[str] = "latest_measurement_from_device"
    template_description: ClassVar[str] = "Fetches the single most recent value of a specific numeric measurement from a single device."

    device: Optional[DeviceID] = Field(None, description="The URI of the device to query.")
    property_type: Optional[PropertyType] = Field(
        None,
        description="The URI of the measurement type to retrieve (e.g., saref:Temperature, ic:BatteryLevel, ic:CO2Level, saref:Humidity).",
    )


class MaxMeasurementInBuilding(BaseTemplate):
    """Finds the highest value ever recorded for a specific numeric measurement across all devices."""

    template_name: ClassVar[str] = "max_measurement_in_building"
    template_description: ClassVar[str] = "Finds the highest value ever recorded for a specific numeric measurement across all devices."

    property_type: Optional[PropertyType] = Field(
        None,
        description="The URI of the measurement type to find the maximum of (e.g., saref:Temperature, ic:BatteryLevel, ic:CO2Level, saref:Humidity).",
    )


class MinMeasurementInBuilding(BaseTemplate):
    """Finds the lowest value ever recorded for a specific numeric measurement across all devices."""

    template_name: ClassVar[str] = "min_measurement_in_building"
    template_description: ClassVar[str] = "Finds the lowest value ever recorded for a specific numeric measurement across all devices."

    property_type: Optional[PropertyType] = Field(
        None,
        description="The URI of the measurement type to find the minimum of (e.g., saref:Temperature, ic:BatteryLevel, ic:CO2Level, saref:Humidity).",
    )


class CountDevicesByStatus(BaseTemplate):
    """Counts the number of unique devices that reported a specific status within a given time period."""

    template_name: ClassVar[str] = "count_devices_by_status"
    template_description: ClassVar[str] = "Counts the number of unique devices that reported a specific status within a given time period."

    status: Optional[DeviceStatus] = Field(None, description="The device status to count ('active' or 'inactive').")
    min_time: Optional[Timestamp] = Field(None, description="Start time in ISO format (YYYY-MM-DDTHH:MM:SS).")
    max_time: Optional[Timestamp] = Field(None, description="End time in ISO format (YYYY-MM-DDTHH:MM:SS).")


class WasWindowOpenedOnFloor(BaseTemplate):
    """Checks if a window (contact sensor) was opened on a floor during a time period."""

    template_name: ClassVar[str] = "was_window_opened_on_floor"
    template_description: ClassVar[str] = "Checks if a window (contact sensor) was opened on a floor during a time period."

    floor: Optional[FloorID] = Field(None, description="The URI of the floor to query (e.g., ic:VL_floor_7).")
    min_time: Optional[Timestamp] = Field(None, description="Start time in ISO format (YYYY-MM-DDTHH:MM:SS).")
    max_time: Optional[Timestamp] = Field(None, description="End time in ISO format (YYYY-MM-DDTHH:MM:SS).")


class CountWindowOpeningsOnFloor(BaseTemplate):
    """Counts how many times a window (contact sensor) was opened on a floor during a time period."""

    template_name: ClassVar[str] = "count_window_openings_on_floor"
    template_description: ClassVar[str] = "Counts how many times a window (contact sensor) was opened on a floor during a time period."

    floor: Optional[FloorID] = Field(None, description="The URI of the floor to query (e.g., ic:VL_floor_7).")
    min_time: Optional[Timestamp] = Field(None, description="Start time in ISO format (YYYY-MM-DDTHH:MM:SS).")
    max_time: Optional[Timestamp] = Field(None, description="End time in ISO format (YYYY-MM-DDTHH:MM:SS).")


class ListDeviceProperties(BaseTemplate):
    """Lists all measurement properties a given device is capable of, returned as a single comma-separated string."""

    template_name: ClassVar[str] = "list_device_properties"
    template_description: ClassVar[str] = "Lists all measurement properties a given device is capable of, returned as a single comma-separated string."

    device: Optional[DeviceID] = Field(None, description="The URI of the device to query.")
