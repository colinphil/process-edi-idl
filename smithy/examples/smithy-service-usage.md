# Smithy EDI Service Usage Examples

This document provides comprehensive examples of how to use the Smithy EDI Service for processing multiple Electronic Data Interchange message types.

## Service Overview

The Smithy EDI Service provides HTTP-based endpoints for processing various EDI message types:
- **EDI 850**: Purchase Orders
- **EDI 810**: Invoices  
- **EDI 856**: Advance Ship Notices
- **EDI 997**: Functional Acknowledgments

## HTTP API Endpoints

### Primary Endpoints
- `POST /edi/process` - Process EDI messages
- `GET /edi/supported-types` - Get supported message types
- `POST /edi/validate` - Validate EDI messages

## Processing Different EDI Message Types

### EDI 850 - Purchase Order

**Request:**
```bash
curl -X POST http://localhost:8080/edi/process \
  -H 'Content-Type: application/json' \
  -d '{
    "ediMessage": "ISA*00*          *00*          *ZZ*SENDER         *ZZ*RECEIVER       *210101*1200*^*00501*000000001*0*P*>~\nGS*PO*SENDER*RECEIVER*20210101*1200*1*X*005010~\nST*850*0001~\nBEG*00*SA*PO123456**20210101~\nREF*DP*DEPARTMENT123~\nPER*BD*John Smith*TE*555-123-4567~\nN1*BY*ACME Corporation*92*123456789~\nN3*123 Main Street~\nN4*New York*NY*10001*US~\nN1*ST*Warehouse Inc*92*987654321~\nN3*456 Warehouse Blvd~\nN4*Chicago*IL*60601*US~\nN1*RE*ACME Corporation*92*123456789~\nN3*123 Main Street~\nN4*New York*NY*10001*US~\nPO1*1*10*EA*25.50**VP*SKU12345*PD*Widget A~\nPO1*2*5*EA*15.75**VP*SKU67890*PD*Widget B~\nCTT*2~\nSE*15*0001~\nGE*1*1~\nIEA*1*000000001~",
    "messageType": "850",
    "customerId": "ACME_CORP",
    "options": {
      "validateFormat": true,
      "validateBusinessRules": true,
      "includeParsingDetails": false,
      "environment": "production"
    }
  }'
```

**Response:**
```json
{
  "status": "SUCCESS",
  "messageType": "850",
  "purchaseOrder": {
    "poNumber": "PO123456",
    "poDate": "2021-01-01",
    "buyer": {
      "entityIdentifierCode": "BY",
      "name": "ACME Corporation",
      "identificationNumber": "123456789",
      "address": {
        "addressLine1": "123 Main Street",
        "city": "New York",
        "stateProvince": "NY",
        "postalCode": "10001",
        "countryCode": "US"
      },
      "contact": {
        "name": "John Smith",
        "phone": "555-123-4567"
      }
    },
    "lineItems": [
      {
        "lineNumber": "1",
        "product": {
          "productId": "SKU12345",
          "description": "Widget A"
        },
        "quantityOrdered": {
          "value": 10,
          "unitOfMeasure": "EA"
        },
        "unitPrice": {
          "value": 25.50,
          "currencyCode": "USD"
        }
      }
    ]
  },
  "messages": [],
  "processedAt": "2021-01-01T12:00:00Z"
}
```

### EDI 810 - Invoice

**Request:**
```bash
curl -X POST http://localhost:8080/edi/process \
  -H 'Content-Type: application/json' \
  -d '{
    "ediMessage": "ISA*00*          *00*          *ZZ*SENDER         *ZZ*RECEIVER       *210101*1200*^*00501*000000001*0*P*>~\nGS*IN*SENDER*RECEIVER*20210101*1200*1*X*005010~\nST*810*0001~\nBIG*20210101*INV123456*20210101*PO123456~\nREF*DP*DEPARTMENT123~\nN1*BT*ACME Corporation*92*123456789~\nN3*123 Main Street~\nN4*New York*NY*10001*US~\nN1*ST*Warehouse Inc*92*987654321~\nN3*456 Warehouse Blvd~\nN4*Chicago*IL*60601*US~\nIT1*1*10*EA*25.50**VP*SKU12345*PD*Widget A~\nIT1*2*5*EA*15.75**VP*SKU67890*PD*Widget B~\nTDS*33375~\nSE*15*0001~\nGE*1*1~\nIEA*1*000000001~",
    "messageType": "810",
    "customerId": "ACME_CORP",
    "options": {
      "validateFormat": true,
      "validateBusinessRules": true,
      "environment": "production"
    }
  }'
```

**Response:**
```json
{
  "status": "SUCCESS",
  "messageType": "810",
  "invoice": {
    "invoiceNumber": "INV123456",
    "invoiceDate": "2021-01-01",
    "dueDate": "",
    "billTo": {
      "entityIdentifierCode": "BT",
      "name": "ACME Corporation",
      "identificationNumber": "123456789"
    },
    "shipTo": {
      "entityIdentifierCode": "ST",
      "name": "Warehouse Inc",
      "identificationNumber": "987654321"
    },
    "lineItems": [
      {
        "lineNumber": "1",
        "product": {
          "productId": "SKU12345",
          "description": "Widget A"
        },
        "quantityInvoiced": {
          "value": 10,
          "unitOfMeasure": "EA"
        },
        "unitPrice": {
          "value": 25.50,
          "currencyCode": "USD"
        }
      }
    ],
    "monetaryAmounts": {
      "totalAmount": {
        "value": 333.75,
        "currencyCode": "USD"
      }
    }
  },
  "messages": [],
  "processedAt": "2021-01-01T12:00:00Z"
}
```

## Getting Supported Message Types

**Request:**
```bash
curl -X GET "http://localhost:8080/edi/supported-types?customerId=ACME_CORP" \
  -H 'Accept: application/json'
```

**Response:**
```json
{
  "supportedTypes": [
    {
      "code": "850",
      "name": "Purchase Order",
      "description": "Customer purchase orders",
      "supported": true,
      "requiredSegments": ["ISA", "GS", "ST", "BEG", "SE", "GE", "IEA"],
      "optionalSegments": ["REF", "PER", "N1", "N3", "N4", "PO1", "CTT"]
    },
    {
      "code": "810",
      "name": "Invoice",
      "description": "Customer invoices",
      "supported": true,
      "requiredSegments": ["ISA", "GS", "ST", "BIG", "SE", "GE", "IEA"],
      "optionalSegments": ["REF", "N1", "N3", "N4", "IT1", "TDS"]
    },
    {
      "code": "856",
      "name": "Advance Ship Notice",
      "description": "Shipment notifications",
      "supported": true,
      "requiredSegments": ["ISA", "GS", "ST", "BSN", "HL", "SE", "GE", "IEA"],
      "optionalSegments": ["N1", "N3", "N4", "PRF", "MAN", "LIN", "SN1", "CTT"]
    },
    {
      "code": "997",
      "name": "Functional Acknowledgment",
      "description": "Transaction acknowledgments",
      "supported": true,
      "requiredSegments": ["ISA", "GS", "ST", "AK1", "SE", "GE", "IEA"],
      "optionalSegments": ["AK2", "AK5", "AK9"]
    }
  ]
}
```

## Message Validation

**Request:**
```bash
curl -X POST http://localhost:8080/edi/validate \
  -H 'Content-Type: application/json' \
  -d '{
    "ediMessage": "ISA*00*          *00*          *ZZ*SENDER         *ZZ*RECEIVER       *210101*1200*^*00501*000000001*0*P*>~\nGS*PO*SENDER*RECEIVER*20210101*1200*1*X*005010~\nST*850*0001~\nBEG*00*SA*PO123456**20210101~\nSE*4*0001~\nGE*1*1~\nIEA*1*000000001~",
    "messageType": "850",
    "customerId": "ACME_CORP"
  }'
```

**Response:**
```json
{
  "status": "SUCCESS",
  "messages": [],
  "ediVersion": "005010",
  "detectedMessageType": "850"
}
```

## Error Handling

**Error Response Example:**
```json
{
  "status": "VALIDATION_ERROR",
  "messageType": "850",
  "messages": [
    {
      "level": "ERROR",
      "code": "EDI_FORMAT_ERROR",
      "message": "Invalid ISA segment format",
      "field": "ISA",
      "lineNumber": 1
    },
    {
      "level": "WARNING",
      "code": "MISSING_SHIP_DATE",
      "message": "Requested ship date not specified",
      "field": "BEG",
      "lineNumber": 4
    }
  ],
  "processedAt": "2021-01-01T12:00:00Z"
}
```

## HTTP Status Codes

The Smithy service uses standard HTTP status codes:

- **200 OK**: Successful processing
- **400 Bad Request**: Validation errors, parsing errors
- **415 Unsupported Media Type**: Unsupported message type
- **422 Unprocessable Entity**: Business rule errors
- **500 Internal Server Error**: Server errors

## Integration Examples

### JavaScript/TypeScript Client

```typescript
interface EdiServiceClient {
  processEdiMessage(request: ProcessEdiMessageRequest): Promise<ProcessEdiMessageResponse>;
  getSupportedMessageTypes(request: GetSupportedMessageTypesRequest): Promise<GetSupportedMessageTypesResponse>;
  validateEdiMessage(request: ValidateEdiMessageRequest): Promise<ValidateEdiMessageResponse>;
}

// Usage
const client = new EdiServiceClient('http://localhost:8080');

const response = await client.processEdiMessage({
  ediMessage: "ISA*00*...",
  messageType: "850",
  customerId: "ACME_CORP",
  options: {
    validateFormat: true,
    validateBusinessRules: true,
    environment: "production"
  }
});

console.log('Status:', response.status);
console.log('Message Type:', response.messageType);

// Handle different message types
if (response.purchaseOrder) {
  console.log('PO Number:', response.purchaseOrder.poNumber);
} else if (response.invoice) {
  console.log('Invoice Number:', response.invoice.invoiceNumber);
} else if (response.advanceShipNotice) {
  console.log('Shipment ID:', response.advanceShipNotice.shipmentId);
} else if (response.functionalAcknowledgment) {
  console.log('Original Control Number:', response.functionalAcknowledgment.originalControlNumber);
}
```

### Python Client

```python
import requests
import json

class EdiServiceClient:
    def __init__(self, base_url):
        self.base_url = base_url
    
    def process_edi_message(self, edi_message, message_type, customer_id=None, options=None):
        url = f"{self.base_url}/edi/process"
        payload = {
            "ediMessage": edi_message,
            "messageType": message_type,
            "customerId": customer_id,
            "options": options
        }
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    
    def get_supported_message_types(self, customer_id=None):
        url = f"{self.base_url}/edi/supported-types"
        params = {"customerId": customer_id} if customer_id else {}
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def validate_edi_message(self, edi_message, message_type, customer_id=None):
        url = f"{self.base_url}/edi/validate"
        payload = {
            "ediMessage": edi_message,
            "messageType": message_type,
            "customerId": customer_id
        }
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()

# Usage
client = EdiServiceClient('http://localhost:8080')

response = client.process_edi_message(
    edi_message="ISA*00*...",
    message_type="850",
    customer_id="ACME_CORP",
    options={
        "validateFormat": True,
        "validateBusinessRules": True,
        "environment": "production"
    }
)

print(f"Status: {response['status']}")
print(f"Message Type: {response['messageType']}")

# Handle different message types
if 'purchaseOrder' in response:
    print(f"PO Number: {response['purchaseOrder']['poNumber']}")
elif 'invoice' in response:
    print(f"Invoice Number: {response['invoice']['invoiceNumber']}")
```

## AWS Integration

### Deploy to AWS Lambda

```yaml
# serverless.yml
service: edi-service

provider:
  name: aws
  runtime: nodejs18.x
  region: us-east-1

functions:
  processEdiMessage:
    handler: handler.processEdiMessage
    events:
      - http:
          path: /edi/process
          method: post
          cors: true
  
  getSupportedMessageTypes:
    handler: handler.getSupportedMessageTypes
    events:
      - http:
          path: /edi/supported-types
          method: get
          cors: true
  
  validateEdiMessage:
    handler: handler.validateEdiMessage
    events:
      - http:
          path: /edi/validate
          method: post
          cors: true
```

### Deploy to Amazon API Gateway

```bash
# Generate OpenAPI spec from Smithy
smithy generate --language openapi

# Deploy to API Gateway
aws apigateway import-rest-api --body file://openapi.json
```

## Best Practices

1. **Always specify messageType**: While the service can auto-detect, explicitly specifying improves performance and accuracy.

2. **Use validation**: Enable format validation for production use to ensure EDI compliance.

3. **Handle all message types**: Check the response's `messageType` field and handle the appropriate parsed data type.

4. **Error handling**: Always check the `status` field and review any `messages` for processing issues.

5. **Customer-specific processing**: Use the `customerId` field for customized processing rules and validations.

6. **Environment awareness**: Use appropriate environment settings for different deployment stages.

7. **HTTP status codes**: Use HTTP status codes for error handling in addition to the response status field.

## Comparison with Protocol Buffers Version

| Feature | Protocol Buffers | Smithy |
|---------|------------------|--------|
| **Transport** | gRPC | HTTP/REST |
| **Serialization** | Binary | JSON |
| **Error Handling** | gRPC status codes | HTTP status codes |
| **Client Generation** | gRPC clients | HTTP clients |
| **AWS Integration** | Manual | Native |
| **Documentation** | Comments | OpenAPI/Swagger |

The Smithy version provides a more web-friendly API with better integration for HTTP-based applications and AWS services.
