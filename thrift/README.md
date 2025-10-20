# Thrift EDI Service Implementation

This directory contains a complete Thrift implementation of the EDI service, providing a unified API for processing multiple EDI message types.

## Files Overview

- **`edi_types.thrift`**: Contains all type definitions for EDI message processing, including common structures and EDI-specific data types
- **`edi_exceptions.thrift`**: Defines all exception types for error handling
- **`edi_service.thrift`**: Main service definition with operations and request/response structures
- **`examples/thrift_service_usage.md`**: Comprehensive usage examples in Python, Java, and Go

## Service Features

### Supported EDI Message Types
- **EDI 850**: Purchase Order
- **EDI 810**: Invoice
- **EDI 856**: Advance Ship Notice
- **EDI 997**: Functional Acknowledgment

### Service Operations
1. **`processEdiMessage`**: Process any EDI message type and return structured data
2. **`getSupportedMessageTypes`**: Get list of supported EDI message types
3. **`validateEdiMessage`**: Validate EDI message format without full processing

### Key Features
- **Unified API**: Single service interface for all EDI message types
- **Extensible Design**: Easy to add new EDI message types
- **Comprehensive Error Handling**: Specific exceptions for different error conditions
- **Flexible Processing Options**: Configurable validation and processing behavior
- **Multi-language Support**: Generated code for Java, Python, Go, and other languages

## Data Structures

### Common Structures
- **Party**: Entity information (buyer, seller, ship-to, etc.)
- **Address**: Address information
- **Contact**: Contact details
- **Product**: Product/service information
- **Quantity**: Quantity with unit of measure
- **Price**: Price with currency
- **ReferenceNumber**: Reference number information
- **MonetaryAmounts**: Summary of monetary amounts

### EDI-Specific Structures
- **PurchaseOrderData**: EDI 850 purchase order data
- **InvoiceData**: EDI 810 invoice data
- **AdvanceShipNoticeData**: EDI 856 advance ship notice data
- **FunctionalAcknowledgmentData**: EDI 997 functional acknowledgment data

## Error Handling

The service defines specific exceptions for different error conditions:

- **ValidationError** (HTTP 400): EDI message format is invalid
- **ParsingError** (HTTP 400): EDI message cannot be parsed
- **BusinessRuleError** (HTTP 422): Business rules are violated
- **UnsupportedMessageTypeError** (HTTP 415): Message type is not supported
- **InternalError** (HTTP 500): Internal server error

## Code Generation

To generate client code for your preferred language:

### Java
```bash
thrift --gen java edi_service.thrift
```

### Python
```bash
thrift --gen py edi_service.thrift
```

### Go
```bash
thrift --gen go edi_service.thrift
```

### Other Languages
```bash
thrift --gen <language> edi_service.thrift
```

## Usage Example

```python
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from edi_service import EdiService

# Create client
transport = TSocket.TSocket('localhost', 9090)
transport = TTransport.TBufferedTransport(transport)
protocol = TBinaryProtocol.TBinaryProtocol(transport)
client = EdiService.Client(protocol)
transport.open()

# Process EDI message
request = ProcessEdiMessageRequest(
    ediMessage=edi_message,
    messageType="850",
    customerId="CUSTOMER123"
)

response = client.processEdiMessage(request)
print(f"Status: {response.status}")
print(f"PO Number: {response.purchaseOrder.poNumber}")

transport.close()
```

## Comparison with Smithy Implementation

This Thrift implementation provides the same functionality as the Smithy service definition but with Thrift-specific features:

### Advantages of Thrift
- **Performance**: Binary protocol is more efficient than JSON
- **Language Support**: Native support for more programming languages
- **Mature Ecosystem**: Well-established with extensive tooling
- **Type Safety**: Strong typing with compile-time checking

### Differences from Smithy
- **Protocol**: Uses Thrift binary protocol instead of HTTP/JSON
- **Transport**: Direct socket connection instead of HTTP
- **Error Handling**: Thrift exceptions instead of HTTP status codes
- **Serialization**: Binary serialization instead of JSON

## Integration Notes

- The service maintains the same data structures and business logic as the Smithy implementation
- Error handling is adapted to Thrift's exception model
- All EDI message types and processing options are preserved
- The API is designed to be easily integrated with existing EDI processing systems

## Next Steps

1. Generate client code for your target language(s)
2. Implement the service handler based on your EDI processing logic
3. Set up Thrift server infrastructure
4. Integrate with your existing EDI processing pipeline
5. Add monitoring and logging as needed
