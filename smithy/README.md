# Smithy EDI Service Interface

This directory contains Smithy IDL definitions for the generalized Electronic Data Interchange (EDI) processing service.

## Overview

Smithy is Amazon's IDL for building web services. This Smithy implementation provides the same functionality as the Protocol Buffers version but uses Smithy's syntax and features.

## Files

- **`edi-service.smithy`**: Main service definition with operations and common types
- **`edi-message-types.smithy`**: Specific EDI message type data structures

## Key Differences from Protocol Buffers

### **Smithy Advantages:**
- **HTTP-First**: Built-in HTTP bindings and REST API generation
- **Rich Constraints**: Built-in validation and constraints
- **Better Documentation**: Native documentation support
- **AWS Integration**: Seamless integration with AWS services
- **Code Generation**: Generates clients for multiple languages

### **Syntax Differences:**

#### **Protocol Buffers:**
```protobuf
message ProcessEdiMessageRequest {
  string edi_message = 1;
  string message_type = 2;
  string customer_id = 3;
}
```

#### **Smithy:**
```smithy
structure ProcessEdiMessageRequest {
    @required
    ediMessage: String
    
    @required
    messageType: String
    
    customerId: String
}
```

## Service Definition

### **Main Service:**
```smithy
@Http(method: "POST", uri: "/edi/process")
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
```

### **Operations:**

1. **ProcessEdiMessage**: Process any EDI message type
2. **GetSupportedMessageTypes**: Get list of supported EDI types
3. **ValidateEdiMessage**: Validate EDI format without processing

## Supported EDI Message Types

| Code | Name | Description | Status |
|------|------|-------------|--------|
| 850 | Purchase Order | Customer purchase orders | ✅ Supported |
| 810 | Invoice | Customer invoices | ✅ Supported |
| 856 | Advance Ship Notice | Shipment notifications | ✅ Supported |
| 997 | Functional Acknowledgment | Transaction acknowledgments | ✅ Supported |

## Code Generation

Smithy can generate code for multiple languages and frameworks:

### **Generate AWS SDK Clients:**
```bash
smithy build
```

### **Generate OpenAPI Specification:**
```bash
smithy generate --language openapi
```

### **Generate JSON Schema:**
```bash
smithy generate --language json-schema
```

## HTTP API Endpoints

The Smithy service generates the following HTTP endpoints:

- `POST /edi/process` - Process EDI messages
- `GET /edi/supported-types` - Get supported message types
- `POST /edi/validate` - Validate EDI messages

## Error Handling

Smithy provides structured error handling:

```smithy
@Error("client")
@HttpError(400)
structure ValidationError {
    @required
    message: String
    code: String
    field: String
    lineNumber: Integer
}
```

## Usage Examples

### **Process EDI 850 Purchase Order:**

**Request:**
```bash
curl -X POST http://localhost:8080/edi/process \
  -H 'Content-Type: application/json' \
  -d '{
    "ediMessage": "ISA*00*...",
    "messageType": "850",
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
  "messageType": "850",
  "purchaseOrder": {
    "poNumber": "PO123456",
    "poDate": "2021-01-01",
    "buyer": {
      "name": "ACME Corporation",
      "identificationNumber": "123456789"
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
        }
      }
    ]
  },
  "processedAt": "2021-01-01T12:00:00Z"
}
```

## Integration with AWS Services

Smithy services can be easily deployed to AWS:

- **AWS Lambda**: Serverless function execution
- **Amazon API Gateway**: REST API management
- **AWS AppSync**: GraphQL API generation
- **Amazon CloudFormation**: Infrastructure as code

## Adding New EDI Message Types

To add support for a new EDI message type:

1. **Define the data structure** in `edi-message-types.smithy`:
   ```smithy
   structure NewEdiTypeData {
       @required
       identifier: String
       // ... other fields
   }
   ```

2. **Add to the response** in `edi-service.smithy`:
   ```smithy
   structure ProcessEdiMessageResponse {
       // ... existing fields
       newEdiType: NewEdiTypeData
   }
   ```

3. **Update the service implementation**

## Comparison with Protocol Buffers

| Feature | Protocol Buffers | Smithy |
|---------|------------------|--------|
| **Primary Use** | gRPC, binary serialization | HTTP APIs, AWS services |
| **HTTP Support** | Via gRPC-Gateway | Native |
| **Validation** | Custom | Built-in constraints |
| **Documentation** | Comments | Native `@Documentation` |
| **Code Generation** | Multiple languages | AWS SDK + others |
| **AWS Integration** | Manual | Native |
| **REST APIs** | Via gateway | Direct generation |

## Benefits of Smithy Version

1. **HTTP-First Design**: Better suited for web APIs
2. **AWS Integration**: Seamless deployment to AWS services
3. **Rich Validation**: Built-in constraints and validation
4. **Better Documentation**: Native documentation features
5. **REST API Generation**: Direct OpenAPI/Swagger generation
6. **Structured Errors**: HTTP status codes and error handling

## Next Steps

1. **Generate Code**: Use `smithy build` to generate client code
2. **Deploy to AWS**: Use AWS CDK or CloudFormation
3. **Add Validation**: Implement business rules and constraints
4. **Extend Types**: Add more EDI message types as needed

This Smithy implementation provides a modern, HTTP-first approach to EDI processing with excellent AWS integration capabilities.
