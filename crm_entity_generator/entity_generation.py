"""Contains EntityGenerator class."""

import re
from typing import List, Dict, NamedTuple, Optional, Type, Union
from collections import defaultdict
from enum import Enum
from crm_entity_generator.protos import (
    CreateCrmEntityRequest,
    UpdateCrmEntityRequest,
    SearchCrmEntitiesRequest,
    CrmEntity,
    CrmKeyValuePair,
    FormattedGuid,
    EntitySearch,
    crm_search_proto,
    CrmServiceStub,
)
from google.protobuf.message import Message
from crm_entity_generator.entity_value_utility import EntityValueUtility
from google.protobuf.internal.containers import RepeatedCompositeFieldContainer
from google.protobuf.wrappers_pb2 import (
    FloatValue,
    UInt64Value,
    StringValue,
    BoolValue,
    DoubleValue,
)


class FieldMapping(NamedTuple):
    """Name the fields in the translation compendium.

    :param protobuf_field: the name of the field as it is represented in abc-protobuf
    :type protobuf_field: str
    :param crm_field: the name of the field as it exists on the crm entity this generator is
        built for
    :type crm_field: str
    :param navigation_crm_field: the "navigation property" that exists for this field on the
        crm entity this generator is built for. This value is used when updating this type
        (Lookup) of field.
    :type crm_field Optional str
    :param linked_entity: The name of the crm entity that the lookup field is referencing.
        There can be more than one entity type per Lookup field (eg. User / Teams) might
        be allowed in a field called "owner". Previous versions have required a "/" prefix
        for entity type names. This is still supported but should be considered deprecated
        in favor of the bare entity type name only, ie. prefer "system_users" over "/system_users".
    :type linked_entity: Optional[Union[str, List[str]]]
    :param owning_entities_primary_id_field_name: The name of the crm field that describes
        the primary id of the linked_entity referenced for a Lookup field.
    :type owning_entities_primary_id_field_name: Optional str
    """

    protobuf_field: str
    crm_field: str
    navigation_crm_field: Optional[str] = None
    linked_entity: Optional[Union[str, List[str]]] = None
    owning_entities_primary_id_field_name: Optional[str] = None


class CrudType(Enum):
    """CrudType Enum."""

    CREATE = 1
    READ = 2
    UPDATE = 3
    DELETE = 4


class EntityGenerator:
    """Class to generate a specific entity.

    :param crm_api_formatted_value_string: string that defines marker for formatted value in crm
        response. Any field that is an enum variant or has a guid value will have an accompanying
        @Odata.Community.Display.V1.FormattedValue field - to provide the 'display' or 'formatted'
        value
    :type crm_api_formatted_value_string: str
    :param entity_value_utility: Class that has get/set methods for an entity type
    :type entity_value_utility: EntityValueUtility
    :param entity_type: type of crm entity eg. 'newaccesslogs'
    :type entity_type: str
    :param entity_guid_field: the name of the crm field for the particular entity you're operating
        with which references its own guid eg. 'new_accesslogid'
    :type entity_guid_field: str
    :param crm_creation_source_value: a "numerical string" eg. '10000011' that references an enum
        in CRM - which defines what method is being used to create the record
        (CRM, ACME, PC Client, etc)
    :type crm_creation_source_value: str
    :param required_fields: a flat list of crm field names for the specific entity you're operating
        with which defines which fields are required to create a record
    :type required_fields: List[str]
    :param protected_fields: a Dict of crm field names for the specific entity you're operating
        with which defines which fields are protected and cannot be created / updated / deleted
    :type protected_fields: Dict[CrudType, List[str]]
    :type translation_compendium: List[Tuple]
    :param translation_compendium: a list of tuples that contains the translation information
        between protofield / crm_fields / crm navigation names and crm linked entity names
    :param translate_proto_to_linked_entity: a Dictionary that allows the translation between
        protobuf field names for your specific entity and crm 'linked entities'. Linked entity
        refers to the CRM entity that the guid provided for this field is referencing.
        eg. ("created_by_guid": "/systemusers")
        The key of the dictionary is the protobuf field name and its value is linked entity
    :type translate_proto_to_linked_entity: Dict[protobuf_field: str, linked_entity: str]
    :param translate_proto_to_navigation_property: a Dictionary that allows the translation between
        protobuf field names and the 'navigation property' of a CRM field. The navigation property
        is required when operating on fields that are 'linked' to other CRM entities. The key of
        the dictionary is the protobuf field name and its value is the crm navigation property
    :type translate_proto_to_navigation_property: Dict[str: protobuf_field, str: crm_navigation_property]  # noqa E501
    :param translate_proto_to_crm_dict: a Dictionary that allows the translation between
        protobuf field names for your specific entity and crm field names for the same entity.
        The key of the dictionary is the protobuf field name and its value is the crm field name
    :type translate_proto_to_crm_dict: Dict[protobuf_field: str, crm_field_name: str]
    """

    crm_api_formatted_value_string = "@OData.Community.Display.V1.FormattedValue"
    entity_value_utility: EntityValueUtility

    entity_type: str = ""
    entity_guid_field: str = ""
    crm_creation_source_value: str = ""
    required_fields: List[str] = []
    protected_fields: Dict[CrudType, List[str]] = {}
    translation_compendium: List[FieldMapping] = []
    translate_proto_to_linked_entity: Dict[str, str] = {}
    translate_proto_to_navigation_property: Dict[str, str] = {}
    translate_proto_to_crm_dict: Dict[str, str] = {}
    full_proto_to_linked_entity: Dict[str, Optional[List[str]]] = {}
    full_proto_to_navigation_property: Dict[str, Optional[str]] = {}
    full_proto_to_crm_dict: Dict[str, str] = {}

    @staticmethod
    def get_field_type(specific_entity: Message, field: str) -> str:
        """Get a field type.

        :param specific_entity: an actual copy of a fully formed Entity from one of the ordering
            mid-tiers - not just the type.
        :param field: the name (protobuf field name) of one of the fields on that particular
            entity
        """
        field_type = type(getattr(specific_entity, field)).__name__
        return field_type

    def specific_to_generic_allof_criteria(
        self, allof_criterion, specific_allof_entity_type
    ) -> List[crm_search_proto.Criterion]:
        """Convert specific criterion to generic criterion.

        :param allof_criterion: an AndCriteria from one of the ordering mid-tier services.
        :param specific_allof_entity_type: the capital T, Type of ordering entity you are
            searching for (eg. AccessLog, NetworkElement)

        """
        list_of_generic_and_criterion = []
        this_field_name = allof_criterion.WhichOneof("field_to_search")
        this_field_type = self.get_field_type(
            specific_allof_entity_type(), this_field_name
        )

        # This isn't techincally a kosher comparison, because `allof_criterion.match`
        # will be of the <Entity>Match enum type for the specific service whereas
        # crm_search_proto.Match is from the adapter layer.
        # However, we're already relying on the integer values of the enums being
        # consistent between the adapter and all the ordering-* services.
        # So, until we fix `crm_search_proto.Criterion(match=allof_criterion.match, ...)`
        # down below, this is not any more dangerous than that.
        # Plus, using this comparison makes it really easy to stick this (hashable) tuple
        # in a dictionary of additional (field_type, match_type) pairs if/when we find
        # more edge cases like this where we want to tweak the behavior of
        # operators
        if (this_field_type, allof_criterion.match) == (
            "FormattedTimestamp",
            crm_search_proto.Match.MATCH_EQUAL,
        ):
            ge_crit = crm_search_proto.Criterion(
                match=crm_search_proto.Match.MATCH_GREAT_THAN_OR_EQUAL,
                field_name=self.translate_proto_to_crm_dict[this_field_name],
                field_value=self.entity_value_utility.get_ultimate_value(
                    entity=allof_criterion,
                    field_name=this_field_name,
                    field_type=this_field_type,
                    for_search=True,
                ),
            )
            ts_field = getattr(allof_criterion, this_field_name)
            ts_field.value.seconds += 1
            le_crit = crm_search_proto.Criterion(
                match=crm_search_proto.Match.MATCH_LESS_THAN,
                field_name=self.translate_proto_to_crm_dict[this_field_name],
                field_value=self.entity_value_utility.get_ultimate_value(
                    entity=allof_criterion,
                    field_name=this_field_name,
                    field_type=this_field_type,
                    for_search=True,
                ),
            )

            list_of_generic_and_criterion.extend([ge_crit, le_crit])
        else:
            list_of_generic_and_criterion.append(
                crm_search_proto.Criterion(
                    match=allof_criterion.match,
                    field_name=self.translate_proto_to_crm_dict[this_field_name],
                    field_value=self.entity_value_utility.get_ultimate_value(
                        entity=allof_criterion,
                        field_name=this_field_name,
                        field_type=this_field_type,
                        for_search=True,
                    ),
                )
            )

        return list_of_generic_and_criterion

    def specific_to_generic_anyof_criteria(
        self, anyof_criteria: Message, specific_allof_entity_type: Type[Message]
    ) -> crm_search_proto.EntitySearch:
        """Convert mid-tier anyof_criteria (OR'd criteria) into generic CRM search criteria.

        :param anyof_criteria: an OrCriteria message from one of the ordering mid-tier services
        :param specifi_allof_entity_type: the capital T, Type of ordering entity you are searching
            for (eg. AccessLog, NetworkElement)
        """
        list_of_generic_or_criterion = []
        for allof_criterion in anyof_criteria.allof_criteria:
            converted_criteria = self.specific_to_generic_allof_criteria(
                allof_criterion=allof_criterion,
                specific_allof_entity_type=specific_allof_entity_type,
            )
            list_of_generic_or_criterion.extend(converted_criteria)

        return EntitySearch(criterion=list_of_generic_or_criterion)

    def convert_specific_entity_search_message_to_generic_search_message(
        self,
        specific_entity_search: Message,
        specific_allof_entity_type: Message,
    ) -> SearchCrmEntitiesRequest:
        """Convert search request message from a specific mid-tier entity into adapter.

        :param specific_entity_search: a SearchMessage from one of the ordering mid-tier services.
        :param specific_allof_entity_type: an AndCriteria from one of the ordering mid-tier
            services.
        """

        list_of_generic_crm_searches = []
        for anyof_criteria in specific_entity_search.anyof_criteria:
            one_converted_or_criteria = self.specific_to_generic_anyof_criteria(
                anyof_criteria=anyof_criteria,
                specific_allof_entity_type=specific_allof_entity_type,
            )
            list_of_generic_crm_searches.append(one_converted_or_criteria)

        search_request = SearchCrmEntitiesRequest(
            crm_entity_type=self.entity_type,
            limit=specific_entity_search.limit,
            search=list_of_generic_crm_searches,
        )
        if specific_entity_search.return_all:
            search_request.return_all = specific_entity_search.return_all
        else:
            search_request.fields_to_return.CopyFrom(
                crm_search_proto.CrmFieldsToReturn(
                    fields_to_return=[
                        self.translate_proto_to_crm_dict[field]
                        for field in specific_entity_search.fields_to_return.fields_to_return
                    ]
                )
            )

        return search_request

    def generate_formatted_value_and_value_dict(
        self,
        response_fields: RepeatedCompositeFieldContainer[CrmKeyValuePair],
    ) -> dict:
        """Generate a dictionary that we can loop through to associate values and formatted values
        together.

        :param response_fields: a "list" (protobuf version of a list) of CrmKeyValuePairs
        """

        value_dict = defaultdict(dict)
        kvp: CrmKeyValuePair
        for kvp in response_fields:
            key_name, at_sym, format_name = kvp.key.partition("@")

            value_field = kvp.WhichOneof("value_type")
            if value_field is None:
                value = kvp.value
            else:
                value = getattr(kvp, value_field).value

            # we're dealing with a formatted value here
            if at_sym + format_name == self.crm_api_formatted_value_string:
                value_dict[key_name]["formatted_value"] = value
            # were dealing with a regular value here
            else:
                value_dict[kvp.key]["value"] = value
        return value_dict

    def crm_result_to_specific_entity(
        self, specific_entity_type: Type[Message], one_crm_entity_response: CrmEntity
    ):
        """Turn a result from the CRM Adapter into an entity.

        :param specific_entity_type: the capital T, Type of ordering entity you are
            searching for (eg. AccessLog, NetworkElement).
        :param one_crm_entity_response: a CrmEntity that we need to turn into the specific entity
            type in the previous param.
        """

        specific_entity = specific_entity_type()

        # swap key/values for lookups
        # TODO: why are we building this every time?
        crm_to_proto = {
            value: key for key, value in self.translate_proto_to_crm_dict.items()
        }

        all_fields = self.generate_formatted_value_and_value_dict(
            one_crm_entity_response.fields
        )
        for key in all_fields.keys():
            if key not in crm_to_proto:
                continue

            specific_entity_proto_field_name = crm_to_proto[key]
            returned_value = all_fields[key]["value"]
            formatted_value = ""
            if "formatted_value" in all_fields[key]:
                formatted_value = all_fields[key]["formatted_value"]
            field_type = self.get_field_type(
                specific_entity, specific_entity_proto_field_name
            )

            # if there are results in the adapter response that match the crm field name
            # set the entity specific crm value to the api response using
            # translation dictionary
            specific_entity = self.entity_value_utility.set_entity_attribute(
                entity=specific_entity,
                field_name=specific_entity_proto_field_name,
                field_type=field_type,
                new_value=returned_value,
                formatted_value=formatted_value,
            )

        return specific_entity

    def specific_entity_to_generic_crm_entity(
        self,
        specific_entity: Message,
        crud_type: CrudType,
        already_empty_fields: List = None,
    ) -> CrmEntity:
        """Return a CrmEntity from any 'specific' crm entity. The 'guid' field is intentionally
        left out because it is not used in 'create' calls to the adapter.

        :param specific_entity: a copy of an ordering mid-tier "entity (eg. AccessLog,
            NetworkElement, ProvisioningDetail, etc)
        :param crud_type: an Enum of the class CrudType defined above.
        :param already_empty_fields: a list of protobuf field names that describe which fields
            were already empty before proposed update.
        """
        if already_empty_fields is None:
            already_empty_fields = []
        list_of_kvps = self.get_list_of_kvps(
            specific_entity, crud_type, already_empty_fields
        )
        crm_entity = CrmEntity(crm_entity_type=self.entity_type, fields=list_of_kvps)
        return crm_entity

    def build_kvp_with_linked_entity(
        self, field_name: str, field_value: str
    ) -> CrmKeyValuePair:
        """Build a CrmKeyValuePair that has a linked entity.

        :param field_name: the name of the field you want to add to a CrmKeyValuePair
        :param field_value: the value of the field you want to add to a CrmKeyValuePair
        """
        # swap navigation property in for key name
        if self.translate_proto_to_navigation_property.get(field_name) is None:
            raise ValueError(
                f'You have not set a navigation property for "{field_name}" in the generator'
            )
        if self.translate_proto_to_linked_entity.get(field_name) is None:
            raise ValueError(
                f'You have not set a linked entity for "{field_name} in the generator"'
            )
        key = self.translate_proto_to_navigation_property[field_name]

        # Support both single linked_entity type name and a list of names. If a list is provided
        # we assume the first should be used for create/update ops.
        linked_entity = self.translate_proto_to_linked_entity[field_name]
        if type(linked_entity) is list:
            try:
                linked_entity = linked_entity[0]
            except IndexError:
                raise ValueError(
                    f'You have not set a linked entity for "{field_name} in the generator"'
                )
        linked_entity = f"/{linked_entity.lstrip('/')}"

        value = field_value
        kvp = self.create_kvp_with_correct_value_type(key, value)
        kvp.linked_entity = linked_entity
        return kvp

    def build_kvp_for_field_deletion(
        self, field_name: str, field_value: str
    ) -> CrmKeyValuePair:
        """Build KVP for field deletion.

        :param field_name: the name of the field you want to add to a CrmKeyValuePair
        :param field_value: the value of the field you want to add to a CrmKeyValuePair
        """
        key = ""
        value = field_value
        linked_entity = None
        if field_name in self.translate_proto_to_navigation_property:
            key = self.translate_proto_to_navigation_property[field_name]

            # Support both single linked_entity type name and a list of names. If a list is provided
            # we assume the first should be used for create/update ops.
            linked_entity = self.translate_proto_to_linked_entity[field_name]
            if type(linked_entity) is list:
                try:
                    linked_entity = linked_entity[0]
                except IndexError:
                    raise ValueError(
                        f'You have not set a linked entity for "{field_name} in the generator"'
                    )
            linked_entity = f"/{linked_entity.lstrip('/')}"
        else:
            key = self.translate_proto_to_crm_dict[field_name]

        kvp = self.create_kvp_with_correct_value_type(key, value)
        if linked_entity:
            kvp.linked_entity = linked_entity
        return kvp

    def create_kvp_with_correct_value_type(
        self, key: str, field_value
    ) -> CrmKeyValuePair:
        """Set the value of one of the 'value_type' oneof fields of a CrmKeyValuePair.

        :param kvp: a CrmKeyValuePair
        :param field: a field from a protobuf message that we are going to use to determine the type
        of 'value_type' field we want to set on the CrmKeyValuePair
        """
        assignment_dict = {
            "str": ("str_value", StringValue),
            "int": ("int_value", UInt64Value),
            "float": ("float_value", FloatValue),
            "double": ("float_value", DoubleValue),
            "bool": ("bool_value", BoolValue),
        }

        this_type = type(field_value).__name__

        if this_type not in assignment_dict:
            raise ValueError(
                f"In the set_kvp_value_type function in the abc_crm_entity_generator there is not"
                f' a return type set for "{this_type}" in the assignment_dict that is used to'
                f' determine which "value_type" field to set on the CrmKeyValuePair.'
                f' you should also ensure that the "value_type" field has been created'
                f" in the CrmKeyValuePair proto definition."
            )

        oneof_name, google_wrapper_type = assignment_dict.get(this_type)

        kvp = CrmKeyValuePair(
            key=key,
            **{oneof_name: google_wrapper_type(value=field_value)},
            value=str(field_value),
        )
        return kvp

    def build_kvp_regular(self, field_name: str, field_value: str) -> CrmKeyValuePair:
        """Build a CrmKeyValuePair that is 'regular.'

        :param field_name: the name of the field you want to add to a CrmKeyValuePair
        :param field_value: the value of the field you want to add to a CrmKeyValuePair
        """
        key = self.translate_proto_to_crm_dict[field_name]
        value = field_value
        return self.create_kvp_with_correct_value_type(key, value)

    def determine_type_and_build_kvp(
        self, field_name: str, field_value: str
    ) -> CrmKeyValuePair:
        """Determine type and build kvp.

        :param field_name: the name of the field you want to add to a CrmKeyValuePair
        :param field_value: the value of the field you want to add to a CrmKeyValuePair
        """
        # we're building KVP for deletion
        if field_value == "":
            kvp = self.build_kvp_for_field_deletion(
                field_name=field_name, field_value=field_value
            )
        # are we building a linked entity field type?
        elif field_name in self.translate_proto_to_linked_entity:
            kvp = self.build_kvp_with_linked_entity(
                field_name=field_name, field_value=field_value
            )
        # or a regular field type
        else:
            kvp = self.build_kvp_regular(field_name=field_name, field_value=field_value)
        return kvp

    def get_list_of_kvps(
        self,
        specific_entity: Message,
        crud_type: CrudType,
        already_empty_fields: List = None,
        # fields in this param will not be turned into kvps
    ) -> List[CrmKeyValuePair]:
        """Return a list of CrmKeyValuePairs for use in generating a CrmEntity.

        :param specific_entity: a copy of an ordering mid-tier "entity (eg. AccessLog,
            NetworkElement, ProvisioningDetail, etc)
        :param crud_type: an Enum of the class CrudType defined above.
        :param already_empty_fields: a list of protobuf field names that describe which fields
            were already empty before proposed update.
        """
        if already_empty_fields is None:
            already_empty_fields = []
        list_of_kvps = []
        for field_name in self.translate_proto_to_crm_dict:
            # we can't create or update this field value
            protected_fields = (
                self.protected_fields.get(crud_type, [])
                if isinstance(self.protected_fields, dict)
                else self.protected_fields  # backwards-compatibility with List[str]
            )

            if protected_fields and field_name in protected_fields:
                continue

            field_type = self.get_field_type(specific_entity, field_name)
            # drill down into any message type and get the ultimate value we need
            # if no value is returned replace "None" with '' so that the adapter will delete that
            # property
            ultimate_value = self.entity_value_utility.get_ultimate_value(
                specific_entity, field_name, field_type
            )
            if not ultimate_value:
                ultimate_value = ""

            if field_name in self.required_fields and not ultimate_value:
                raise ValueError(
                    f"The field: {field_name} is required and cannot be left blank or deleted"
                )

            # if the field is already empty - dont add it to the list of KVPs
            if field_name in already_empty_fields and ultimate_value == "":
                continue

            kvp = self.determine_type_and_build_kvp(field_name, ultimate_value)
            list_of_kvps.append(kvp)

        return list_of_kvps

    def update(
        self,
        crm_adapter: CrmServiceStub,
        specific_entity: Message,
        specific_entity_guid: str,
        already_empty_fields: List,
        existing_entity: Optional[Message] = None,
    ):
        """Create a specific entity.

        :param crm_adapter: a service stub for access to calls into the crm_adapter
        :param specific_entity_type: the capital T, Type of ordering entity you are searching for
            (eg. AccessLog, NetworkElement)
        :param specific_entity_guid: a string representation of the GUID of the crm item you are
            updating.
        :param already_empty_fields: a flat list of fields that were already empty before
            attempting the update. Field names should be protobuf fields names - not crm field
            names.
        :param existing_entity: Existing instance of the ordering message to be updated. Used to
            filter unchanged fields.
        """

        crm_entity = self.specific_entity_to_generic_crm_entity(
            specific_entity=specific_entity,
            crud_type=CrudType.UPDATE,
            already_empty_fields=already_empty_fields,
        )

        if existing_entity is not None:
            # Filter unchanged values
            existing_crm_entity = self.specific_entity_to_generic_crm_entity(
                specific_entity=existing_entity,
                crud_type=CrudType.UPDATE,
                already_empty_fields=already_empty_fields,
            )

            existing_crm_entity_fields = set()
            for field in existing_crm_entity.fields:
                field_type = field.WhichOneof("value_type")
                field_value = getattr(field, field_type).value
                existing_crm_entity_fields.add((field.key, field_value))

            update_fields = []
            for field in crm_entity.fields:
                field_type = field.WhichOneof("value_type")
                field_value = getattr(field, field_type).value
                if (field.key, field_value) not in existing_crm_entity_fields:
                    update_fields.append(field)

            crm_entity.ClearField("fields")
            crm_entity.fields.extend(update_fields)

            if update_fields == []:
                return existing_entity

        crm_entity.guid.CopyFrom(FormattedGuid(value=specific_entity_guid))
        crm_adapter_response = crm_adapter.UpdateCrmEntity(
            UpdateCrmEntityRequest(entity=crm_entity)
        )
        new_specific_entity = self.crm_result_to_specific_entity(
            one_crm_entity_response=crm_adapter_response.entity,
            specific_entity_type=type(specific_entity),
        )

        return new_specific_entity

    def search(
        self,
        crm_adapter: CrmServiceStub,
        search: Message,
        specific_entity_type: Type[Message],
    ):
        """Search for an entity.

        :param crm_adapter: a service stub for access to calls into the crm_adapter
        :param search: A search Message from one of the ordering midtier services.
        :param specific_entity_type: the capital T, Type of ordering entity you are searching
            for (eg. AccessLog, NetworkElement)
        """

        invalid_fields = set(search.fields_to_return.fields_to_return) - set(
            self.full_proto_to_linked_entity
        )
        if len(invalid_fields) > 0:
            raise ValueError(f"Invalid fields to return: {','.join(invalid_fields)}")

        api_search = (
            self.convert_specific_entity_search_message_to_generic_search_message(
                specific_entity_search=search,
                specific_allof_entity_type=specific_entity_type,
            )
        )

        def remove_single_quotes(string):
            return re.sub("^'|'$", "", string)

        # hack around bug in search-generator where the guid field "id" is
        # interpreted as a string by removing single quotes from field_value
        for search in api_search.search:
            for criterion in search.criterion:
                if criterion.field_name == self.entity_guid_field:
                    criterion.field_value = remove_single_quotes(criterion.field_value)

        return crm_adapter.SearchCrmEntities(api_search)

    def create(
        self,
        crm_adapter: CrmServiceStub,
        specific_entity: Type[Message],
    ):
        """Create a specific entity.

        :param crm_adapter: a service stub for access to calls into the crm_adapter
        :param specific_entity_type: the capital T, Type of ordering entity you are searching '
            for (eg. AccessLog, NetworkElement)
        """

        crm_entity = self.specific_entity_to_generic_crm_entity(
            specific_entity=specific_entity, crud_type=CrudType.CREATE
        )
        crm_adapter_response = crm_adapter.CreateCrmEntity(
            CreateCrmEntityRequest(entity=crm_entity)
        )
        new_specific_entity = self.crm_result_to_specific_entity(
            one_crm_entity_response=crm_adapter_response.entity,
            specific_entity_type=type(specific_entity),
        )
        return new_specific_entity
