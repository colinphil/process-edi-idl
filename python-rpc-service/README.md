# Python gRPC EDI Service Implementation

This directory contains a complete Python implementation of the EDI service using gRPC and Protocol Buffers.

## Project Structure

```
python-rpc-service/
├── proto/                          # Protocol buffer definitions
│   ├── edi_service.proto
│   └── edi_message_types.proto
├── generated/                      # Generated Python protobuf code
│   ├── __init__.py
│   ├── edi_service_pb2.py
│   ├── edi_service_pb2_grpc.py
│   ├── edi_message_types_pb2.py
│   └── edi_message_types_pb2_grpc.py
├── src/                           # Source code
│   ├── __init__.py
│   ├── edi_service.py            # Main service implementation
│   ├── edi_parser.py             # EDI parsing logic
│   ├── edi_validator.py          # EDI validation logic
│   └── utils.py                  # Utility functions
├── examples/                      # Usage examples
│   ├── client_example.py
│   ├── server_example.py
│   └── test_messages.py
├── tests/                         # Unit tests
│   ├── __init__.py
│   ├── test_edi_service.py
│   ├── test_edi_parser.py
│   └── test_edi_validator.py
├── requirements.txt               # Python dependencies
├── setup.py                       # Package setup
├── Dockerfile                     # Docker configuration
├── docker-compose.yml            # Docker Compose setup
└── README.md                      # This file
```

## Features

- **Complete gRPC Service**: Implements all three operations from the protobuf service definition
- **EDI Parsing**: Parses EDI 850, 810, 856, and 997 message types
- **Validation**: Comprehensive EDI format and business rule validation
- **Error Handling**: Proper gRPC error responses with detailed messages
- **Extensible**: Easy to add new EDI message types
- **Testing**: Comprehensive unit tests
- **Docker Support**: Containerized deployment
- **Client Examples**: Ready-to-use client code

## Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Generate Protobuf Code**:
   ```bash
   python -m grpc_tools.protoc -I../proto --python_out=generated --grpc_python_out=generated ../proto/*.proto
   ```

3. **Run the Server**:
   ```bash
   python examples/server_example.py
   ```

4. **Test with Client**:
   ```bash
   python examples/client_example.py
   ```

## Service Operations

### 1. ProcessEdiMessage
Processes any EDI message type and returns structured data.

### 2. GetSupportedMessageTypes
Returns a list of supported EDI message types.

### 3. ValidateEdiMessage
Validates EDI message format without full processing.

## Supported EDI Types

- **EDI 850**: Purchase Order
- **EDI 810**: Invoice
- **EDI 856**: Advance Ship Notice
- **EDI 997**: Functional Acknowledgment

## Development

### Running Tests
```bash
python -m pytest tests/
```

### Code Generation
```bash
# Generate protobuf code
python -m grpc_tools.protoc -I../proto --python_out=generated --grpc_python_out=generated ../proto/*.proto

# Fix imports in generated files
python -c "
import os
for file in os.listdir('generated'):
    if file.endswith('_pb2_grpc.py'):
        with open(f'generated/{file}', 'r') as f:
            content = f.read()
        content = content.replace('import edi_service_pb2', 'from . import edi_service_pb2')
        content = content.replace('import edi_message_types_pb2', 'from . import edi_message_types_pb2')
        with open(f'generated/{file}', 'w') as f:
            f.write(content)
"
```

### Docker Deployment
```bash
# Build image
docker build -t edi-service .

# Run with docker-compose
docker-compose up
```

## Configuration

The service can be configured through environment variables:

- `EDI_SERVICE_HOST`: Server host (default: localhost)
- `EDI_SERVICE_PORT`: Server port (default: 50051)
- `EDI_LOG_LEVEL`: Logging level (default: INFO)
- `EDI_VALIDATION_STRICT`: Strict validation mode (default: true)

## API Documentation

The service implements the exact same API as defined in the protobuf files. See the generated protobuf code for detailed message definitions and field documentation.

## Contributing

1. Follow PEP 8 style guidelines
2. Add tests for new features
3. Update documentation as needed
4. Ensure all tests pass before submitting PRs
