"""Tests for entity_generation."""

import pytest
from unittest.mock import Mock
from google.protobuf.timestamp_pb2 import Timestamp
from crm_entity_generator.entity_generation import CrudType
from crm_entity_generator.protos import (
    AccessLog,
    CrmKeyValuePair,
    CreateCrmEntityResponse,
    CrmEntity,
    FormattedGuid,
    WorkRegion,
    UpdateCrmEntityRequest,
    UpdateCrmEntityResponse,
    SearchCrmEntitiesRequest,
    SearchCrmEntitiesResponse,
    contact_search_proto,
    contact_service,
    access_log_search_proto,
    access_log_service,
    assignment_service,
    assignment_search,
    crm_search_proto,
    crm_core_proto,
)
from tests.fixtures.generator_and_entity_utility import (
    AccessLogGenerator,
    AssignmentGenerator,
    ContactGenerator,
)


def test_accesslog_generator():
    """Test some values."""
    generator = AccessLogGenerator()
    assert type(generator.translate_proto_to_crm_dict) == dict
    assert len(generator.translate_proto_to_crm_dict) > 0
    assert type(generator.translate_proto_to_navigation_property) == dict
    assert len(generator.translate_proto_to_navigation_property) > 0
    assert type(generator.translate_proto_to_linked_entity) == dict
    assert len(generator.translate_proto_to_linked_entity) > 0
    assert type(generator.required_fields) == list
    assert len(generator.required_fields) > 0


def test_convert_to_crm_search_return_all_fields():
    """Test converting from a specific search type to a crm search type with return all=true."""
    generator = AccessLogGenerator()
    criterion1 = access_log_search_proto.AndCriteria(
        match=access_log_search_proto.AccessLogMatch.ACCESS_LOG_MATCH_EQUAL,
        access_log_number="55555",
    )
    criterion2 = access_log_search_proto.AndCriteria(
        match=access_log_search_proto.AccessLogMatch.ACCESS_LOG_MATCH_EQUAL,
        created_on=crm_core_proto.FormattedTimestamp(
            value=Timestamp(seconds=1234567890)
        ),
    )
    my_search = access_log_service.SearchAccessLogsRequest(
        anyof_criteria=[
            access_log_search_proto.OrCriteria(allof_criteria=[criterion1, criterion2])
        ],
        return_all=True,
        limit=5,
    )
    generic_search = (
        generator.convert_specific_entity_search_message_to_generic_search_message(
            specific_entity_search=my_search,
            specific_allof_entity_type=access_log_search_proto.AndCriteria,
        )
    )
    assert type(generic_search) == SearchCrmEntitiesRequest
    assert generic_search.return_all is True
    assert generic_search.limit == 5
    assert generic_search.search[0].criterion[0] == crm_search_proto.Criterion(
        match=crm_search_proto.MATCH_EQUAL,
        field_name="new_accesslognumber",
        field_value="'55555'",
    )
    assert generic_search.search[0].criterion[1] == crm_search_proto.Criterion(
        match=crm_search_proto.MATCH_GREAT_THAN_OR_EQUAL,
        field_name="createdon",
        field_value="2009-02-13T23:31:30Z",
    )
    assert generic_search.search[0].criterion[2] == crm_search_proto.Criterion(
        match=crm_search_proto.MATCH_LESS_THAN,
        field_name="createdon",
        field_value="2009-02-13T23:31:31Z",
    )


def test_convert_to_crm_search_field_to_return():
    """Test converting from a specific search type to a crm search type with fields to return."""
    generator = ContactGenerator()
    criterion1 = contact_search_proto.AndCriteria(
        match=contact_search_proto.CONTACT_MATCH_EQUAL, first_name="steve"
    )
    criterion2 = contact_search_proto.AndCriteria(
        match=contact_search_proto.CONTACT_MATCH_EQUAL, last_name="bagni"
    )
    criterion3 = contact_search_proto.AndCriteria(
        match=contact_search_proto.CONTACT_MATCH_EQUAL, email="blah@blah.com"
    )
    my_search = contact_service.SearchContactsRequest(
        anyof_criteria=[
            contact_search_proto.OrCriteria(
                allof_criteria=[criterion1, criterion2],
            ),
            contact_search_proto.OrCriteria(allof_criteria=[criterion3]),
        ],
        fields_to_return=contact_search_proto.ContactFieldsToReturn(
            fields_to_return=["first_name"]
        ),
        limit=5,
    )
    generic_search = (
        generator.convert_specific_entity_search_message_to_generic_search_message(
            specific_entity_search=my_search,
            specific_allof_entity_type=contact_search_proto.AndCriteria,
        )
    )
    assert type(generic_search) == SearchCrmEntitiesRequest
    assert generic_search.limit == 5
    assert generic_search.fields_to_return == crm_search_proto.CrmFieldsToReturn(
        fields_to_return=["firstname"]
    )
    assert generic_search.search[0].criterion[0] == crm_search_proto.Criterion(
        match=crm_search_proto.MATCH_EQUAL,
        field_name="firstname",
        field_value="'steve'",
    )
    assert generic_search.search[0].criterion[1] == crm_search_proto.Criterion(
        match=crm_search_proto.MATCH_EQUAL, field_name="lastname", field_value="'bagni'"
    )
    assert generic_search.search[1].criterion[0] == crm_search_proto.Criterion(
        match=crm_search_proto.MATCH_EQUAL,
        field_name="emailaddress1",
        field_value="'blah@blah.com'",
    )


def test_get_field_type():
    """Test get field type."""
    access_log = AccessLog(first_name="adam")
    field_type = AccessLogGenerator.get_field_type(
        specific_entity=access_log, field="first_name"
    )
    assert field_type == "str"


def test_get_list_of_kvps_protected_field_empty_and_type_is_update():
    """Test get list of kvps and protected field is empty."""
    generator = AccessLogGenerator()
    generator.translate_proto_to_crm_dict = {"id": "id"}
    generator.protected_fields = {CrudType.UPDATE: ["id"]}
    results = generator.get_list_of_kvps(
        crud_type=CrudType.UPDATE, specific_entity=AccessLog(), already_empty_fields=[]
    )
    assert len(results) == 0


def test_get_list_of_kvps_protected_fields_and_type_is_create():
    """Test get list of kvps and protected field is empty."""
    generator = AccessLogGenerator()
    generator.translate_proto_to_crm_dict = {"account_number": "account_number"}
    generator.protected_fields = {CrudType.CREATE: ["account_number"]}
    results = generator.get_list_of_kvps(
        crud_type=CrudType.CREATE, specific_entity=AccessLog(), already_empty_fields=[]
    )
    assert len(results) == 0


def test_get_list_of_kvps_protected_fields_and_super_secret_legacy_implementation():
    """Test get list of kvps and protected field is using legacy implementation."""
    generator = AccessLogGenerator()
    generator.translate_proto_to_crm_dict = {"account_number": "account_number"}
    generator.protected_fields = ["account_number"]
    results = generator.get_list_of_kvps(
        crud_type=CrudType.CREATE, specific_entity=AccessLog(), already_empty_fields=[]
    )
    assert len(results) == 0


def test_build_kvp_with_linked_entity_empty_proto_to_navigation():
    """Test build kvp with linked entity and no linked entity."""
    with pytest.raises(Exception) as error_info:
        generator = AccessLogGenerator()
        generator.translate_proto_to_crm_dict = {"name": "name"}
        generator.translate_proto_to_linked_entity = {}
        generator.build_kvp_with_linked_entity(field_name="name", field_value="Luke")
        assert (
            error_info.value
            == '"You have not set a navigation property for "name" in the generator'
        )


def test_get_list_of_kvps_already_empty_and_blank_value():
    """Test get list of kvps and field is already empty in existing entity."""
    generator = AccessLogGenerator()
    generator.required_fields = []
    generator.translate_proto_to_crm_dict = {"first_name": "first_name"}
    results = generator.get_list_of_kvps(
        crud_type=CrudType.UPDATE,
        specific_entity=AccessLog(),
        already_empty_fields=["first_name"],
    )
    assert len(results) == 0


def test_get_list_of_kvps_empty_required_field():
    """Test get kvps and required field is empty"""
    with pytest.raises(Exception) as error_info:
        generator = AccessLogGenerator()
        generator.translate_proto_to_crm_dict = {"first_name": "first_name"}
        generator.required_fields = ["first_name"]
        generator.translate_proto_to_linked_entity = {}
        generator.get_list_of_kvps(
            crud_type=CrudType.UPDATE,
            specific_entity=AccessLog(first_name=""),
            already_empty_fields=["first_name"],
        )
        assert (
            error_info.value
            == "The field: first_name is required and cannot be left blank or deleted"
        )


def test_build_kvp_with_linked_entity_no_navigation_property():
    """Test build kvp with linked entity and no navigation property."""
    with pytest.raises(Exception) as error_info:
        generator = AccessLogGenerator()
        generator.translate_proto_to_crm_dict = {"name": "name"}
        generator.translate_proto_to_navigation_property = {}
        generator.build_kvp_with_linked_entity(field_name="name", field_value="Luke")
        assert (
            error_info.value
            == '"You have not set a navigation property for "name" in the generator'
        )


def test_build_kvp_with_linked_entity_no_linked_entity():
    """Test build kvp with linked entity and no linked entity."""
    with pytest.raises(Exception) as error_info:
        generator = AccessLogGenerator()
        generator.translate_proto_to_crm_dict = {"name": "name"}
        generator.translate_proto_to_linked_entity = {}
        generator.translate_proto_to_navigation_property = {"name": "name"}
        generator.build_kvp_with_linked_entity(field_name="name", field_value="Luke")
        assert (
            error_info.value
            == '"You have not set a linked entity for "name" in the generator'
        )


def test_generate_formatted_value_and_value_dict():
    """Test generate formatted value and value dict."""
    one = CrmKeyValuePair(
        key="new_workregion@OData.Community.Display.V1.FormattedValue",
        str_value={"value": "California - LA County"},
    )
    two = CrmKeyValuePair(key="new_workregion", str_value={"value": "16"})
    response_fields = [one, two]
    generator = AccessLogGenerator()
    value_dict = generator.generate_formatted_value_and_value_dict(response_fields)
    assert value_dict == {
        "new_workregion": {"formatted_value": "California - LA County", "value": "16"}
    }


def test_crm_result_to_specific_entity():
    """Test crm_result_to_specific_entity."""
    generator = AccessLogGenerator()
    kvps = [
        CrmKeyValuePair(
            key="new_workregion@OData.Community.Display.V1.FormattedValue",
            str_value={"value": "California - LA County"},
        ),
        CrmKeyValuePair(key="new_workregion", str_value={"value": "16"}),
    ]
    crm_response = CreateCrmEntityResponse(
        entity=CrmEntity(
            crm_entity_type="new_accesslog", guid=FormattedGuid(value=""), fields=kvps
        )
    )
    entity = generator.crm_result_to_specific_entity(
        specific_entity_type=type(AccessLog()),
        one_crm_entity_response=crm_response.entity,
    )
    access_log = AccessLog(
        work_region=WorkRegion(region=16, formatted_value="California - LA County")
    )
    assert access_log == entity


def test_crm_result_to_specific_entity_field_not_in_crm_to_proto():
    """Test crm_result_to_specific_entity with field not in crm to proto."""
    generator = AccessLogGenerator()
    kvps = [
        CrmKeyValuePair(
            key="new_workregion@OData.Community.Display.V1.FormattedValue",
            str_value={"value": "California - LA County"},
        ),
        CrmKeyValuePair(key="new_workregion", str_value={"value": "16"}),
        CrmKeyValuePair(key="Darth", str_value={"value": "Vader"}),
    ]
    crm_response = CreateCrmEntityResponse(
        entity=CrmEntity(
            crm_entity_type="new_accesslog", guid=FormattedGuid(value=""), fields=kvps
        )
    )
    entity = generator.crm_result_to_specific_entity(
        specific_entity_type=type(AccessLog()),
        one_crm_entity_response=crm_response.entity,
    )
    access_log = AccessLog(
        work_region=WorkRegion(region=16, formatted_value="California - LA County")
    )
    assert access_log == entity


def test_specific_entity_to_generic_crm_entity():
    """Test specific_entity_to_generic_crm_entity."""
    generator = AccessLogGenerator()
    generator.required_fields = []
    generator.translate_proto_to_crm_dict = {"work_region": "new_workregion"}
    access_log = AccessLog(
        work_region=WorkRegion(region=16, formatted_value="California - LA County")
    )
    entity = generator.specific_entity_to_generic_crm_entity(
        specific_entity=access_log, crud_type=CrudType.UPDATE
    )
    mock_entity = CrmEntity(
        crm_entity_type="new_accesslogs",
        fields=[
            CrmKeyValuePair(key="new_workregion", str_value={"value": "16"}, value="16")
        ],
    )
    assert entity == mock_entity


@pytest.mark.parametrize(
    "translate_value,expected",
    [
        ("/new_states", "/new_states"),
        ("new_states", "/new_states"),
        (["new_states", "/new_new_stateseses"], "/new_states"),
    ],
)
def test_build_kvp_with_linked_entity(translate_value, expected):
    """Test build_kvp_with_linked_entity."""
    field_name = "state_work_is_in"
    generator = AccessLogGenerator()
    generator.translate_proto_to_linked_entity[field_name] = translate_value

    kvp = generator.build_kvp_with_linked_entity(
        field_name=field_name, field_value="Zelda"
    )
    mock_kvp = CrmKeyValuePair(
        key="new_StateWorkIsInid",
        str_value={"value": "Zelda"},
        linked_entity=expected,
        value="Zelda",
    )
    assert kvp == mock_kvp


@pytest.mark.parametrize(
    "translate_value,expected",
    [
        ("/new_states", "/new_states"),
        ("new_states", "/new_states"),
        (["new_states", "/new_new_stateseses"], "/new_states"),
    ],
)
def test_build_kvp_for_field_deletion(translate_value, expected):
    """Test build_kvp_for_field_deletion."""
    field_name = "state_work_is_in"
    generator = AccessLogGenerator()
    generator.translate_proto_to_linked_entity[field_name] = translate_value

    kvp = generator.build_kvp_for_field_deletion(
        field_name=field_name, field_value="Zelda"
    )
    mock_kvp = CrmKeyValuePair(
        key="new_StateWorkIsInid",
        str_value={"value": "Zelda"},
        linked_entity=expected,
        value="Zelda",
    )
    assert kvp == mock_kvp


def test_get_list_of_kvps():
    """Test get_list_of_kvps."""
    generator = AccessLogGenerator()
    generator.translate_proto_to_crm_dict = {"state_work_is_in": "new_StateWorkIsInid"}
    access_log = AccessLog(
        state_work_is_in=FormattedGuid(value="1", formatted_value="The Moon")
    )
    mock_kvps = [
        CrmKeyValuePair(
            key="new_StateWorkIsInid",
            str_value={"value": "1"},
            linked_entity="/new_states",
            value="1",
        )
    ]
    kvps = generator.get_list_of_kvps(
        specific_entity=access_log, crud_type=CrudType.CREATE
    )
    assert kvps == mock_kvps


def test_update():
    """Test the update function."""
    generator = AccessLogGenerator()
    generator.required_fields = []
    mock_entity = CrmEntity(
        crm_entity_type="new_accesslog",
        fields=[CrmKeyValuePair(key="new_firstname", str_value={"value": "Marge"})],
    )
    mock_crm_response = UpdateCrmEntityResponse(entity=mock_entity)
    mock_crm_adapter = Mock()
    mock_crm_adapter.UpdateCrmEntity.return_value = mock_crm_response
    access_log = AccessLog(first_name="Marge")
    entity = generator.update(
        crm_adapter=mock_crm_adapter,
        specific_entity=access_log,
        specific_entity_guid="id",
        already_empty_fields=[],
    )
    assert entity == access_log


def test_update_with_existing():
    """Test updating an entity correctly filters unchanged fields."""
    generator = AccessLogGenerator()
    generator.required_fields = []

    mock_entity = CrmEntity(
        crm_entity_type="new_accesslog",
        fields=[
            CrmKeyValuePair(key="new_firstname", str_value={"value": "Marge"}),
            CrmKeyValuePair(key="new_lastname", str_value={"value": "Bouvier"}),
        ],
    )
    mock_crm_response = UpdateCrmEntityResponse(entity=mock_entity)

    mock_crm_adapter = Mock()
    mock_crm_adapter.UpdateCrmEntity.return_value = mock_crm_response

    existing_access_log = AccessLog(first_name="Marge", last_name="Simpson")
    updated_access_log = AccessLog(first_name="Marge", last_name="Bouvier")

    entity = generator.update(
        crm_adapter=mock_crm_adapter,
        specific_entity=updated_access_log,
        specific_entity_guid="id",
        already_empty_fields=[
            "id",
            "company_name",
            "owning_business_unit_guid",
            "state_work_is_in",
            "change_management_guid",
            "service_number_guid",
            "preventative_maintenance_guid",
            "location_guid",
            "noc_ticket_guid",
            "created_by_guid",
            "access_log_number",
            "access_log_type",
            "start_date_and_time",
            "end_date_and_time",
            "created_on",
            "access_log_status",
            "enclosure_name",
            "span_id",
            "netcracker_equipment_name",
            "contact_email",
            "contact_name",
            "contact_phone",
            "contact_email",
            "owning_team_guid",
            "owning_user_guid",
            "user_guid",
            "account_guid",
            "vendor_guid",
            "work_region",
            "notes",
            "description",
            "other",
            "ospi_notes",
            "address_or_cross_street",
            "county",
            "completed_as_designed",
            "work_related_status",
            "creation_source",
        ],
        existing_entity=existing_access_log,
    )

    assert entity == updated_access_log
    mock_crm_adapter.UpdateCrmEntity.assert_called_once_with(
        UpdateCrmEntityRequest(
            entity=CrmEntity(
                crm_entity_type="new_accesslogs",
                guid=FormattedGuid(value="id"),
                fields=[
                    CrmKeyValuePair(
                        key="new_lastname",
                        str_value={"value": "Bouvier"},
                        value="Bouvier",
                    ),
                ],
            )
        )
    )


def test_update_with_existing_all_fields_the_same():
    """Test updating an entity correctly filters unchanged fields."""
    generator = AccessLogGenerator()
    generator.required_fields = []

    mock_entity = CrmEntity(
        crm_entity_type="new_accesslog",
        fields=[
            CrmKeyValuePair(key="new_firstname", str_value={"value": "Marge"}),
            CrmKeyValuePair(key="new_lastname", str_value={"value": "Bouvier"}),
        ],
    )
    mock_crm_response = UpdateCrmEntityResponse(entity=mock_entity)

    mock_crm_adapter = Mock()
    mock_crm_adapter.UpdateCrmEntity.return_value = mock_crm_response

    existing_access_log = AccessLog(first_name="Marge", last_name="Simpson")
    updated_access_log = AccessLog(first_name="Marge", last_name="Simpson")

    entity = generator.update(
        crm_adapter=mock_crm_adapter,
        specific_entity=updated_access_log,
        specific_entity_guid="id",
        already_empty_fields=[
            "id",
            "company_name",
            "owning_business_unit_guid",
            "state_work_is_in",
            "change_management_guid",
            "service_number_guid",
            "preventative_maintenance_guid",
            "location_guid",
            "noc_ticket_guid",
            "created_by_guid",
            "access_log_number",
            "access_log_type",
            "start_date_and_time",
            "end_date_and_time",
            "created_on",
            "access_log_status",
            "enclosure_name",
            "span_id",
            "netcracker_equipment_name",
            "contact_email",
            "contact_name",
            "contact_phone",
            "contact_email",
            "owning_team_guid",
            "owning_user_guid",
            "user_guid",
            "account_guid",
            "vendor_guid",
            "work_region",
            "notes",
            "description",
            "other",
            "ospi_notes",
            "address_or_cross_street",
            "county",
            "completed_as_designed",
            "work_related_status",
            "creation_source",
        ],
        existing_entity=existing_access_log,
    )

    assert entity == updated_access_log
    mock_crm_adapter.UpdateCrmEntity.assert_not_called()


def test_search_with_guid_field():
    """Test the search function runs through the guid field check."""
    generator = AssignmentGenerator()
    mock_crm_adapter = Mock()
    mock_entity = CrmEntity(
        crm_entity_type="new_assignments",
        fields=[CrmKeyValuePair(key="new_firstname", str_value={"value": "Homer"})],
    )
    mock_crm_response = SearchCrmEntitiesResponse(entity=mock_entity)
    mock_crm_adapter.SearchCrmEntities.return_value = mock_crm_response
    my_search = assignment_service.SearchAssignmentsRequest(
        anyof_criteria=[
            assignment_search.OrCriteria(
                allof_criteria=[
                    assignment_search.AndCriteria(
                        match=assignment_search.ASSIGNMENT_MATCH_CONTAINS,
                        id=FormattedGuid(value="'1234'", formatted_value="blah"),
                    ),
                ]
            )
        ],
        return_all=True,
        limit=10,
    )
    results = generator.search(
        crm_adapter=mock_crm_adapter, search=my_search, specific_entity_type=AccessLog
    )
    search_crm_entities_request = SearchCrmEntitiesRequest(
        crm_entity_type="new_assignmentses",
        search=[
            crm_search_proto.EntitySearch(
                criterion=[
                    crm_search_proto.Criterion(
                        match=crm_search_proto.Match.MATCH_CONTAINS,
                        field_name="new_assignmentsid",
                        field_value="1234",
                    )
                ]
            )
        ],
        return_all=True,
        limit=10,
    )
    mock_crm_adapter.SearchCrmEntities.assert_called_with(search_crm_entities_request)
    assert results.entity == mock_entity


def test_search_invalid_fields_to_return():
    """Test the search function errors on invalid fields."""
    with pytest.raises(ValueError) as error_info:
        generator = AccessLogGenerator()
        mock_crm_adapter = Mock()
        my_search = access_log_service.SearchAccessLogsRequest(
            anyof_criteria=[
                access_log_search_proto.OrCriteria(
                    allof_criteria=[
                        access_log_search_proto.AndCriteria(
                            match=access_log_search_proto.ACCESS_LOG_MATCH_CONTAINS,
                            access_log_number="ACC",
                        ),
                    ]
                )
            ],
            fields_to_return=access_log_search_proto.AccessLogFieldsToReturn(
                fieldss_to_return=["lightsaber_color"]
            ),
            limit=10,
        )
        generator.search(
            crm_adapter=mock_crm_adapter,
            search=my_search,
            specific_entity_type=AccessLog,
        )
        assert error_info.value == "Invalid fields to return: lightsaber_color"


def test_search():
    """Test the search function."""
    generator = AccessLogGenerator()
    generator.required_fields = []
    mock_crm_adapter = Mock()
    mock_entity = CrmEntity(
        crm_entity_type="new_accesslog",
        fields=[CrmKeyValuePair(key="new_firstname", str_value={"value": "Homer"})],
    )
    mock_crm_response = SearchCrmEntitiesResponse(entity=mock_entity)
    mock_crm_adapter.SearchCrmEntities.return_value = mock_crm_response
    my_search = access_log_service.SearchAccessLogsRequest(
        anyof_criteria=[
            access_log_search_proto.OrCriteria(
                allof_criteria=[
                    access_log_search_proto.AndCriteria(
                        match=access_log_search_proto.ACCESS_LOG_MATCH_CONTAINS,
                        access_log_number="ACC",
                    ),
                ]
            )
        ],
        return_all=True,
        limit=10,
    )

    search_crm_entities_request = SearchCrmEntitiesRequest(
        crm_entity_type="new_accesslogs",
        search=[
            crm_search_proto.EntitySearch(
                criterion=[
                    crm_search_proto.Criterion(
                        match=crm_search_proto.Match.MATCH_CONTAINS,
                        field_name="new_accesslognumber",
                        field_value="'ACC'",
                    )
                ]
            )
        ],
        return_all=True,
        limit=10,
    )

    results = generator.search(
        crm_adapter=mock_crm_adapter, search=my_search, specific_entity_type=AccessLog
    )
    mock_crm_adapter.SearchCrmEntities.assert_called_with(search_crm_entities_request)
    assert results.entity == mock_entity


def test_create():
    """Test the create function."""
    generator = AccessLogGenerator()
    generator.required_fields = []
    mock_entity = CrmEntity(
        crm_entity_type="new_accesslog",
        fields=[CrmKeyValuePair(key="new_firstname", str_value={"value": "Marge"})],
    )
    mock_crm_response = CreateCrmEntityResponse(entity=mock_entity)
    mock_crm_adapter = Mock()
    mock_crm_adapter.CreateCrmEntity.return_value = mock_crm_response
    access_log = AccessLog(first_name="Marge")
    entity = generator.create(
        crm_adapter=mock_crm_adapter,
        specific_entity=access_log,
    )
    assert entity == access_log
