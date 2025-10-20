"""
EDI Service Implementation

This module implements the gRPC EDI service with business logic for processing
EDI messages of various types (850, 810, 856, 997).
"""

import grpc
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from concurrent import futures

from generated import edi_service_pb2
from generated import edi_service_pb2_grpc
from src.edi_parser import EdiParser
from src.edi_validator import EdiValidator
from src.utils import setup_logging

logger = setup_logging(__name__)


class EdiServiceServicer(edi_service_pb2_grpc.EdiServiceServicer):
    """Implementation of the EDI service."""
    
    def __init__(self):
        """Initialize the EDI service."""
        self.parser = EdiParser()
        self.validator = EdiValidator()
        self.supported_types = self._initialize_supported_types()
        
    def _initialize_supported_types(self) -> List[edi_service_pb2.EdiMessageType]:
        """Initialize the list of supported EDI message types."""
        return [
            edi_service_pb2.EdiMessageType(
                code="850",
                name="Purchase Order",
                description="EDI 850 Purchase Order transaction set",
                supported=True,
                required_segments=["ISA", "GS", "ST", "BEG", "SE", "GE", "IEA"],
                optional_segments=["REF", "N1", "N3", "N4", "PO1", "CTT"]
            ),
            edi_service_pb2.EdiMessageType(
                code="810",
                name="Invoice",
                description="EDI 810 Invoice transaction set",
                supported=True,
                required_segments=["ISA", "GS", "ST", "BIG", "SE", "GE", "IEA"],
                optional_segments=["REF", "N1", "N3", "N4", "IT1", "TDS", "CTT"]
            ),
            edi_service_pb2.EdiMessageType(
                code="856",
                name="Advance Ship Notice",
                description="EDI 856 Advance Ship Notice transaction set",
                supported=True,
                required_segments=["ISA", "GS", "ST", "BSN", "SE", "GE", "IEA"],
                optional_segments=["REF", "N1", "N3", "N4", "HL", "PRF", "TD1", "TD5"]
            ),
            edi_service_pb2.EdiMessageType(
                code="997",
                name="Functional Acknowledgment",
                description="EDI 997 Functional Acknowledgment transaction set",
                supported=True,
                required_segments=["ISA", "GS", "ST", "AK1", "SE", "GE", "IEA"],
                optional_segments=["AK2", "AK5", "AK9"]
            )
        ]
    
    def ProcessEdiMessage(self, request: edi_service_pb2.ProcessEdiMessageRequest, context: grpc.ServicerContext) -> edi_service_pb2.ProcessEdiMessageResponse:
        """
        Process any EDI message type.
        
        Args:
            request: The EDI message processing request
            context: gRPC service context
            
        Returns:
            ProcessEdiMessageResponse containing parsed data and processing status
        """
        try:
            logger.info(f"Processing EDI message of type {request.message_type} for customer {request.customer_id}")
            
            # Validate message type is supported
            if not self._is_message_type_supported(request.message_type):
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(f"Unsupported message type: {request.message_type}")
                return edi_service_pb2.ProcessEdiMessageResponse(
                    status=edi_service_pb2.PROCESSING_STATUS_UNSUPPORTED_MESSAGE_TYPE,
                    message_type=request.message_type,
                    processed_at=datetime.now().isoformat(),
                    messages=[
                        edi_service_pb2.ProcessingMessage(
                            level=edi_service_pb2.MESSAGE_LEVEL_ERROR,
                            code="UNSUPPORTED_MESSAGE_TYPE",
                            message=f"Message type {request.message_type} is not supported"
                        )
                    ]
                )
            
            # Validate EDI message format if requested
            messages = []
            if request.options and request.options.validate_format:
                validation_result = self.validator.validate_format(request.edi_message, request.message_type)
                if not validation_result.is_valid:
                    messages.extend(validation_result.messages)
                    if validation_result.has_errors:
                        return edi_service_pb2.ProcessEdiMessageResponse(
                            status=edi_service_pb2.PROCESSING_STATUS_VALIDATION_ERROR,
                            message_type=request.message_type,
                            processed_at=datetime.now().isoformat(),
                            messages=messages
                        )
            
            # Parse the EDI message
            parse_result = self.parser.parse_message(request.edi_message, request.message_type)
            
            if not parse_result.success:
                return edi_service_pb2.ProcessEdiMessageResponse(
                    status=edi_service_pb2.PROCESSING_STATUS_PARSING_ERROR,
                    message_type=request.message_type,
                    processed_at=datetime.now().isoformat(),
                    messages=[
                        edi_service_pb2.ProcessingMessage(
                            level=edi_service_pb2.MESSAGE_LEVEL_ERROR,
                            code="PARSING_ERROR",
                            message=parse_result.error_message
                        )
                    ]
                )
            
            # Validate business rules if requested
            if request.options and request.options.validate_business_rules:
                business_validation = self.validator.validate_business_rules(parse_result.data, request.message_type)
                if not business_validation.is_valid:
                    messages.extend(business_validation.messages)
                    if business_validation.has_errors:
                        return edi_service_pb2.ProcessEdiMessageResponse(
                            status=edi_service_pb2.PROCESSING_STATUS_BUSINESS_RULE_ERROR,
                            message_type=request.message_type,
                            processed_at=datetime.now().isoformat(),
                            messages=messages
                        )
            
            # Create response with parsed data
            response = edi_service_pb2.ProcessEdiMessageResponse(
                status=edi_service_pb2.PROCESSING_STATUS_SUCCESS,
                message_type=request.message_type,
                processed_at=datetime.now().isoformat(),
                messages=messages
            )
            
            # Set the appropriate parsed data based on message type
            if request.message_type == "850":
                response.purchase_order.CopyFrom(parse_result.data)
            elif request.message_type == "810":
                response.invoice.CopyFrom(parse_result.data)
            elif request.message_type == "856":
                response.advance_ship_notice.CopyFrom(parse_result.data)
            elif request.message_type == "997":
                response.functional_acknowledgment.CopyFrom(parse_result.data)
            
            # Add parsed segments if requested
            if request.options and request.options.include_raw_segments:
                response.parsed_segments.extend(parse_result.segments)
            
            logger.info(f"Successfully processed EDI message of type {request.message_type}")
            return response
            
        except Exception as e:
            logger.error(f"Error processing EDI message: {str(e)}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal error: {str(e)}")
            return edi_service_pb2.ProcessEdiMessageResponse(
                status=edi_service_pb2.PROCESSING_STATUS_INTERNAL_ERROR,
                message_type=request.message_type,
                processed_at=datetime.now().isoformat(),
                messages=[
                    edi_service_pb2.ProcessingMessage(
                        level=edi_service_pb2.MESSAGE_LEVEL_ERROR,
                        code="INTERNAL_ERROR",
                        message=f"Internal server error: {str(e)}"
                    )
                ]
            )
    
    def GetSupportedMessageTypes(self, request: edi_service_pb2.GetSupportedMessageTypesRequest, context: grpc.ServicerContext) -> edi_service_pb2.GetSupportedMessageTypesResponse:
        """
        Get supported EDI message types.
        
        Args:
            request: The request for supported message types
            context: gRPC service context
            
        Returns:
            GetSupportedMessageTypesResponse containing list of supported types
        """
        try:
            logger.info(f"Getting supported message types for customer {request.customer_id}")
            
            # Filter by customer if specified (could be used for customer-specific configurations)
            supported_types = self.supported_types
            if request.customer_id:
                # In a real implementation, you might filter based on customer capabilities
                logger.debug(f"Filtering supported types for customer {request.customer_id}")
            
            return edi_service_pb2.GetSupportedMessageTypesResponse(
                supported_types=supported_types
            )
            
        except Exception as e:
            logger.error(f"Error getting supported message types: {str(e)}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal error: {str(e)}")
            return edi_service_pb2.GetSupportedMessageTypesResponse()
    
    def ValidateEdiMessage(self, request: edi_service_pb2.ValidateEdiMessageRequest, context: grpc.ServicerContext) -> edi_service_pb2.ValidateEdiMessageResponse:
        """
        Validate EDI message format without processing.
        
        Args:
            request: The EDI message validation request
            context: gRPC service context
            
        Returns:
            ValidateEdiMessageResponse containing validation status and messages
        """
        try:
            logger.info(f"Validating EDI message of type {request.message_type} for customer {request.customer_id}")
            
            # Validate message type is supported
            if not self._is_message_type_supported(request.message_type):
                return edi_service_pb2.ValidateEdiMessageResponse(
                    status=edi_service_pb2.PROCESSING_STATUS_UNSUPPORTED_MESSAGE_TYPE,
                    messages=[
                        edi_service_pb2.ProcessingMessage(
                            level=edi_service_pb2.MESSAGE_LEVEL_ERROR,
                            code="UNSUPPORTED_MESSAGE_TYPE",
                            message=f"Message type {request.message_type} is not supported"
                        )
                    ]
                )
            
            # Perform format validation
            validation_result = self.validator.validate_format(request.edi_message, request.message_type)
            
            # Detect EDI version and message type
            detected_version = self.validator.detect_edi_version(request.edi_message)
            detected_message_type = self.validator.detect_message_type(request.edi_message)
            
            return edi_service_pb2.ValidateEdiMessageResponse(
                status=edi_service_pb2.PROCESSING_STATUS_SUCCESS if validation_result.is_valid else edi_service_pb2.PROCESSING_STATUS_VALIDATION_ERROR,
                messages=validation_result.messages,
                edi_version=detected_version,
                detected_message_type=detected_message_type
            )
            
        except Exception as e:
            logger.error(f"Error validating EDI message: {str(e)}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal error: {str(e)}")
            return edi_service_pb2.ValidateEdiMessageResponse(
                status=edi_service_pb2.PROCESSING_STATUS_INTERNAL_ERROR,
                messages=[
                    edi_service_pb2.ProcessingMessage(
                        level=edi_service_pb2.MESSAGE_LEVEL_ERROR,
                        code="INTERNAL_ERROR",
                        message=f"Internal server error: {str(e)}"
                    )
                ]
            )
    
    def _is_message_type_supported(self, message_type: str) -> bool:
        """Check if a message type is supported."""
        return any(msg_type.code == message_type for msg_type in self.supported_types)


def serve(host: str = "localhost", port: int = 50051, max_workers: int = 10):
    """
    Start the gRPC server.
    
    Args:
        host: Server host address
        port: Server port
        max_workers: Maximum number of worker threads
    """
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
    edi_service_pb2_grpc.add_EdiServiceServicer_to_server(EdiServiceServicer(), server)
    
    listen_addr = f"{host}:{port}"
    server.add_insecure_port(listen_addr)
    
    logger.info(f"Starting EDI service on {listen_addr}")
    server.start()
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Shutting down EDI service")
        server.stop(0)


def main():
    """Main entry point for the service."""
    import os
    
    host = os.getenv("EDI_SERVICE_HOST", "localhost")
    port = int(os.getenv("EDI_SERVICE_PORT", "50051"))
    max_workers = int(os.getenv("EDI_MAX_WORKERS", "10"))
    
    serve(host, port, max_workers)


if __name__ == "__main__":
    main()
