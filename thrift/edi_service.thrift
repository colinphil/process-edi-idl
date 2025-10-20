/**
 * EDI Service Definition
 * 
 * This file contains the main service definition for the EDI processing service,
 * including all operations and their request/response structures.
 */

include "edi_types.thrift"
include "edi_exceptions.thrift"

namespace java com.colinleephillips.process.edi.thrift
namespace py com.colinleephillips.process.edi.thrift
namespace go com.colinleephillips.process.edi.thrift

// ============================================================================
// Request/Response Structures
// ============================================================================

/**
 * Request message for processing any EDI message
 */
struct ProcessEdiMessageRequest {
    1: required string ediMessage,
    2: required string messageType,
    3: optional string customerId,
    4: optional ProcessingOptions options,
    5: optional map<string, string> parameters
}

/**
 * Response message for EDI processing
 */
struct ProcessEdiMessageResponse {
    1: required ProcessingStatus status,
    2: required string messageType,
    3: optional PurchaseOrderData purchaseOrder,
    4: optional InvoiceData invoice,
    5: optional AdvanceShipNoticeData advanceShipNotice,
    6: optional FunctionalAcknowledgmentData functionalAcknowledgment,
    7: optional list<ProcessingMessage> messages,
    8: required i64 processedAt,
    9: optional list<EdiSegment> parsedSegments
}

/**
 * Request for getting supported message types
 */
struct GetSupportedMessageTypesRequest {
    1: optional string customerId
}

/**
 * Response with supported message types
 */
struct GetSupportedMessageTypesResponse {
    1: required list<EdiMessageType> supportedTypes
}

/**
 * Request for validating EDI message format
 */
struct ValidateEdiMessageRequest {
    1: required string ediMessage,
    2: required string messageType,
    3: optional string customerId
}

/**
 * Response for EDI message validation
 */
struct ValidateEdiMessageResponse {
    1: required ProcessingStatus status,
    2: optional list<ProcessingMessage> messages,
    3: optional string ediVersion,
    4: optional string detectedMessageType
}

// ============================================================================
// Service Definition
// ============================================================================

/**
 * Generic EDI Processing Service
 * 
 * This service provides a unified API for processing multiple EDI message types.
 * It supports:
 * - Multiple EDI Types: 850 (Purchase Order), 810 (Invoice), 856 (Advance Ship Notice), 997 (Functional Acknowledgment), and more
 * - Unified API: Single service interface for all EDI message types
 * - Extensible Design: Easy to add new EDI message types
 */
service EdiService {
    
    /**
     * Process any EDI message type
     * 
     * This operation processes EDI messages of any supported type and returns
     * the parsed data in a structured format. The response includes the parsed
     * data specific to the message type, along with processing status and any
     * validation messages.
     * 
     * @param request The EDI message processing request
     * @return ProcessEdiMessageResponse containing parsed data and processing status
     * @throws ValidationError if the EDI message format is invalid
     * @throws ParsingError if the EDI message cannot be parsed
     * @throws BusinessRuleError if business rules are violated
     * @throws UnsupportedMessageTypeError if the message type is not supported
     * @throws InternalError if an internal server error occurs
     */
    ProcessEdiMessageResponse processEdiMessage(1: ProcessEdiMessageRequest request)
        throws (
            1: ValidationError validationError,
            2: ParsingError parsingError,
            3: BusinessRuleError businessRuleError,
            4: UnsupportedMessageTypeError unsupportedMessageTypeError,
            5: InternalError internalError
        );
    
    /**
     * Get supported EDI message types
     * 
     * This operation returns a list of all EDI message types supported by the service,
     * along with their descriptions and requirements. Optionally filtered by customer.
     * 
     * @param request The request for supported message types
     * @return GetSupportedMessageTypesResponse containing list of supported types
     */
    GetSupportedMessageTypesResponse getSupportedMessageTypes(1: GetSupportedMessageTypesRequest request);
    
    /**
     * Validate EDI message format without processing
     * 
     * This operation validates the format of an EDI message without performing
     * full processing. Useful for format validation before actual processing.
     * 
     * @param request The EDI message validation request
     * @return ValidateEdiMessageResponse containing validation status and messages
     * @throws ValidationError if the EDI message format is invalid
     * @throws ParsingError if the EDI message cannot be parsed
     */
    ValidateEdiMessageResponse validateEdiMessage(1: ValidateEdiMessageRequest request)
        throws (
            1: ValidationError validationError,
            2: ParsingError parsingError
        );
}
