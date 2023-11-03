"""Subclass EntityGenerator."""
from typing import List, Dict, Tuple
from crm_entity_generator.protos import (
    AccessLogType,
    AccessLogStatus,
    CompletedAsDesigned,
    WorkRelatedStatus,
    Contact,
    CrmEntity,
    ContactType,
    ContactStatus,
)
from crm_entity_generator.entity_value_utility import EntityValueUtility
from crm_entity_generator.entity_generation import EntityGenerator


class AssignmentValueUtility(EntityValueUtility):
    """Subclasses EntityValueUtility to add custom methods to get/set values for Assignment."""


class AccessLogValueUtility(EntityValueUtility):
    """Subclass EntityValueUtility add custom methods to get/set this specific entities values."""

    @classmethod
    def from_type_AccessLogType(cls, entity_field_obj) -> str:
        """Get value of AccessLogType."""
        if entity_field_obj.type != 0:
            return str(entity_field_obj.type)

    @classmethod
    def set_type_AccessLogType(
        cls, entity, field_name, new_value, formatted_value
    ) -> str:
        """Set the value of AccessLogType."""
        ac_type = AccessLogType(type=int(new_value), formatted_value=formatted_value)
        getattr(entity, field_name).CopyFrom(ac_type)
        return entity

    @classmethod
    def from_type_AccessLogStatus(cls, entity_field_obj) -> str:
        """Get the value of AccessLogStatus."""
        if entity_field_obj.status != 0:
            return str(entity_field_obj.status)

    @classmethod
    def set_type_AccessLogStatus(
        cls, entity, field_name, new_value, formatted_value
    ) -> str:
        """Set the value of AccessLogStatus."""
        ac_status = AccessLogStatus(
            status=int(new_value), formatted_value=formatted_value
        )
        getattr(entity, field_name).CopyFrom(ac_status)
        return entity

    @classmethod
    def from_type_WorkRelatedStatus(cls, entity_field_obj) -> str:
        """Get the value of WorkRelatedStatus."""
        if entity_field_obj.status != 0:
            return str(entity_field_obj.status)

    @classmethod
    def set_type_WorkRelatedStatus(
        cls, entity, field_name, new_value, formatted_value
    ) -> str:
        """Set the value of WorkRelatedStatus."""
        status = WorkRelatedStatus(
            status=int(new_value), formatted_value=formatted_value
        )
        getattr(entity, field_name).CopyFrom(status)
        return entity

    @classmethod
    def from_type_CompletedAsDesigned(cls, entity_field_obj) -> str:
        """Get the value of CompletedAsDesigned."""
        if entity_field_obj.status != 0:
            return str(entity_field_obj.status)

    @classmethod
    def set_type_CompletedAsDesigned(
        cls, entity, field_name, new_value, formatted_value
    ) -> str:
        """Set the value of CompletedAsDesigned."""
        ac_status = CompletedAsDesigned(
            status=int(new_value), formatted_value=formatted_value
        )
        getattr(entity, field_name).CopyFrom(ac_status)
        return entity


class ContactValueUtility(EntityValueUtility):
    """Subclass EntityValueUtility add custom methods to get/set this specific entities values."""

    @classmethod
    def from_type_ContactType(cls, entity_field_obj) -> str:
        """Get value of AccessLogType."""
        if entity_field_obj.type != 0:
            return str(entity_field_obj.type)

    @classmethod
    def set_type_ContactType(
        cls, entity, field_name, new_value, formatted_value
    ) -> str:
        """Set the value of AccessLogType."""
        translate_dict = {
            0: ContactType.TYPE_UNSPECIFIED,
            1: ContactType.TYPE_ACCOUNT_CONTACT,
            2: ContactType.TYPE_LOCAL_CONTACT,
            3: ContactType.TYPE_SYSTEM_CONTACT,
            4: ContactType.TYPE_VENDOR_CONTACT,
            5: ContactType.TYPE_BOOKABLE_RESOURCE,
        }
        ac_type = ContactType(
            type=translate_dict[int(new_value)], formatted_value=formatted_value
        )
        getattr(entity, field_name).CopyFrom(ac_type)
        return entity

    @classmethod
    def from_type_ContactStatus(cls, entity_field_obj) -> str:
        """Get the value of AccessLogStatus."""
        if entity_field_obj.status != 0:
            return str(entity_field_obj.status)

    @classmethod
    def set_type_ContactStatus(
        cls, entity, field_name, new_value, formatted_value
    ) -> str:
        """Set the value of AccessLogStatus."""
        translate_dict = {
            0: ContactStatus.STATUS_UNSPECIFIED,
            1: ContactStatus.STATUS_ACTIVE,
            2: ContactStatus.STATUS_INACTIVE,
        }
        ac_status = ContactStatus(
            status=translate_dict[int(new_value)], formatted_value=formatted_value
        )
        getattr(entity, field_name).CopyFrom(ac_status)
        return entity


class ContactGenerator(EntityGenerator):
    """Subclass of EntityGenerator. Customizations go here."""

    entity_value_utility = ContactValueUtility()
    entity_type: str = "contacts"
    entity_guid_field: str = "new_contactnumber"
    crm_creation_source_value: str = "100000011"
    required_fields: List[str] = [
        "first_name",
        "last_name",
        "email",
        "contact_type",
        "owner_id",
    ]
    protected_fields: List[str] = ["owner_id"]
    translation_compendium: List[Tuple] = [
        # protobuf field, crm field, navigation crm field, linked entity
        ("id", "contactid", None, None),
        ("first_name", "firstname", None, None),
        ("last_name", "lastname", None, None),
        ("job_title", "jobtitle", None, None),
        ("contact_number", "new_contactnumber", None, None),
        ("business_phone_1", "telephone1", None, None),
        ("business_phone_2", "new_businessphone2", None, None),
        ("mobile_phone", "mobilephone", None, None),
        ("home_phone", "telephone2", None, None),
        ("email", "emailaddress1", None, None),
        ("contact_type", "new_contacttype", None, None),
        ("owner_id", "_ownerid_value", "ownerid", "systemusers"),
        ("contact_status", "new_contactstatus", None, None),
        # this field will be added in a future update - left here to avoid having to look up
        # the names in CRM again
        # (
        #    "account",
        #    "_parentcustomerid_value",
        #    "parentcustomerid_contact",
        #    "contacts",
        # ),  # this is supposed to be linked to both "accounts" and "contact"s
    ]
    full_proto_to_linked_entity: Dict[str, str] = {
        proto: linked_entity for (proto, _, _, linked_entity) in translation_compendium
    }
    # removes 'None' values
    translate_proto_to_linked_entity: Dict[str, str] = {
        key: value
        for key, value in full_proto_to_linked_entity.items()
        if value is not None
    }
    full_proto_to_navigation_property: Dict[str, str] = {
        proto: navigation_prop
        for (proto, _, navigation_prop, _) in translation_compendium
    }
    # removes 'None' values
    translate_proto_to_navigation_property: Dict[str, str] = {
        key: value
        for key, value in full_proto_to_navigation_property.items()
        if value is not None
    }

    full_proto_to_crm_dict: Dict[str, str] = {
        proto: crm_field for (proto, crm_field, _, _) in translation_compendium
    }
    # removes 'None' values
    translate_proto_to_crm_dict: Dict[str, str] = {
        key: value for key, value in full_proto_to_crm_dict.items() if value is not None
    }

    def get_already_empty_fields(self, existing_entity: Contact) -> List:
        """Get a list of already empty fields on an existing Contact."""
        already_blank_fields = []
        for field in self.translate_proto_to_crm_dict:
            field_type = self.get_field_type(existing_entity, field)
            existing_entity_value = self.entity_value_utility.get_ultimate_value(
                entity=existing_entity, field_name=field, field_type=field_type
            )
            if existing_entity_value == "":
                already_blank_fields.append(field)
        return already_blank_fields

    def update_contact(
        self,
        crm_adapter,
        existing_entity: Contact,
        updated_entity: Contact,
        entity_guid: str,
    ) -> Contact:
        """Update a Contact."""
        already_empty_fields = self.get_already_empty_fields(existing_entity)
        contact = super().update(
            crm_adapter=crm_adapter,
            specific_entity=updated_entity,
            specific_entity_guid=entity_guid,
            already_empty_fields=already_empty_fields,
        )
        return contact

    def crm_result_to_contact(
        self,
        one_crm_entity_response: CrmEntity,
    ) -> Contact:
        """Convert a CrmEntity to a Contact."""
        if one_crm_entity_response.crm_entity_type != self.entity_type:
            raise Exception(
                f"You are trying to search through: '{one_crm_entity_response.crm_entity_type}'"
                f" in a generator that uses: '{self.entity_type}' "
            )
        return super().crm_result_to_specific_entity(
            one_crm_entity_response=one_crm_entity_response,
            specific_entity_type=Contact,
        )


class AssignmentGenerator(EntityGenerator):
    """Subclass of EntityGenerator for Assignment."""

    entity_value_utility = AssignmentValueUtility()
    entity_type: str = "new_assignmentses"
    entity_guid_field: str = "new_assignmentsid"
    crm_creation_source_value: str = "100000011"
    required_fields: List[str] = [
        # add required fields here - make sure to add them to the "test_required_fields"
        # test, which is located in "test_assignment_generator.py"
    ]
    protected_fields: List[str] = []
    translation_compendium: List[Tuple] = [
        # protobuf field, crm field, navigation crm field, linked entity
        (
            "id",
            "new_assignmentsid",
            None,
            None,
        ),
        (
            "assignment_number",
            "new_assignmentnumber",
            None,
            None,
        ),
        (
            "summary",
            "new_assignmentsummary",
            None,
            None,
        ),
        (
            "assignment_type",
            "new_assignmenttype",
            None,
            None,
        ),
        (
            "assignment_status",
            "new_assignmentstatus",
            None,
            None,
        ),
        (
            "start_date",
            "new_assignmentstartdate",
            None,
            None,
        ),
        (
            "assignment_priority",
            "new_assignmentpriority",
            None,
            None,
        ),
        (
            "owner_id",
            "_ownerid_value",
            "OwnerId",
            ["systemuser"],
        ),
        (
            "assignment_department",
            "new_assignmentdepartment",
            None,
            None,
        ),
        (
            "initial_comment",
            "new_initialcomment",
            None,
            None,
        ),
        (
            "comments",
            "new_comments",
            None,
            None,
        ),
        (
            "comment_append",
            "new_commentappend",
            None,
            None,
        ),
        (
            "notes",
            "new_notes",
            None,
            None,
        ),
        (
            "location_aid",
            "_new_locationaid_value",
            "new_LocationAId",
            ["new_location"],
        ),
        (
            "building_aid",
            "_new_buildingaid_value",
            "new_buildingaid",
            ["new_building"],
        ),
        (
            "created_by",
            "_createdby_value",
            "CreatedBy",
            ["systemuser"],
        ),
        (
            "created_at",
            "createdon",
            None,
            None,
        ),
        (
            "modified_by",
            "_modifiedby_value",
            "ModifiedBy",
            ["systemuser"],
        ),
        (
            "modified_at",
            "modifiedon",
            None,
            None,
        ),
        (
            "completed_at",
            "new_assignmentcompleteddate",
            None,
            None,
        ),
    ]
    full_proto_to_linked_entity: Dict[str, str] = {
        proto: linked_entity for (proto, _, _, linked_entity) in translation_compendium
    }
    # removes "None" values
    translate_proto_to_linked_entity: Dict[str, str] = {
        key: value
        for key, value in full_proto_to_linked_entity.items()
        if value is not None
    }
    full_proto_to_navigation_property: Dict[str, str] = {
        proto: navigation_prop
        for (proto, _, navigation_prop, _) in translation_compendium
    }
    # removes "None" values
    translate_proto_to_navigation_property: Dict[str, str] = {
        key: value
        for key, value in full_proto_to_navigation_property.items()
        if value is not None
    }
    full_proto_to_crm_dict: Dict[str, str] = {
        proto: crm_field for (proto, crm_field, _, _) in translation_compendium
    }
    # removes "None" values
    translate_proto_to_crm_dict: Dict[str, str] = {
        key: value for key, value in full_proto_to_crm_dict.items() if value is not None
    }


class AccessLogGenerator(EntityGenerator):
    """Subclass of EntityGenerator. Customizations go here."""

    entity_value_utility = AccessLogValueUtility()
    entity_type: str = "new_accesslogs"
    entity_guid_field: str = "new_accesslogid"
    crm_creation_source_value: str = "100000011"
    required_fields: List[str] = [
        "access_log_type",
        "start_date_and_time",
        "access_log_status",
        "contact_phone",
        "company_name",
        "first_name",
        "last_name",
        "state_work_is_in",
        "work_region",
        "address_or_cross_street",
    ]
    translate_proto_to_linked_entity: Dict[str, str] = {
        "state_work_is_in": "/new_states",
        "change_management_guid": "/new_changemanagements",
        "service_number_guid": "/new_ltservices",
        "work_order_guid": "/new_internalworkorder",
        "preventative_maintenance_guid": "/new_preventativemaintenances",
        "assignment_guid": "/new_assignmentses",
        "location_guid": "/new_locations",
        "noc_ticket_guid": "/new_nocticketings",
        "created_by_guid": "/systemusers",
    }
    translate_proto_to_navigation_property: Dict[str, str] = {
        "state_work_is_in": "new_StateWorkIsInid",
        "change_management_guid": "new_ChangeManagementId",
        "service_number_guid": "new_ServiceId",
        "work_order_guid": "new_InternalWorkOrderId",
        "preventative_maintenance_guid": "new_PreventativeMaintenanceId",
        "assignment_guid": "new_AssignmentId",
        "location_guid": "new_LocationId",
        "noc_ticket_guid": "new_NocTicketId",
        "created_by_guid": "new_CreatedonBehalf",
    }
    translate_proto_to_crm_dict: Dict[str, str] = {
        "id": "new_accesslogid",
        "access_log_number": "new_accesslognumber",
        "access_log_type": "new_accesslogtype",
        "start_date_and_time": "new_startdateandtime",
        "end_date_and_time": "new_enddateandtime",
        "created_on": "createdon",
        "access_log_status": "new_accesslogstatus",
        "enclosure_name": "new_enclosurename",
        "span_id": "new_spanid",
        "netcracker_equipment_name": "new_netcrackerequipmentname",
        "contact_email": "new_contactemail",
        "contact_name": "new_contact_name",
        "contact_phone": "new_contactphone",
        "company_name": "new_companyname",
        "first_name": "new_firstname",
        "last_name": "new_lastname",
        "service_number_guid": "_new_serviceid_value",
        "owning_team_guid": "_owningteam_value",
        "created_by_guid": "_createdonbehalfby_value",
        "owning_business_unit_guid": "_owning_businessunit_value",
        "noc_ticket_guid": "_new_nocticetid_value",
        "owning_user_guid": "_owninguser_value",
        "change_management_guid": "_new_changemanagementid_value",
        "location_guid": "_new_locationid_value",
        "state_work_is_in": "_new_stateworkisinid_value",
        "user_guid": "_new_crmuserid_value",
        "account_guid": "_new_accountid_value",
        "vendor_guid": "_new_vendorid_value",
        "preventative_maintenance_guid": "_new_preventativemaintenanceid_value",
        "work_region": "new_workregion",
        "notes": "new_notes",
        "description": "new_description",
        "other": "new_other",
        "ospi_notes": "new_associatedospiinformation",
        "address_or_cross_street": "new_addressorcrossstreetofwork",
        "county": "new_county",
        "completed_as_designed": "new_completedasdesigned",
        "work_related_status": "new_workrelatedstatus",
        "creation_source": "new_creationsource",
    }
