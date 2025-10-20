/**
 * EDI Message Types and Common Structures
 * 
 * This file contains all the type definitions for EDI message processing,
 * including common structures used across different EDI message types.
 */

namespace java com.colinleephillips.process.edi.thrift
namespace py com.colinleephillips.process.edi.thrift
namespace go com.colinleephillips.process.edi.thrift

// ============================================================================
// Enumerations
// ============================================================================

/**
 * Processing status enumeration
 */
enum ProcessingStatus {
    SUCCESS = 1,
    VALIDATION_ERROR = 2,
    PARSING_ERROR = 3,
    BUSINESS_RULE_ERROR = 4,
    UNSUPPORTED_MESSAGE_TYPE = 5,
    INTERNAL_ERROR = 6
}

/**
 * Message level enumeration
 */
enum MessageLevel {
    INFO = 1,
    WARNING = 2,
    ERROR = 3
}

// ============================================================================
// Common Structures
// ============================================================================

/**
 * Address information
 */
struct Address {
    1: optional string addressLine1,
    2: optional string addressLine2,
    3: optional string city,
    4: optional string stateProvince,
    5: optional string postalCode,
    6: optional string countryCode
}

/**
 * Contact information
 */
struct Contact {
    1: optional string name,
    2: optional string phone,
    3: optional string email,
    4: optional string fax
}

/**
 * Party information (used in multiple EDI types)
 */
struct Party {
    1: optional string entityIdentifierCode,
    2: optional string name,
    3: optional string identificationNumber,
    4: optional Address address,
    5: optional Contact contact
}

/**
 * Product information
 */
struct Product {
    1: optional string productId,
    2: optional string description,
    3: optional string identifierType,
    4: optional string manufacturerPartNumber,
    5: optional string brandName
}

/**
 * Quantity information
 */
struct Quantity {
    1: required double value,
    2: optional string unitOfMeasure,
    3: optional string unitOfMeasureDescription
}

/**
 * Price information
 */
struct Price {
    1: required double value,
    2: optional string currencyCode,
    3: optional string priceBasisCode
}

/**
 * Reference number information
 */
struct ReferenceNumber {
    1: required string referenceType,
    2: required string referenceValue,
    3: optional string description
}

/**
 * Date/time information
 */
struct DateTime {
    1: optional string date,
    2: optional string time,
    3: optional string timezone,
    4: optional string qualifier
}

/**
 * Monetary amounts summary
 */
struct MonetaryAmounts {
    1: optional Price totalAmount,
    2: optional Price taxAmount,
    3: optional Price freightAmount,
    4: optional Price discountAmount,
    5: optional Price termsDiscountAmount,
    6: optional map<string, string> additionalAmounts
}

/**
 * Generic EDI Segment representation
 */
struct EdiSegment {
    1: required string segmentId,
    2: required list<string> elements,
    3: optional i32 lineNumber,
    4: optional i32 position
}

/**
 * Processing message for errors or warnings
 */
struct ProcessingMessage {
    1: required MessageLevel level,
    2: required string code,
    3: required string message,
    4: optional string field,
    5: optional i32 lineNumber,
    6: optional i32 elementPosition
}

/**
 * EDI Message Type information
 */
struct EdiMessageType {
    1: required string code,
    2: required string name,
    3: required string description,
    4: required bool supported,
    5: optional list<string> requiredSegments,
    6: optional list<string> optionalSegments
}

/**
 * Processing options for EDI messages
 */
struct ProcessingOptions {
    1: optional bool validateFormat,
    2: optional bool validateBusinessRules,
    3: optional bool includeParsingDetails,
    4: optional bool includeRawSegments,
    5: optional string environment,
    6: optional map<string, string> validationRules
}

// ============================================================================
// EDI 850 Purchase Order Structures
// ============================================================================

/**
 * EDI 850 specific line item
 */
struct PurchaseOrderLineItem {
    1: required string lineNumber,
    2: optional Product product,
    3: optional Quantity quantityOrdered,
    4: optional Price unitPrice,
    5: optional Price extendedPrice,
    6: optional string requestedShipDate,
    7: optional string requestedDeliveryDate,
    8: optional list<string> notes
}

/**
 * EDI 850 Purchase Order Data
 */
struct PurchaseOrderData {
    1: required string poNumber,
    2: optional string poDate,
    3: optional string requestedShipDate,
    4: optional string requestedDeliveryDate,
    5: optional Party buyer,
    6: optional Party seller,
    7: optional Party shipTo,
    8: optional Party billTo,
    9: optional list<PurchaseOrderLineItem> lineItems,
    10: optional MonetaryAmounts monetaryAmounts,
    11: optional list<string> notes,
    12: optional list<ReferenceNumber> referenceNumbers
}

// ============================================================================
// EDI 810 Invoice Structures
// ============================================================================

/**
 * Tax information for invoice line items
 */
struct TaxInformation {
    1: optional string taxTypeCode,
    2: optional Price taxAmount,
    3: optional double taxRate,
    4: optional string taxJurisdiction
}

/**
 * EDI 810 specific line item
 */
struct InvoiceLineItem {
    1: required string lineNumber,
    2: optional Product product,
    3: optional Quantity quantityInvoiced,
    4: optional Price unitPrice,
    5: optional Price extendedPrice,
    6: optional string invoiceDate,
    7: optional list<string> notes,
    8: optional list<TaxInformation> taxInfo
}

/**
 * EDI 810 Invoice Data
 */
struct InvoiceData {
    1: required string invoiceNumber,
    2: optional string invoiceDate,
    3: optional string dueDate,
    4: optional string invoiceTypeCode,
    5: optional Party billTo,
    6: optional Party remitTo,
    7: optional Party shipFrom,
    8: optional Party shipTo,
    9: optional list<InvoiceLineItem> lineItems,
    10: optional MonetaryAmounts monetaryAmounts,
    11: optional string paymentTerms,
    12: optional list<ReferenceNumber> referenceNumbers,
    13: optional list<string> notes
}

// ============================================================================
// EDI 856 Advance Ship Notice Structures
// ============================================================================

/**
 * Package dimensions
 */
struct PackageDimensions {
    1: optional double length,
    2: optional double width,
    3: optional double height,
    4: optional string unitOfMeasure
}

/**
 * Item within a package
 */
struct PackageItem {
    1: optional Product product,
    2: optional Quantity quantityShipped,
    3: optional list<string> serialNumbers,
    4: optional list<string> lotNumbers
}

/**
 * Shipment detail for ASN
 */
struct ShipmentDetail {
    1: optional string packageId,
    2: optional string packageType,
    3: optional Quantity weight,
    4: optional PackageDimensions dimensions,
    5: optional list<PackageItem> items,
    6: optional string trackingNumber
}

/**
 * EDI 856 Advance Ship Notice Data
 */
struct AdvanceShipNoticeData {
    1: required string shipmentId,
    2: optional string shipmentDate,
    3: optional string expectedDeliveryDate,
    4: optional Party shipFrom,
    5: optional Party shipTo,
    6: optional Party billTo,
    7: optional Party carrier,
    8: optional list<ShipmentDetail> shipmentDetails,
    9: optional list<ReferenceNumber> referenceNumbers,
    10: optional list<string> notes
}

// ============================================================================
// EDI 997 Functional Acknowledgment Structures
// ============================================================================

/**
 * Transaction set acknowledgment
 */
struct TransactionSetAcknowledgment {
    1: optional string transactionSetId,
    2: optional string controlNumber,
    3: optional string acknowledgmentCode,
    4: optional list<string> errorMessages
}

/**
 * Segment acknowledgment
 */
struct SegmentAcknowledgment {
    1: optional string segmentId,
    2: optional i32 position,
    3: optional string acknowledgmentCode,
    4: optional list<string> errorMessages
}

/**
 * Element acknowledgment
 */
struct ElementAcknowledgment {
    1: optional i32 position,
    2: optional string value,
    3: optional string acknowledgmentCode,
    4: optional list<string> errorMessages
}

/**
 * EDI 997 Functional Acknowledgment Data
 */
struct FunctionalAcknowledgmentData {
    1: optional string originalTransactionSetId,
    2: optional string originalControlNumber,
    3: optional string acknowledgmentCode,
    4: optional string processingDate,
    5: optional string processingTime,
    6: optional string senderId,
    7: optional string receiverId,
    8: optional list<TransactionSetAcknowledgment> transactionSetAcks,
    9: optional list<SegmentAcknowledgment> segmentAcks,
    10: optional list<ElementAcknowledgment> elementAcks
}

// ============================================================================
// Generic Line Item Structure
// ============================================================================

/**
 * Line item information (generic for different EDI types)
 */
struct LineItem {
    1: required string lineNumber,
    2: optional Product product,
    3: optional Quantity quantity,
    4: optional Price price,
    5: optional Price extendedPrice,
    6: optional map<string, string> dates,
    7: optional list<string> notes,
    8: optional map<string, string> additionalData
}
