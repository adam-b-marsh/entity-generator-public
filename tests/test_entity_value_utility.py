"""Tests for entity_value_utility."""

import pytest
from unittest import mock
from crm_entity_generator.entity_generation import EntityValueUtility
from crm_entity_generator.protos import (
    AccessLog,
    FormattedInt,
    FormattedStr,
    FormattedTimestamp,
    CreationSource,
)


def test_set_entity_attribute():
    """Test set entity attribute."""
    access_log = AccessLog()
    access_log = EntityValueUtility().set_entity_attribute(
        entity=access_log,
        field_name="first_name",
        field_type="str",
        new_value="Luke",
        formatted_value="blargh",
    )
    assert hasattr(access_log, "first_name")
    assert access_log.first_name == "Luke"


def test_set_entity_error():
    """Test error for set entity attribute."""
    with pytest.raises(TypeError) as error_info:
        access_log = AccessLog()
        access_log = EntityValueUtility().set_entity_attribute(
            entity=access_log,
            field_name="first_name",
            field_type="magical_unicorn",
            new_value="Luke",
            formatted_value="blargh",
        )
        assert error_info.value == (
            "Set function for field type: 'magical_unicorn' has not been created."
        )


def test_get_ultimate_value_wrong_field():
    """Test get ultimate value with a wrong field."""
    with pytest.raises(TypeError) as error_info:
        access_log = AccessLog(first_name="Luke")
        value = EntityValueUtility().get_ultimate_value(
            entity=access_log, field_name="first_name", field_type="demon_baby"
        )
        assert value
        assert error_info.value == (
            "Get function for field type: 'demon_baby' has not been created"
        )


def test_get_ultimate_value():
    """Test ultimate value."""
    access_log = AccessLog(first_name="Luke")
    value = EntityValueUtility().get_ultimate_value(
        entity=access_log, field_name="first_name", field_type="str"
    )
    assert value == "Luke"


def test_from_type_bool():
    """Test from type boolean."""
    value = EntityValueUtility().from_type_bool(False)
    assert value is False


def test_set_type_bool():
    """Test set type bool."""

    class MyMockObject:
        bool_field: bool = True

    entity = EntityValueUtility().set_type_bool(
        entity=MyMockObject,
        field_name="bool_field",
        new_value=False,
        formatted_value="",
    )
    assert entity.bool_field is False


def test_from_type_int():
    """Test from type int."""
    value = EntityValueUtility().from_type_int(1)
    assert value == 1


def test_set_type_int():
    """Test set type int."""

    class MyMockObject:
        int_field = 1

    entity = EntityValueUtility().set_type_int(
        entity=MyMockObject, field_name="int_field", new_value=2, formatted_value=""
    )
    assert entity.int_field == 2


def test_from_type_float():
    """Test from type float."""
    value = EntityValueUtility().from_type_float(1.1)
    assert value == 1.1


def test_set_type_float():
    """Test set type float."""

    class MyMockObject:
        float_field = 0.0

    entity = EntityValueUtility().set_type_float(
        entity=MyMockObject, field_name="float_field", new_value=1.1, formatted_value=""
    )
    assert entity.float_field == 1.1


def test_set_type_FormattedGuid():
    """Test set type FormattedGuid."""
    entity = EntityValueUtility().set_type_FormattedGuid(
        entity=AccessLog(),
        field_name="service_number_guid",
        new_value="2",
        formatted_value="Banana Republic",
    )
    assert entity.service_number_guid.value == "2"


def test_from_type_FormattedInt():
    """Test from type FormattedInt."""
    mock_obj = mock.Mock()
    mock_obj.value = 1
    value = EntityValueUtility().from_type_FormattedInt(mock_obj)
    assert value == "1"


def test_set_type_FormattedInt():
    """Black magic test, that a smarter person than me wrote that passes so...yay!"""
    m = mock.Mock()
    obj = EntityValueUtility().set_type_FormattedInt(m, "test_field", "17", "seventeen")
    assert m is obj
    ((formatted_int,), _) = m.test_field.CopyFrom.call_args
    assert isinstance(formatted_int, FormattedInt)
    assert formatted_int.value == 17
    assert formatted_int.formatted_value == "seventeen"


def test_from_type_FormattedStr():
    """Test from type FormattedStr."""
    mock_obj = mock.Mock()
    mock_obj.value = "1"
    value = EntityValueUtility().from_type_FormattedStr(mock_obj)
    assert value == "1"


def test_set_type_FormattedStr():
    """Black magic test, that a smarter person than me wrote that passes so...yay!"""
    m = mock.Mock()
    obj = EntityValueUtility().set_type_FormattedStr(m, "test_field", "17", "seventeen")
    assert m is obj
    ((formatted_str,), _) = m.test_field.CopyFrom.call_args
    assert isinstance(formatted_str, FormattedStr)
    assert formatted_str.value == "17"
    assert formatted_str.formatted_value == "seventeen"


def test_from_type_FormattedTimestamp():
    """Test from type FormattedTimestamp."""
    mock_obj = mock.Mock()
    mock_obj.value.seconds = 12345914947
    value = EntityValueUtility().from_type_FormattedTimestamp(mock_obj)
    assert value == "2361-03-24T12:49:07Z"


def test_set_type_FormattedTimestamp():
    """Test set type FormattedTimestamp"""
    entity = EntityValueUtility().set_type_FormattedTimestamp(
        AccessLog(), "start_date_and_time", "2361-03-24T12:49:07Z", ""
    )
    assert isinstance(entity.start_date_and_time, FormattedTimestamp)
    assert entity.start_date_and_time.value.seconds == 12345914947


def test_from_type_CreationSource():
    """Test from type CreationSource."""
    mock_obj = mock.Mock()
    mock_obj.source = 101
    value = EntityValueUtility().from_type_CreationSource(mock_obj)
    assert value == 101


def test_set_type_CreationSource():
    """Test set type CreationSource."""
    entity = EntityValueUtility().set_type_CreationSource(
        AccessLog(), "creation_source", 0, ""
    )
    assert isinstance(entity.creation_source, CreationSource)
    assert entity.creation_source.source == 0


def test_enum_value_from_string_invalid_input():
    """Test from_type helper method for generated CRM services input error handling."""
    entity_value_utility = EntityValueUtility()
    with pytest.raises(
        ValueError,
        match=(
            "Invalid value for field 'field_name': "
            "expected a string representation of an integer, got 'null'"
        ),
    ):
        entity_value_utility.enum_value_from_string(
            mock.NonCallableMock(),
            "field_name",
            "null",
            "formatted_value",
            mock.NonCallableMock(),
            {},
        )


def test_enum_value_from_string_unmapped_input():
    """Test from_type helper method for generated CRM services input error handling."""
    mock_entity_field_constructor = mock.NonCallableMock(__name__="FieldName")

    entity_value_utility = EntityValueUtility()
    with pytest.raises(
        ValueError,
        match=(
            "Invalid FieldName value: " "1 does not correspond to an enumerated value."
        ),
    ):
        entity_value_utility.enum_value_from_string(
            mock.NonCallableMock(),
            "field_name",
            "1",
            "formatted_value",
            mock_entity_field_constructor,
            {},
        )


def test_enum_value_from_string():
    """Test from_type helper method for generated CRM services."""
    mock_entity_field_constructor = mock.Mock(return_value=mock.Mock())
    mock_entity = mock.Mock(field=mock.Mock())
    mock_enum = mock.NonCallableMock()
    set_field = {1: mock_enum}

    entity_value_utility = EntityValueUtility()
    entity = entity_value_utility.enum_value_from_string(
        mock_entity,
        "field_name",
        "1",
        "formatted_value",
        mock_entity_field_constructor,
        set_field,
    )

    assert entity is mock_entity
    entity.field_name.CopyFrom.assert_called_once_with(
        mock_entity_field_constructor.return_value
    )
    mock_entity_field_constructor.assert_called_once_with(
        value=mock_enum, formatted_value="formatted_value"
    )


def test_string_from_enum_value_unspecified_input():
    """Test set_type helper method for generated CRM services input error handling."""
    mock_enum = mock.NonCallableMock()
    mock_entity_field_constructor = mock.NonCallableMock(
        Enum=mock.NonCallableMock(ENUM_UNSPECIFIED=mock_enum)
    )
    mock_entity_field_obj = mock.Mock(value=mock_enum)
    from_type = {mock.NonCallableMock(): 1}

    entity_value_utility = EntityValueUtility()
    value = entity_value_utility.string_from_enum_value(
        mock_entity_field_obj, mock_entity_field_constructor, from_type
    )

    assert value is None


def test_string_from_enum_value_unmapped_input():
    """Test set_type helper method for generated CRM services."""
    mock_entity_field_constructor = mock.NonCallableMock(
        __name__="FieldName",
        Enum=mock.NonCallableMock(
            Name=mock.Mock(return_value="ENUM_UNMAPPED"),
            ENUM_UNSPECIFIED=mock.NonCallableMock(),
        ),
    )
    mock_enum = mock.NonCallableMock()
    mock_entity_field_obj = mock.Mock(value=mock_enum)
    from_type = {}

    entity_value_utility = EntityValueUtility()
    with pytest.raises(
        ValueError, match="FieldName.Enum.ENUM_UNMAPPED is not mapped to a CRM value."
    ):
        entity_value_utility.string_from_enum_value(
            mock_entity_field_obj, mock_entity_field_constructor, from_type
        )

    mock_entity_field_constructor.Enum.Name.assert_called_once_with(mock_enum)


def test_string_from_enum_value():
    """Test set_type helper method for generated CRM services."""
    mock_entity_field_constructor = mock.NonCallableMock(
        Enum=mock.NonCallableMock(ENUM_UNSPECIFIED=mock.NonCallableMock())
    )
    mock_enum = mock.NonCallableMock()
    mock_entity_field_obj = mock.Mock(value=mock_enum)
    from_type = {mock_enum: 1}

    entity_value_utility = EntityValueUtility()
    value = entity_value_utility.string_from_enum_value(
        mock_entity_field_obj, mock_entity_field_constructor, from_type
    )

    assert value == "1"
