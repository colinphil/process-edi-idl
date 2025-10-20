$version: "2"

namespace com.colinleephillips.process.edi

use smithy.api#Documentation
use smithy.api#Error
use smithy.api#Http
use smithy.api#HttpError
use smithy.api#HttpPayload
use smithy.api#HttpResponseCode
use smithy.api#Operation
use smithy.api#Service
use smithy.api#TimestampFormat
use smithy.api#Trait
use smithy.api#Unit

/// Generic EDI Processing Service
/// This service provides a unified API for processing multiple EDI message types.
/// It supports:
/// - Multiple EDI Types: 850 (Purchase Order), 810 (Invoice), 856 (Advance Ship Notice), 997 (Functional Acknowledgment), and more
/// - Unified API: Single service interface for all EDI message types
/// - Extensible Design: Easy to add new EDI message types
@Http(method: "POST", uri: "/edi/process")
@Documentation("Generic EDI Processing Service")
service EdiService {
    version: "2024-01-01"
    operations: [
        ProcessEdiMessage
        GetSupportedMessageTypes
        ValidateEdiMessage
    ]
    errors: [
        ValidationError
        ParsingError
        BusinessRuleError
        UnsupportedMessageTypeError
        InternalError
    ]
}

/// Process any EDI message type
@Operation
@Http(method: "POST", uri: "/edi/process")
operation ProcessEdiMessage {
    input: ProcessEdiMessageRequest
    output: ProcessEdiMessageResponse
    errors: [
        ValidationError
        ParsingError
        BusinessRuleError
        UnsupportedMessageTypeError
        InternalError
    ]
}

/// Get supported EDI message types
@Operation
@Http(method: "GET", uri: "/edi/supported-types")
operation GetSupportedMessageTypes {
    input: GetSupportedMessageTypesRequest
    output: GetSupportedMessageTypesResponse
}

/// Validate EDI message format without processing
@Operation
@Http(method: "POST", uri: "/edi/validate")
operation ValidateEdiMessage {
    input: ValidateEdiMessageRequest
    output: ValidateEdiMessageResponse
    errors: [
        ValidationError
        ParsingError
    ]
}

/// Request message for processing any EDI message
structure ProcessEdiMessageRequest {
    /// The raw EDI message content
    @required
    @HttpPayload
    ediMessage: String

    /// EDI message type (e.g., "850", "810", "856", "997")
    @required
    messageType: String

    /// Optional: Customer/partner identifier
    customerId: String

    /// Optional: Processing options
    options: ProcessingOptions

    /// Optional: Message-specific processing parameters
    parameters: ProcessingParameters
}

/// Response message for EDI processing
structure ProcessEdiMessageResponse {
    /// Processing status
    @required
    status: ProcessingStatus

    /// EDI message type that was processed
    @required
    messageType: String

    /// Parsed EDI data (oneof to support different message types)
    purchaseOrder: PurchaseOrderData
    invoice: InvoiceData
    advanceShipNotice: AdvanceShipNoticeData
    functionalAcknowledgment: FunctionalAcknowledgmentData

    /// Processing messages/errors
    messages: ProcessingMessageList

    /// Processing timestamp
    @required
    @timestampFormat(TimestampFormat.DATE_TIME)
    processedAt: Timestamp

    /// Raw parsed segments (for debugging/audit)
    parsedSegments: EdiSegmentList
}

/// Request for getting supported message types
structure GetSupportedMessageTypesRequest {
    /// Optional: Filter by customer/partner
    customerId: String
}

/// Response with supported message types
structure GetSupportedMessageTypesResponse {
    /// List of supported EDI message types
    @required
    supportedTypes: EdiMessageTypeList
}

/// Request for validating EDI message format
structure ValidateEdiMessageRequest {
    /// The raw EDI message content
    @required
    @HttpPayload
    ediMessage: String

    /// EDI message type
    @required
    messageType: String

    /// Optional: Customer/partner identifier
    customerId: String
}

/// Response for EDI message validation
structure ValidateEdiMessageResponse {
    /// Validation status
    @required
    status: ProcessingStatus

    /// Validation messages
    messages: ProcessingMessageList

    /// Detected EDI version (e.g., "005010", "004010")
    ediVersion: String

    /// Detected message type
    detectedMessageType: String
}

/// Processing options for EDI messages
structure ProcessingOptions {
    /// Whether to validate the EDI format
    validateFormat: Boolean

    /// Whether to perform business rule validation
    validateBusinessRules: Boolean

    /// Whether to return detailed parsing information
    includeParsingDetails: Boolean

    /// Whether to return raw parsed segments
    includeRawSegments: Boolean

    /// Target processing environment
    environment: String

    /// Message-specific validation rules
    validationRules: ProcessingParameters
}

/// Processing status enumeration
@Documentation("Processing status enumeration")
enum ProcessingStatus {
    SUCCESS = "SUCCESS"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    PARSING_ERROR = "PARSING_ERROR"
    BUSINESS_RULE_ERROR = "BUSINESS_RULE_ERROR"
    UNSUPPORTED_MESSAGE_TYPE = "UNSUPPORTED_MESSAGE_TYPE"
    INTERNAL_ERROR = "INTERNAL_ERROR"
}

/// Processing message for errors or warnings
structure ProcessingMessage {
    /// Message level
    @required
    level: MessageLevel

    /// Message code
    @required
    code: String

    /// Human-readable message
    @required
    message: String

    /// Optional: Field or segment that caused the issue
    field: String

    /// Optional: Line number in the EDI message
    lineNumber: Integer

    /// Optional: Element position within segment
    elementPosition: Integer
}

/// Message level enumeration
@Documentation("Message level enumeration")
enum MessageLevel {
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
}

/// Generic EDI Segment representation
structure EdiSegment {
    /// Segment identifier (e.g., "ISA", "BEG", "PO1")
    @required
    segmentId: String

    /// Segment elements
    @required
    elements: StringList

    /// Line number in the original message
    lineNumber: Integer

    /// Segment position in the message
    position: Integer
}

/// EDI Message Type information
structure EdiMessageType {
    /// Message type code (e.g., "850", "810")
    @required
    code: String

    /// Human-readable name
    @required
    name: String

    /// Description of the message type
    @required
    description: String

    /// Whether this message type is supported
    @required
    supported: Boolean

    /// Required segments for this message type
    requiredSegments: StringList

    /// Optional segments for this message type
    optionalSegments: StringList
}

/// Common EDI data structures that can be reused across message types

/// Party information (used in multiple EDI types)
structure Party {
    /// Entity identifier code
    entityIdentifierCode: String

    /// Name
    name: String

    /// Identification number
    identificationNumber: String

    /// Address
    address: Address

    /// Contact information
    contact: Contact
}

/// Address information
structure Address {
    /// Address line 1
    addressLine1: String

    /// Address line 2
    addressLine2: String

    /// City
    city: String

    /// State or province
    stateProvince: String

    /// Postal code
    postalCode: String

    /// Country code
    countryCode: String
}

/// Contact information
structure Contact {
    /// Contact name
    name: String

    /// Phone number
    phone: String

    /// Email address
    email: String

    /// Fax number
    fax: String
}

/// Product information
structure Product {
    /// Product identifier
    productId: String

    /// Product description
    description: String

    /// Product identifier type (e.g., "SKU", "UPC", "ISBN")
    identifierType: String

    /// Manufacturer part number
    manufacturerPartNumber: String

    /// Brand name
    brandName: String
}

/// Quantity information
structure Quantity {
    /// Quantity value
    @required
    value: Double

    /// Unit of measure code
    unitOfMeasure: String

    /// Unit of measure description
    unitOfMeasureDescription: String
}

/// Price information
structure Price {
    /// Price value
    @required
    value: Double

    /// Currency code
    currencyCode: String

    /// Price basis code
    priceBasisCode: String
}

/// Reference number information
structure ReferenceNumber {
    /// Reference number type
    @required
    referenceType: String

    /// Reference number value
    @required
    referenceValue: String

    /// Reference number description
    description: String
}

/// Date/time information
structure DateTime {
    /// Date in YYYY-MM-DD format
    date: String

    /// Time in HH:MM:SS format
    time: String

    /// Time zone
    timezone: String

    /// Date/time qualifier
    qualifier: String
}

/// Monetary amounts summary
structure MonetaryAmounts {
    /// Total amount
    totalAmount: Price

    /// Tax amount
    taxAmount: Price

    /// Freight amount
    freightAmount: Price

    /// Discount amount
    discountAmount: Price

    /// Terms discount amount
    termsDiscountAmount: Price

    /// Additional amounts (flexible for different message types)
    additionalAmounts: ProcessingParameters
}

/// Line item information (generic for different EDI types)
structure LineItem {
    /// Line item number
    @required
    lineNumber: String

    /// Product/service information
    product: Product

    /// Quantity information
    quantity: Quantity

    /// Price information
    price: Price

    /// Extended price
    extendedPrice: Price

    /// Dates associated with this line item
    dates: ProcessingParameters

    /// Additional line item notes
    notes: StringList

    /// Line item specific data (flexible for different message types)
    additionalData: ProcessingParameters
}

/// Error definitions
@Error("client")
@HttpError(400)
structure ValidationError {
    @required
    message: String
    code: String
    field: String
    lineNumber: Integer
}

@Error("client")
@HttpError(400)
structure ParsingError {
    @required
    message: String
    code: String
    field: String
    lineNumber: Integer
}

@Error("client")
@HttpError(422)
structure BusinessRuleError {
    @required
    message: String
    code: String
    field: String
    lineNumber: Integer
}

@Error("client")
@HttpError(415)
structure UnsupportedMessageTypeError {
    @required
    message: String
    code: String
    messageType: String
}

@Error("server")
@HttpError(500)
structure InternalError {
    @required
    message: String
    code: String
}

/// List types
list ProcessingMessageList {
    member: ProcessingMessage
}

list EdiSegmentList {
    member: EdiSegment
}

list EdiMessageTypeList {
    member: EdiMessageType
}

list StringList {
    member: String
}

/// Map type for flexible parameters
map ProcessingParameters {
    key: String
    value: String
}
