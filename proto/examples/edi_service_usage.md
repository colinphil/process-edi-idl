# Generalized EDI Service Usage Guide

This document provides comprehensive examples of how to use the generalized EDI Service for processing multiple Electronic Data Interchange message types.

## Service Overview

The generalized EDI Service provides a unified API for processing various EDI message types including:
- **EDI 850**: Purchase Orders
- **EDI 810**: Invoices  
- **EDI 856**: Advance Ship Notices
- **EDI 997**: Functional Acknowledgments

## API Endpoints

### Primary Service
```
POST /edi.EdiService/ProcessEdiMessage
```

### Utility Endpoints
```
GET /edi.EdiService/GetSupportedMessageTypes
POST /edi.EdiService/ValidateEdiMessage
```

## Processing Different EDI Message Types

### EDI 850 - Purchase Order

**Request:**
```json
{
  "edi_message": "ISA*00*          *00*          *ZZ*SENDER         *ZZ*RECEIVER       *210101*1200*^*00501*000000001*0*P*>~\nGS*PO*SENDER*RECEIVER*20210101*1200*1*X*005010~\nST*850*0001~\nBEG*00*SA*PO123456**20210101~\nREF*DP*DEPARTMENT123~\nPER*BD*John Smith*TE*555-123-4567~\nN1*BY*ACME Corporation*92*123456789~\nN3*123 Main Street~\nN4*New York*NY*10001*US~\nN1*ST*Warehouse Inc*92*987654321~\nN3*456 Warehouse Blvd~\nN4*Chicago*IL*60601*US~\nN1*RE*ACME Corporation*92*123456789~\nN3*123 Main Street~\nN4*New York*NY*10001*US~\nPO1*1*10*EA*25.50**VP*SKU12345*PD*Widget A~\nPO1*2*5*EA*15.75**VP*SKU67890*PD*Widget B~\nCTT*2~\nSE*15*0001~\nGE*1*1~\nIEA*1*000000001~",
  "message_type": "850",
  "customer_id": "ACME_CORP",
  "options": {
    "validate_format": true,
    "validate_business_rules": true,
    "include_parsing_details": false,
    "environment": "production"
  }
}
```

**Response:**
```json
{
  "status": "PROCESSING_STATUS_SUCCESS",
  "message_type": "850",
  "purchase_order": {
    "po_number": "PO123456",
    "po_date": "2021-01-01",
    "buyer": {
      "entity_identifier_code": "BY",
      "name": "ACME Corporation",
      "identification_number": "123456789",
      "address": {
        "address_line_1": "123 Main Street",
        "city": "New York",
        "state_province": "NY",
        "postal_code": "10001",
        "country_code": "US"
      }
    },
    "line_items": [
      {
        "line_number": "1",
        "product": {
          "product_id": "SKU12345",
          "description": "Widget A"
        },
        "quantity_ordered": {
          "value": 10,
          "unit_of_measure": "EA"
        },
        "unit_price": {
          "value": 25.50,
          "currency_code": "USD"
        }
      }
    ]
  },
  "messages": [],
  "processed_at": "2021-01-01T12:00:00Z"
}
```

### EDI 810 - Invoice

**Request:**
```json
{
  "edi_message": "ISA*00*          *00*          *ZZ*SENDER         *ZZ*RECEIVER       *210101*1200*^*00501*000000001*0*P*>~\nGS*IN*SENDER*RECEIVER*20210101*1200*1*X*005010~\nST*810*0001~\nBIG*20210101*INV123456*20210101*PO123456~\nREF*DP*DEPARTMENT123~\nN1*BT*ACME Corporation*92*123456789~\nN3*123 Main Street~\nN4*New York*NY*10001*US~\nN1*ST*Warehouse Inc*92*987654321~\nN3*456 Warehouse Blvd~\nN4*Chicago*IL*60601*US~\nIT1*1*10*EA*25.50**VP*SKU12345*PD*Widget A~\nIT1*2*5*EA*15.75**VP*SKU67890*PD*Widget B~\nTDS*33375~\nSE*15*0001~\nGE*1*1~\nIEA*1*000000001~",
  "message_type": "810",
  "customer_id": "ACME_CORP",
  "options": {
    "validate_format": true,
    "validate_business_rules": true,
    "environment": "production"
  }
}
```

**Response:**
```json
{
  "status": "PROCESSING_STATUS_SUCCESS",
  "message_type": "810",
  "invoice": {
    "invoice_number": "INV123456",
    "invoice_date": "2021-01-01",
    "due_date": "",
    "bill_to": {
      "entity_identifier_code": "BT",
      "name": "ACME Corporation",
      "identification_number": "123456789"
    },
    "ship_to": {
      "entity_identifier_code": "ST",
      "name": "Warehouse Inc",
      "identification_number": "987654321"
    },
    "line_items": [
      {
        "line_number": "1",
        "product": {
          "product_id": "SKU12345",
          "description": "Widget A"
        },
        "quantity_invoiced": {
          "value": 10,
          "unit_of_measure": "EA"
        },
        "unit_price": {
          "value": 25.50,
          "currency_code": "USD"
        }
      }
    ],
    "monetary_amounts": {
      "total_amount": {
        "value": 333.75,
        "currency_code": "USD"
      }
    }
  },
  "messages": [],
  "processed_at": "2021-01-01T12:00:00Z"
}
```

### EDI 856 - Advance Ship Notice

**Request:**
```json
{
  "edi_message": "ISA*00*          *00*          *ZZ*SENDER         *ZZ*RECEIVER       *210101*1200*^*00501*000000001*0*P*>~\nGS*SH*SENDER*RECEIVER*20210101*1200*1*X*005010~\nST*856*0001~\nBSN*00*ASN123456*20210101*1200~\nHL*1**S~\nN1*SH*ACME Corporation*92*123456789~\nN3*123 Main Street~\nN4*New York*NY*10001*US~\nN1*ST*Warehouse Inc*92*987654321~\nN3*456 Warehouse Blvd~\nN4*Chicago*IL*60601*US~\nHL*2*1*O~\nPRF*PO123456~\nHL*3*2*P~\nMAN*GM*PKG001~\nHL*4*3*I~\nLIN*1*VP*SKU12345*PD*Widget A~\nSN1*1*10*EA~\nCTT*4~\nSE*15*0001~\nGE*1*1~\nIEA*1*000000001~",
  "message_type": "856",
  "customer_id": "ACME_CORP",
  "options": {
    "validate_format": true,
    "validate_business_rules": true,
    "environment": "production"
  }
}
```

**Response:**
```json
{
  "status": "PROCESSING_STATUS_SUCCESS",
  "message_type": "856",
  "advance_ship_notice": {
    "shipment_id": "ASN123456",
    "shipment_date": "2021-01-01",
    "ship_from": {
      "entity_identifier_code": "SH",
      "name": "ACME Corporation",
      "identification_number": "123456789"
    },
    "ship_to": {
      "entity_identifier_code": "ST",
      "name": "Warehouse Inc",
      "identification_number": "987654321"
    },
    "shipment_details": [
      {
        "package_id": "PKG001",
        "package_type": "GM",
        "items": [
          {
            "product": {
              "product_id": "SKU12345",
              "description": "Widget A"
            },
            "quantity_shipped": {
              "value": 10,
              "unit_of_measure": "EA"
            }
          }
        ]
      }
    ]
  },
  "messages": [],
  "processed_at": "2021-01-01T12:00:00Z"
}
```

## Getting Supported Message Types

**Request:**
```json
{
  "customer_id": "ACME_CORP"
}
```

**Response:**
```json
{
  "supported_types": [
    {
      "code": "850",
      "name": "Purchase Order",
      "description": "Customer purchase orders",
      "supported": true,
      "required_segments": ["ISA", "GS", "ST", "BEG", "SE", "GE", "IEA"],
      "optional_segments": ["REF", "PER", "N1", "N3", "N4", "PO1", "CTT"]
    },
    {
      "code": "810",
      "name": "Invoice",
      "description": "Customer invoices",
      "supported": true,
      "required_segments": ["ISA", "GS", "ST", "BIG", "SE", "GE", "IEA"],
      "optional_segments": ["REF", "N1", "N3", "N4", "IT1", "TDS"]
    },
    {
      "code": "856",
      "name": "Advance Ship Notice",
      "description": "Shipment notifications",
      "supported": true,
      "required_segments": ["ISA", "GS", "ST", "BSN", "HL", "SE", "GE", "IEA"],
      "optional_segments": ["N1", "N3", "N4", "PRF", "MAN", "LIN", "SN1", "CTT"]
    },
    {
      "code": "997",
      "name": "Functional Acknowledgment",
      "description": "Transaction acknowledgments",
      "supported": true,
      "required_segments": ["ISA", "GS", "ST", "AK1", "SE", "GE", "IEA"],
      "optional_segments": ["AK2", "AK5", "AK9"]
    }
  ]
}
```

## Message Validation

**Request:**
```json
{
  "edi_message": "ISA*00*          *00*          *ZZ*SENDER         *ZZ*RECEIVER       *210101*1200*^*00501*000000001*0*P*>~\nGS*PO*SENDER*RECEIVER*20210101*1200*1*X*005010~\nST*850*0001~\nBEG*00*SA*PO123456**20210101~\nSE*4*0001~\nGE*1*1~\nIEA*1*000000001~",
  "message_type": "850",
  "customer_id": "ACME_CORP"
}
```

**Response:**
```json
{
  "status": "PROCESSING_STATUS_SUCCESS",
  "messages": [],
  "edi_version": "005010",
  "detected_message_type": "850"
}
```

## Error Handling

**Error Response Example:**
```json
{
  "status": "PROCESSING_STATUS_VALIDATION_ERROR",
  "message_type": "850",
  "messages": [
    {
      "level": "MESSAGE_LEVEL_ERROR",
      "code": "EDI_FORMAT_ERROR",
      "message": "Invalid ISA segment format",
      "field": "ISA",
      "line_number": 1
    },
    {
      "level": "MESSAGE_LEVEL_WARNING",
      "code": "MISSING_SHIP_DATE",
      "message": "Requested ship date not specified",
      "field": "BEG",
      "line_number": 4
    }
  ],
  "processed_at": "2021-01-01T12:00:00Z"
}
```

## Integration Examples

### gRPC Client (Go)

```go
package main

import (
    "context"
    "log"
    
    "google.golang.org/grpc"
    pb "github.com/colinleephillips/process-edi-idl/generated/edi"
)

func main() {
    conn, err := grpc.Dial("localhost:50051", grpc.WithInsecure())
    if err != nil {
        log.Fatal(err)
    }
    defer conn.Close()
    
    client := pb.NewEdiServiceClient(conn)
    
    // Process EDI 850 Purchase Order
    req := &pb.ProcessEdiMessageRequest{
        EdiMessage: "ISA*00*...",
        MessageType: "850",
        CustomerId: "ACME_CORP",
        Options: &pb.ProcessingOptions{
            ValidateFormat: true,
            ValidateBusinessRules: true,
            Environment: "production",
        },
    }
    
    resp, err := client.ProcessEdiMessage(context.Background(), req)
    if err != nil {
        log.Fatal(err)
    }
    
    log.Printf("Status: %v", resp.Status)
    log.Printf("Message Type: %s", resp.MessageType)
    
    // Handle different message types
    switch resp.MessageType {
    case "850":
        if resp.PurchaseOrder != nil {
            log.Printf("PO Number: %s", resp.PurchaseOrder.PoNumber)
        }
    case "810":
        if resp.Invoice != nil {
            log.Printf("Invoice Number: %s", resp.Invoice.InvoiceNumber)
        }
    case "856":
        if resp.AdvanceShipNotice != nil {
            log.Printf("Shipment ID: %s", resp.AdvanceShipNotice.ShipmentId)
        }
    case "997":
        if resp.FunctionalAcknowledgment != nil {
            log.Printf("Original Control Number: %s", resp.FunctionalAcknowledgment.OriginalControlNumber)
        }
    }
}
```

### HTTP/REST Client (curl)

```bash
# Process EDI 850 Purchase Order
curl -X POST \
  http://localhost:8080/edi.EdiService/ProcessEdiMessage \
  -H 'Content-Type: application/json' \
  -d '{
    "edi_message": "ISA*00*...",
    "message_type": "850",
    "customer_id": "ACME_CORP",
    "options": {
      "validate_format": true,
      "validate_business_rules": true,
      "environment": "production"
    }
  }'

# Get supported message types
curl -X POST \
  http://localhost:8080/edi.EdiService/GetSupportedMessageTypes \
  -H 'Content-Type: application/json' \
  -d '{
    "customer_id": "ACME_CORP"
  }'

# Validate EDI message
curl -X POST \
  http://localhost:8080/edi.EdiService/ValidateEdiMessage \
  -H 'Content-Type: application/json' \
  -d '{
    "edi_message": "ISA*00*...",
    "message_type": "850",
    "customer_id": "ACME_CORP"
  }'
```

## Best Practices

1. **Always specify message_type**: While the service can auto-detect, explicitly specifying the message type improves performance and accuracy.

2. **Use validation**: Enable format validation for production use to ensure EDI compliance.

3. **Handle all message types**: Check the response's `message_type` field and handle the appropriate parsed data type.

4. **Error handling**: Always check the `status` field and review any `messages` for processing issues.

5. **Customer-specific processing**: Use the `customer_id` field for customized processing rules and validations.

6. **Environment awareness**: Use appropriate environment settings for different deployment stages.

## Migration from Individual Services

If you're migrating from individual EDI services:

1. **Update service client**: Change from individual service clients to `EdiServiceClient`
2. **Update request structure**: Add `message_type` field to requests
3. **Update response handling**: Check `message_type` and use appropriate parsed data field
4. **Test thoroughly**: Validate all message types and error scenarios
