# IDL Service Interface - Generalized EDI Processing

This project contains Interface Definition Language (IDL) specifications for a generalized Electronic Data Interchange (EDI) processing service that supports multiple EDI message types.

## Project Structure

```
process-edi-idl/
├── proto/                           # Protocol Buffer definitions
│   ├── edi_service.proto           # Generalized EDI service definition
│   └── edi_message_types.proto     # Specific EDI message type definitions
├── examples/                         # Usage examples and documentation
│   ├── edi_service_usage.md        # EDI service usage guide
│   └── edi850_service_usage.md     # EDI 850 specific examples
├── generated/                       # Generated code (to be created)
└── docs/                            # Additional documentation
```

## Generalized EDI Service

The generalized EDI service provides a unified API for processing multiple EDI message types. It supports:

- **Multiple EDI Types**: 850 (Purchase Order), 810 (Invoice), 856 (Advance Ship Notice), 997 (Functional Acknowledgment), and more
- **Unified API**: Single service interface for all EDI message types
- **Extensible Design**: Easy to add new EDI message types

### Key Features

- **Single Service Interface**: `EdiService` with unified `ProcessEdiMessage` method
- **Message Type Detection**: Automatic detection and validation of EDI message types
- **Comprehensive Data Models**: Complete representations for each supported EDI type
- **Flexible Processing**: Configurable validation and processing options
- **Error Handling**: Detailed error messages and processing status
- **Extensibility**: Easy to add new EDI message types

### Supported EDI Message Types

| Code | Name | Description | Status |
|------|------|-------------|--------|
| 850 | Purchase Order | Customer purchase orders | ✅ Supported |
| 810 | Invoice | Customer invoices | ✅ Supported |
| 856 | Advance Ship Notice | Shipment notifications | ✅ Supported |
| 997 | Functional Acknowledgment | Transaction acknowledgments | ✅ Supported |
| 855 | Purchase Order Acknowledgment | PO confirmations | 🔄 Planned |
| 860 | Purchase Order Change Request | PO modifications | 🔄 Planned |
| 861 | Receiving Advice | Receipt notifications | 🔄 Planned |

### Service Architecture

The service uses a modular architecture:

1. **Base Service** (`edi_service.proto`): Core service interface and common types
2. **Message Types** (`edi_message_types.proto`): Specific EDI message data structures

### Usage

See the [examples/edi_service_usage.md](examples/edi_service_usage.md) file for detailed usage examples, including:

- Processing different EDI message types
- Request/response examples for each type
- Error handling patterns
- Integration examples for different languages

### Adding New EDI Message Types

To add support for a new EDI message type:

1. **Define the data structure** in `edi_message_types.proto`:
   ```protobuf
   message NewEdiTypeData {
     // Define the specific fields for this EDI type
   }
   ```

2. **Add to the oneof** in `ProcessEdiMessageResponse`:
   ```protobuf
   oneof parsed_data {
     // ... existing types
     NewEdiTypeData new_edi_type = X;
   }
   ```

3. **Update supported types** in the service implementation

### Generated Code

To generate client/server code from the protobuf definitions:

```bash
# Generate Go code for all services
protoc --go_out=generated --go_opt=paths=source_relative \
       --go-grpc_out=generated --go-grpc_opt=paths=source_relative \
       proto/*.proto

# Generate other languages as needed
protoc --python_out=generated proto/*.proto
protoc --java_out=generated proto/*.proto
```

### Usage Example

```go
client := pb.NewEdiServiceClient(conn)
resp, err := client.ProcessEdiMessage(ctx, &pb.ProcessEdiMessageRequest{
    EdiMessage: ediMessage,
    MessageType: "850",
    CustomerId: "ACME_CORP",
    Options: &pb.ProcessingOptions{
        ValidateFormat: true,
        ValidateBusinessRules: true,
        Environment: "production",
    },
})
```
