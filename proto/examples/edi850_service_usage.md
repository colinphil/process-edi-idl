# EDI 850 Service Example Usage

This document provides examples of how to use the generalized EDI Service for processing EDI 850 Purchase Order messages.

## Service Overview

The generalized EDI Service provides a unified API for processing EDI 850 Purchase Order messages along with other EDI message types. It accepts raw EDI 850 data and returns structured, parsed purchase order information.

## API Endpoint

```
POST /edi.EdiService/ProcessEdiMessage
```

## Example EDI 850 Message

Here's a sample EDI 850 Purchase Order message:

```
ISA*00*          *00*          *ZZ*SENDER         *ZZ*RECEIVER       *210101*1200*^*00501*000000001*0*P*>~
GS*PO*SENDER*RECEIVER*20210101*1200*1*X*005010~
ST*850*0001~
BEG*00*SA*PO123456**20210101~
REF*DP*DEPARTMENT123~
PER*BD*John Smith*TE*555-123-4567~
N1*BY*ACME Corporation*92*123456789~
N3*123 Main Street~
N4*New York*NY*10001*US~
N1*ST*Warehouse Inc*92*987654321~
N3*456 Warehouse Blvd~
N4*Chicago*IL*60601*US~
N1*RE*ACME Corporation*92*123456789~
N3*123 Main Street~
N4*New York*NY*10001*US~
PO1*1*10*EA*25.50**VP*SKU12345*PD*Widget A~
PO1*2*5*EA*15.75**VP*SKU67890*PD*Widget B~
CTT*2~
SE*15*0001~
GE*1*1~
IEA*1*000000001~
```

## Example Request

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

## Example Response

```json
{
  "status": "PROCESSING_STATUS_SUCCESS",
  "message_type": "850",
  "purchase_order": {
    "po_number": "PO123456",
    "po_date": "2021-01-01",
    "requested_ship_date": "",
    "requested_delivery_date": "",
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
      },
      "contact": {
        "name": "John Smith",
        "phone": "555-123-4567"
      }
    },
    "seller": {
      "entity_identifier_code": "RE",
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
    "ship_to": {
      "entity_identifier_code": "ST",
      "name": "Warehouse Inc",
      "identification_number": "987654321",
      "address": {
        "address_line_1": "456 Warehouse Blvd",
        "city": "Chicago",
        "state_province": "IL",
        "postal_code": "60601",
        "country_code": "US"
      }
    },
    "line_items": [
      {
        "line_number": "1",
        "product": {
          "product_id": "SKU12345",
          "description": "Widget A",
          "identifier_type": "VP"
        },
        "quantity_ordered": {
          "value": 10,
          "unit_of_measure": "EA"
        },
        "unit_price": {
          "value": 25.50,
          "currency_code": "USD"
        },
        "extended_price": {
          "value": 255.00,
          "currency_code": "USD"
        }
      },
      {
        "line_number": "2",
        "product": {
          "product_id": "SKU67890",
          "description": "Widget B",
          "identifier_type": "VP"
        },
        "quantity_ordered": {
          "value": 5,
          "unit_of_measure": "EA"
        },
        "unit_price": {
          "value": 15.75,
          "currency_code": "USD"
        },
        "extended_price": {
          "value": 78.75,
          "currency_code": "USD"
        }
      }
    ],
    "monetary_amounts": {
      "total_amount": {
        "value": 333.75,
        "currency_code": "USD"
      }
    },
    "reference_numbers": [
      {
        "reference_type": "DP",
        "reference_value": "DEPARTMENT123"
      }
    ]
  },
  "messages": [],
  "processed_at": "2021-01-01T12:00:00Z"
}
```

## Error Response Example

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

## Usage Notes

1. **EDI Format**: The service expects standard EDI 850 format with proper segment terminators (~) and element separators (*).

2. **Validation**: Enable format validation for production use to ensure EDI compliance.

3. **Business Rules**: Enable business rule validation to check for logical consistency in the purchase order data.

4. **Error Handling**: Always check the `status` field and review any `messages` for processing issues.

5. **Customer ID**: Use the `customer_id` field to identify the trading partner for customized processing rules.

## Supported EDI Segments

The service supports the following EDI 850 segments:
- ISA/GS/ST/SE/GE/IEA (Envelope segments)
- BEG (Beginning segment)
- REF (Reference identification)
- PER (Administrative communications contact)
- N1/N3/N4 (Name and address segments)
- PO1 (Purchase order line item)
- CTT (Transaction totals)

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
    if resp.PurchaseOrder != nil {
        log.Printf("PO Number: %s", resp.PurchaseOrder.PoNumber)
    }
}
```

### HTTP/REST Client (curl)
```bash
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
```
