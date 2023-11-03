"""Proto imports."""
# pylama:ignore=W0611, E402

# ordering common
import abc.ordering.common.v1.core_pb2 as ordering_common_proto

# Timestamp import
import google.protobuf.timestamp_pb2 as timestamp_proto

# AccessLog imports
import abc.ordering.access_log.v1.core_pb2 as access_log_core_proto
import abc.ordering.access_log.v1.search_pb2 as access_log_search_proto
import abc.ordering.access_log.v1.access_log_service_pb2 as access_log_service

# Assignment Imports
import abc.ordering.assignment.v1.search_pb2 as assignment_search
import abc.ordering.assignment.v1.assignment_service_pb2 as assignment_service

# Adapter imports
import abc.adapter.crm.v1.core_pb2 as crm_core_proto
import abc.adapter.crm.v1.search_pb2 as crm_search_proto
from abc.adapter.crm.v1.crm_service_pb2 import (
    CreateCrmEntityRequest,
    CreateCrmEntityResponse,
    UpdateCrmEntityRequest,
    UpdateCrmEntityResponse,
    SearchCrmEntitiesRequest,
    SearchCrmEntitiesResponse,
)
from abc.adapter.crm.v1.crm_service_pb2_grpc import CrmServiceStub

import abc.ordering.contact.v1.core_pb2 as contact_core_proto
import abc.ordering.contact.v1.search_pb2 as contact_search_proto
import abc.ordering.contact.v1.contact_service_pb2 as contact_service

Contact = contact_core_proto.Contact
ContactType = Contact.ContactType
ContactStatus = Contact.ContactStatus

AccessLog = access_log_core_proto.AccessLog
AccessLogType = access_log_core_proto.AccessLog.AccessLogType
AccessLogStatus = access_log_core_proto.AccessLog.AccessLogStatus
CompletedAsDesigned = access_log_core_proto.AccessLog.CompletedAsDesigned
WorkRelatedStatus = access_log_core_proto.AccessLog.WorkRelatedStatus

# Convenience names
FormattedTimestamp = crm_core_proto.FormattedTimestamp
FormattedInt = crm_core_proto.FormattedInt
FormattedGuid = crm_core_proto.FormattedGuid
FormattedStr = crm_core_proto.FormattedStr
# Timestamp
Timestamp = timestamp_proto.Timestamp
# CRM CORE & SEARCH
CrmEntity = crm_core_proto.CrmEntity
CrmKeyValuePair = crm_core_proto.CrmKeyValuePair
EntitySearch = crm_search_proto.EntitySearch
# ORDERING COMMON
WorkRegion = ordering_common_proto.WorkRegion
CreationSource = ordering_common_proto.CreationSource
