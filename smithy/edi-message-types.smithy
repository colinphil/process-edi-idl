$version: "2"

namespace com.colinleephillips.process.edi

use smithy.api#Documentation

/// EDI 850 Purchase Order Data
structure PurchaseOrderData {
    /// Purchase Order Number
    @required
    poNumber: String

    /// Purchase Order Date
    poDate: String

    /// Requested Ship Date
    requestedShipDate: String

    /// Requested Delivery Date
    requestedDeliveryDate: String

    /// Buyer information
    buyer: Party

    /// Seller information
    seller: Party

    /// Ship-to address
    shipTo: Party

    /// Bill-to address
    billTo: Party

    /// Purchase order line items
    lineItems: PurchaseOrderLineItemList

    /// Total monetary amounts
    monetaryAmounts: MonetaryAmounts

    /// Additional notes or comments
    notes: StringList

    /// Reference numbers
    referenceNumbers: ReferenceNumberList
}

/// EDI 850 specific line item
structure PurchaseOrderLineItem {
    /// Line item number
    @required
    lineNumber: String

    /// Product/service information
    product: Product

    /// Quantity ordered
    quantityOrdered: Quantity

    /// Unit price
    unitPrice: Price

    /// Extended price
    extendedPrice: Price

    /// Requested ship date for this line item
    requestedShipDate: String

    /// Requested delivery date for this line item
    requestedDeliveryDate: String

    /// Additional line item notes
    notes: StringList
}

/// EDI 810 Invoice Data
structure InvoiceData {
    /// Invoice Number
    @required
    invoiceNumber: String

    /// Invoice Date
    invoiceDate: String

    /// Due Date
    dueDate: String

    /// Invoice Type Code
    invoiceTypeCode: String

    /// Bill-to party
    billTo: Party

    /// Remit-to party
    remitTo: Party

    /// Ship-from party
    shipFrom: Party

    /// Ship-to party
    shipTo: Party

    /// Invoice line items
    lineItems: InvoiceLineItemList

    /// Total monetary amounts
    monetaryAmounts: MonetaryAmounts

    /// Payment terms
    paymentTerms: String

    /// Reference numbers
    referenceNumbers: ReferenceNumberList

    /// Additional notes
    notes: StringList
}

/// EDI 810 specific line item
structure InvoiceLineItem {
    /// Line item number
    @required
    lineNumber: String

    /// Product/service information
    product: Product

    /// Quantity invoiced
    quantityInvoiced: Quantity

    /// Unit price
    unitPrice: Price

    /// Extended price
    extendedPrice: Price

    /// Invoice date for this line item
    invoiceDate: String

    /// Additional line item notes
    notes: StringList

    /// Tax information
    taxInfo: TaxInformationList
}

/// Tax information for invoice line items
structure TaxInformation {
    /// Tax type code
    taxTypeCode: String

    /// Tax amount
    taxAmount: Price

    /// Tax rate
    taxRate: Double

    /// Tax jurisdiction
    taxJurisdiction: String
}

/// EDI 856 Advance Ship Notice Data
structure AdvanceShipNoticeData {
    /// Shipment identification number
    @required
    shipmentId: String

    /// Shipment date
    shipmentDate: String

    /// Expected delivery date
    expectedDeliveryDate: String

    /// Ship-from party
    shipFrom: Party

    /// Ship-to party
    shipTo: Party

    /// Bill-to party
    billTo: Party

    /// Carrier information
    carrier: Party

    /// Shipment details
    shipmentDetails: ShipmentDetailList

    /// Reference numbers
    referenceNumbers: ReferenceNumberList

    /// Additional notes
    notes: StringList
}

/// Shipment detail for ASN
structure ShipmentDetail {
    /// Package identification
    packageId: String

    /// Package type
    packageType: String

    /// Package weight
    weight: Quantity

    /// Package dimensions
    dimensions: PackageDimensions

    /// Items in this package
    items: PackageItemList

    /// Tracking number
    trackingNumber: String
}

/// Package dimensions
structure PackageDimensions {
    /// Length
    length: Double

    /// Width
    width: Double

    /// Height
    height: Double

    /// Unit of measure
    unitOfMeasure: String
}

/// Item within a package
structure PackageItem {
    /// Product information
    product: Product

    /// Quantity shipped
    quantityShipped: Quantity

    /// Serial numbers
    serialNumbers: StringList

    /// Lot numbers
    lotNumbers: StringList
}

/// EDI 997 Functional Acknowledgment Data
structure FunctionalAcknowledgmentData {
    /// Original transaction set identifier
    originalTransactionSetId: String

    /// Original control number
    originalControlNumber: String

    /// Functional acknowledgment code
    acknowledgmentCode: String

    /// Processing date
    processingDate: String

    /// Processing time
    processingTime: String

    /// Sender identification
    senderId: String

    /// Receiver identification
    receiverId: String

    /// Transaction set acknowledgment details
    transactionSetAcks: TransactionSetAcknowledgmentList

    /// Segment acknowledgments
    segmentAcks: SegmentAcknowledgmentList

    /// Element acknowledgments
    elementAcks: ElementAcknowledgmentList
}

/// Transaction set acknowledgment
structure TransactionSetAcknowledgment {
    /// Transaction set identifier
    transactionSetId: String

    /// Control number
    controlNumber: String

    /// Acknowledgment code
    acknowledgmentCode: String

    /// Error messages
    errorMessages: StringList
}

/// Segment acknowledgment
structure SegmentAcknowledgment {
    /// Segment identifier
    segmentId: String

    /// Segment position
    position: Integer

    /// Acknowledgment code
    acknowledgmentCode: String

    /// Error messages
    errorMessages: StringList
}

/// Element acknowledgment
structure ElementAcknowledgment {
    /// Element position
    position: Integer

    /// Element value
    value: String

    /// Acknowledgment code
    acknowledgmentCode: String

    /// Error messages
    errorMessages: StringList
}

/// List types for EDI message data
list PurchaseOrderLineItemList {
    member: PurchaseOrderLineItem
}

list InvoiceLineItemList {
    member: InvoiceLineItem
}

list TaxInformationList {
    member: TaxInformation
}

list ShipmentDetailList {
    member: ShipmentDetail
}

list PackageItemList {
    member: PackageItem
}

list TransactionSetAcknowledgmentList {
    member: TransactionSetAcknowledgment
}

list SegmentAcknowledgmentList {
    member: SegmentAcknowledgment
}

list ElementAcknowledgmentList {
    member: ElementAcknowledgment
}

list ReferenceNumberList {
    member: ReferenceNumber
}
