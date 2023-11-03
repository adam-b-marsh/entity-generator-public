"""Contains the EntityValueUtility class."""

from typing import Optional
from datetime import datetime
import calendar
from crm_entity_generator.protos import (
    FormattedGuid,
    FormattedTimestamp,
    FormattedStr,
    FormattedInt,
    Timestamp,
    WorkRegion,
    CreationSource,
)


class EntityValueUtility:
    """Class used to get/set entity values and format their values correctly.

    :param date_format_string: correct method to format dates when passing them to the CRM API
    :type: str
    """

    date_format_string = "%Y-%m-%dT%H:%M:%SZ"

    @classmethod
    def set_entity_attribute(
        cls, entity, field_name, field_type, new_value, formatted_value
    ):
        """Set an entity value with of form "set_type_{obj_type}."""
        try:
            # grab the function from this class that were going to use to set the value
            set_function = getattr(cls, f"set_type_{field_type}")
        except AttributeError as e:
            raise TypeError(
                f"Set function for field type: '{field_type}' has not been created"
            ) from e  # noqa E501
        # call the function we grabbed to set value and return its result
        return set_function(entity, field_name, new_value, formatted_value)

    @classmethod
    def get_ultimate_value(
        cls, entity, field_name, field_type, for_search=False
    ) -> Optional[str]:
        """Lookup a method with of form "from_type_{obj_type}."""
        entity_field_obj = getattr(entity, field_name)
        try:
            # grab the function from this class that were going to use to get the value
            format_function = getattr(cls, f"from_type_{field_type}")
        except AttributeError as e:
            raise TypeError(
                f"Get function for field type: '{field_type}' has not been created"
            ) from e  # noqa E501
        # call the function we grabbed to get value and return its result
        value = format_function(entity_field_obj)
        # edge case: wrap strings in single-quotes if value is for search
        if for_search and field_type == "str":
            value = f"'{value}'"
        return value

    @classmethod
    def from_type_bool(cls, entity_field_obj) -> bool:
        """Get value from a boolean."""
        return True if entity_field_obj else False

    @classmethod
    def set_type_bool(cls, entity, field_name, new_value, formatted_value):
        """Set value of a boolean."""
        setattr(entity, field_name, new_value == "True")
        return entity

    @classmethod
    def from_type_str(cls, entity_field_obj) -> str:
        """Get value from str."""
        # wrap string in outer single-quotes if going into url query param
        return entity_field_obj

    @classmethod
    def set_type_str(cls, entity, field_name, new_value, formatted_value):
        """Set value of str."""
        setattr(entity, field_name, new_value)
        return entity

    @classmethod
    def from_type_int(cls, entity_field_obj) -> int:
        """Get value of int."""
        return entity_field_obj

    @classmethod
    def set_type_int(cls, entity, field_name, new_value, formatted_value):
        """Set value of int."""
        setattr(entity, field_name, int(new_value))
        return entity

    @classmethod
    def from_type_float(cls, entity_field_obj) -> float:
        """Get value of float."""
        return entity_field_obj

    @classmethod
    def set_type_float(cls, entity, field_name, new_value, formatted_value):
        """Set value of float."""
        setattr(entity, field_name, float(new_value))
        return entity

    @classmethod
    def from_type_FormattedGuid(cls, entity_field_obj) -> str:
        """Get value of FormattedGuid."""
        return entity_field_obj.value

    @classmethod
    def set_type_FormattedGuid(cls, entity, field_name, new_value, formatted_value):
        """Set value of FormattedGuid."""
        guid = FormattedGuid(value=new_value, formatted_value=formatted_value)
        getattr(entity, field_name).CopyFrom(guid)
        return entity

    @classmethod
    def from_type_FormattedInt(cls, entity_field_obj) -> str:
        """Get value of Formatted In."""
        return str(entity_field_obj.value)

    @classmethod
    def set_type_FormattedInt(cls, entity, field_name, new_value, formatted_value):
        """Set value of FormattedInt."""
        my_int = FormattedInt(value=int(new_value), formatted_value=formatted_value)
        getattr(entity, field_name).CopyFrom(my_int)
        return entity

    @classmethod
    def from_type_FormattedStr(cls, entity_field_obj) -> str:
        """Get value of FormattedStr."""
        return entity_field_obj.value

    @classmethod
    def set_type_FormattedStr(cls, entity, field_name, new_value, formatted_value):
        """Set value of FormattedStr."""
        my_str = FormattedStr(value=new_value, formatted_value=formatted_value)
        getattr(entity, field_name).CopyFrom(my_str)
        return entity

    @classmethod
    def from_type_FormattedTimestamp(cls, entity_field_obj) -> str:
        """Get value of FormattedTimestamp."""
        if entity_field_obj.value.seconds != 0:
            return datetime.utcfromtimestamp(entity_field_obj.value.seconds).strftime(
                cls.date_format_string
            )  # noqa E501

    @classmethod
    def set_type_FormattedTimestamp(
        cls, entity, field_name, new_value, formatted_value
    ):
        """Set value of FormattedTimestamp."""
        timestamp_value = int(
            calendar.timegm(
                datetime.strptime(new_value, cls.date_format_string).timetuple()
            )
        )  # noqa E501

        timestamp = Timestamp()
        timestamp.seconds = timestamp_value

        my_timestamp = FormattedTimestamp(formatted_value=formatted_value)
        my_timestamp.value.CopyFrom(timestamp)

        getattr(entity, field_name).CopyFrom(my_timestamp)
        return entity

    @classmethod
    def from_type_WorkRegion(cls, entity_field_obj) -> str:
        """Get value of WorkRegion."""
        if entity_field_obj.region != 0:
            return str(entity_field_obj.region)

    @classmethod
    def set_type_WorkRegion(cls, entity, field_name, new_value, formatted_value):
        """Set value of WorkRegion."""
        translate_dict = {
            0: WorkRegion.REGION_EMPTY_UNSPECIFIED,
            1: WorkRegion.REGION_CONNECTICUT_HUDSON_VALLEY,
            2: WorkRegion.REGION_NEW_ENGLAND,
            3: WorkRegion.REGION_NEW_YORK_METRO,
            4: WorkRegion.REGION_INTER_REGION,
            5: WorkRegion.REGION_NATIONAL_NETWORK,
            6: WorkRegion.REGION_MID_ATLANTIC,
            7: WorkRegion.REGION_CHICAGO,
            8: WorkRegion.REGION_INTERNATIONAL_NETWORK,
            9: WorkRegion.REGION_KENTUCKY_INDIANA,
            10: WorkRegion.REGION_MICHIGAN,
            11: WorkRegion.REGION_OHIO,
            12: WorkRegion.REGION_WESTERN_NEW_YORK,
            13: WorkRegion.REGION_VIRGINIA_CAROLINAS,
            14: WorkRegion.REGION_VIRGINIA,
            15: WorkRegion.REGION_CALIFORNIA_INLAND_EMPIRE,
            16: WorkRegion.REGION_CALIFORNIA_LA_COUNTY,
            17: WorkRegion.REGION_CALIFORNIA_NORTHERN,
            18: WorkRegion.REGION_CALIFORNIA_ORANGE_COUNTY,
            19: WorkRegion.REGION_EASTERN_PENNSYLVANIA_NEW_JERSEY,
            20: WorkRegion.REGION_GEORGIA,
            21: WorkRegion.REGION_LOUISVILLE,
            22: WorkRegion.REGION_MINNEAPOLIS_ST_PAUL,
            23: WorkRegion.REGION_NORTH_FLORIDA,
            24: WorkRegion.REGION_NORTHERN_CALIFORNIA,
            25: WorkRegion.REGION_PACIFIC_NORTH_WEST,
            26: WorkRegion.REGION_PHOENIX,
            27: WorkRegion.REGION_PITTSBURGH,
            28: WorkRegion.REGION_SOUTH_FLORIDA,
            29: WorkRegion.REGION_SOUTHERN_CALIFORNIA,
            30: WorkRegion.REGION_ST_LOUIS,
            31: WorkRegion.REGION_ST_PAUL,
            32: WorkRegion.REGION_TENNESSEE,
            33: WorkRegion.REGION_TEXAS,
            34: WorkRegion.REGION_ROCKY_MOUNTAIN,
            35: WorkRegion.REGION_DESERT_SOUTHWEST,
            36: WorkRegion.REGION_LOS_ANGELES,
            37: WorkRegion.REGION_SAN_DIEGO,
        }
        work_region = WorkRegion(
            region=translate_dict[int(new_value)], formatted_value=formatted_value
        )
        getattr(entity, field_name).CopyFrom(work_region)
        return entity

    @classmethod
    def from_type_CreationSource(cls, entity_field_obj) -> str:
        """Get the value of CreationSource."""
        if entity_field_obj.source != 0:
            return entity_field_obj.source

    @classmethod
    def set_type_CreationSource(cls, entity, field_name, new_value, formatted_value):
        """Set the value of CreationSource."""
        translate_dict = {
            0: CreationSource.SOURCE_UNSPECIFIED,
            100000011: CreationSource.SOURCE_ACME,
        }
        source = CreationSource(
            source=translate_dict[int(new_value)], formatted_value=formatted_value
        )
        getattr(entity, field_name).CopyFrom(source)
        return entity

    @classmethod
    def enum_value_from_string(
        cls,
        entity,
        field_name,
        new_value,
        formatted_value,
        custom_message_type,
        int_to_enum,
    ):
        """Convert a CRM string value to a custom enum message type for a generated service."""
        try:
            value = int(new_value or 0)
        except (ValueError, TypeError) as e:
            raise ValueError(
                f"Invalid value for field {field_name!r}: "
                f"expected a string representation of an integer, got {new_value!r}."
            ) from e

        if value not in int_to_enum:
            raise ValueError(
                f"Invalid {custom_message_type.__name__} value: "
                f"{value} does not correspond to an enumerated value."
            )

        getattr(entity, field_name).CopyFrom(
            custom_message_type(
                value=int_to_enum[int(new_value)], formatted_value=formatted_value
            )
        )
        return entity

    @classmethod
    def string_from_enum_value(
        cls, entity_field_obj, custom_message_type, enum_to_int
    ) -> Optional[str]:
        """Convert a custom entity field object for a generated service into a CRM string value."""
        if entity_field_obj.value is custom_message_type.Enum.ENUM_UNSPECIFIED:
            return None

        if entity_field_obj.value not in enum_to_int:
            raise ValueError(
                f"{custom_message_type.__name__}.Enum."
                f"{custom_message_type.Enum.Name(entity_field_obj.value)} "
                "is not mapped to a CRM value."
            )

        return str(enum_to_int[entity_field_obj.value])
