FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Generate protobuf code
RUN python -m grpc_tools.protoc -I../proto --python_out=generated --grpc_python_out=generated ../proto/*.proto

# Fix imports in generated files
RUN python -c "
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

# Create non-root user
RUN useradd -m -u 1000 edi && chown -R edi:edi /app
USER edi

# Expose port
EXPOSE 50051

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import grpc; grpc.channel_ready_future(grpc.insecure_channel('localhost:50051')).result(timeout=5)"

# Run the service
CMD ["python", "examples/server_example.py"]
