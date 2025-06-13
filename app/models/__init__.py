"""Init module for models."""

from .templates import (
    AvgMeasurementByDevice,
    AvgMeasurementByFloor,
    CountDevicesByStatus,
    CountDevicesOnFloor,
    CountRoomsOnFloor,
    CountTypeOnFloor,
    CountWindowOpeningsOnFloor,
    LatestMeasurementFromDevice,
    ListDeviceProperties,
    MaxMeasurementInBuilding,
    MinMeasurementInBuilding,
    WasWindowOpenedOnFloor,
    ListDevicesAndTypesOnFloor,
)

TEMPLATE_REGISTRY = {
    "avg_measurement_by_device": AvgMeasurementByDevice,
    "avg_measurement_by_floor": AvgMeasurementByFloor,
    "count_type_on_floor": CountTypeOnFloor,
    "count_devices_on_floor": CountDevicesOnFloor,
    "count_rooms_on_floor": CountRoomsOnFloor,
    "latest_measurement_from_device": LatestMeasurementFromDevice,
    "max_measurement_in_building": MaxMeasurementInBuilding,
    "min_measurement_in_building": MinMeasurementInBuilding,
    "count_devices_by_status": CountDevicesByStatus,
    "was_window_opened_on_floor": WasWindowOpenedOnFloor,
    "count_window_openings_on_floor": CountWindowOpeningsOnFloor,
    "list_device_properties": ListDeviceProperties,
    "list_devices_and_types_on_floor": ListDevicesAndTypesOnFloor,
}
