"""Template models for validating and managing template parameters."""

import datetime
from datetime import datetime
from typing import ClassVar, Dict, List, Optional, Tuple, get_args

from pydantic import BaseModel, Field, TypeAdapter

from .params import DeviceID, FloorID, Timestamp


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
