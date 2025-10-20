#!/usr/bin/env python3
"""
EDI Service Client Example

This script demonstrates how to use the EDI gRPC service client.
"""

import os
import sys
import logging
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import grpc
from generated import edi_service_pb2
from generated import edi_service_pb2_grpc
from src.utils import setup_logging

logger = setup_logging(__name__)


def create_channel(host: str = "localhost", port: int = 50051) -> grpc.Channel:
    """Create a gRPC channel."""
    address = f"{host}:{port}"
    logger.info(f"Connecting to EDI service at {address}")
    return grpc.insecure_channel(address)


def test_process_edi_message(client: edi_service_pb2_grpc.EdiServiceStub):
    """Test the ProcessEdiMessage RPC."""
    logger.info("Testing ProcessEdiMessage...")
    
    # Sample EDI 850 Purchase Order message
    edi_message = """ISA*00*          *00*          *ZZ*SENDER         *ZZ*RECEIVER       *210101*1200*^*00501*000000001*0*P*>~
GS*PO*SENDER*RECEIVER*20210101*1200*1*X*005010~
ST*850*0001~
BEG*00*SA*PO123456**20210101~
REF*DP*DEPARTMENT123~
N1*BY*ACME CORP*92*12345~
N3*123 MAIN ST~
N4*NEW YORK*NY*10001~
N1*ST*ACME CORP*92*12345~
N3*123 MAIN ST~
N4*NEW YORK*NY*10001~
PO1*1*10*EA*25.50**VP*SKU123*PD*WIDGET~
PO1*2*5*EA*15.75**VP*SKU456*PD*GADGET~
CTT*2~
SE*15*0001~
GE*1*1~
IEA*1*000000001~"""
    
    # Create request
    request = edi_service_pb2.ProcessEdiMessageRequest(
        edi_message=edi_message,
        message_type="850",
        customer_id="CUSTOMER123",
        options=edi_service_pb2.ProcessingOptions(
            validate_format=True,
            validate_business_rules=True,
            include_parsing_details=True,
            include_raw_segments=True
        )
    )
    
    try:
        # Call the service
        response = client.ProcessEdiMessage(request)
        
        logger.info(f"Processing Status: {response.status}")
        logger.info(f"Message Type: {response.message_type}")
        logger.info(f"Processed At: {response.processed_at}")
        
        if response.purchase_order:
            po = response.purchase_order
            logger.info(f"PO Number: {po.po_number}")
            logger.info(f"PO Date: {po.po_date}")
            logger.info(f"Number of Line Items: {len(po.line_items)}")
            
            for item in po.line_items:
                logger.info(f"  Line {item.line_number}: {item.product.description} - Qty: {item.quantity_ordered.value}")
        
        if response.messages:
            logger.info("Processing Messages:")
            for msg in response.messages:
                logger.info(f"  {msg.level}: {msg.message}")
        
        if response.parsed_segments:
            logger.info(f"Parsed Segments: {len(response.parsed_segments)}")
            
    except grpc.RpcError as e:
        logger.error(f"gRPC Error: {e.code()} - {e.details()}")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)


def test_get_supported_message_types(client: edi_service_pb2_grpc.EdiServiceStub):
    """Test the GetSupportedMessageTypes RPC."""
    logger.info("Testing GetSupportedMessageTypes...")
    
    request = edi_service_pb2.GetSupportedMessageTypesRequest(
        customer_id="CUSTOMER123"
    )
    
    try:
        response = client.GetSupportedMessageTypes(request)
        
        logger.info("Supported EDI Message Types:")
        for msg_type in response.supported_types:
            logger.info(f"  {msg_type.code}: {msg_type.name}")
            logger.info(f"    Description: {msg_type.description}")
            logger.info(f"    Supported: {msg_type.supported}")
            if msg_type.required_segments:
                logger.info(f"    Required Segments: {', '.join(msg_type.required_segments)}")
            logger.info("")
            
    except grpc.RpcError as e:
        logger.error(f"gRPC Error: {e.code()} - {e.details()}")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)


def test_validate_edi_message(client: edi_service_pb2_grpc.EdiServiceStub):
    """Test the ValidateEdiMessage RPC."""
    logger.info("Testing ValidateEdiMessage...")
    
    # Sample EDI message with some issues
    edi_message = """ISA*00*          *00*          *ZZ*SENDER         *ZZ*RECEIVER       *210101*1200*^*00501*000000001*0*P*>~
GS*PO*SENDER*RECEIVER*20210101*1200*1*X*005010~
ST*850*0001~
BEG*00*SA*PO123456**20210101~
SE*15*0001~
GE*1*1~
IEA*1*000000001~"""
    
    request = edi_service_pb2.ValidateEdiMessageRequest(
        edi_message=edi_message,
        message_type="850",
        customer_id="CUSTOMER123"
    )
    
    try:
        response = client.ValidateEdiMessage(request)
        
        logger.info(f"Validation Status: {response.status}")
        logger.info(f"Detected Message Type: {response.detected_message_type}")
        logger.info(f"EDI Version: {response.edi_version}")
        
        if response.messages:
            logger.info("Validation Messages:")
            for msg in response.messages:
                logger.info(f"  {msg.level}: {msg.message}")
                if msg.field:
                    logger.info(f"    Field: {msg.field}")
                if msg.line_number:
                    logger.info(f"    Line: {msg.line_number}")
                    
    except grpc.RpcError as e:
        logger.error(f"gRPC Error: {e.code()} - {e.details()}")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)


def main():
    """Main entry point for the client."""
    # Get configuration from environment variables
    host = os.getenv("EDI_SERVICE_HOST", "localhost")
    port = int(os.getenv("EDI_SERVICE_PORT", "50051"))
    
    # Create channel and client
    channel = create_channel(host, port)
    client = edi_service_pb2_grpc.EdiServiceStub(channel)
    
    try:
        # Test all RPC methods
        test_get_supported_message_types(client)
        test_validate_edi_message(client)
        test_process_edi_message(client)
        
        logger.info("All tests completed successfully!")
        
    except Exception as e:
        logger.error(f"Client error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        channel.close()


if __name__ == "__main__":
    main()
