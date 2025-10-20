"""
EDI Validator Implementation

This module handles validation of EDI messages for format and business rules.
"""

import re
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from generated import edi_service_pb2
from src.utils import setup_logging

logger = setup_logging(__name__)


@dataclass
class ValidationResult:
    """Result of EDI message validation."""
    is_valid: bool
    messages: List[edi_service_pb2.ProcessingMessage]
    has_errors: bool = False


class EdiValidator:
    """Validator for EDI messages."""
    
    def __init__(self):
        """Initialize the EDI validator."""
        self.segment_patterns = {
            "850": {
                "required": ["ISA", "GS", "ST", "BEG", "SE", "GE", "IEA"],
                "optional": ["REF", "N1", "N3", "N4", "PO1", "CTT"]
            },
            "810": {
                "required": ["ISA", "GS", "ST", "BIG", "SE", "GE", "IEA"],
                "optional": ["REF", "N1", "N3", "N4", "IT1", "TDS", "CTT"]
            },
            "856": {
                "required": ["ISA", "GS", "ST", "BSN", "SE", "GE", "IEA"],
                "optional": ["REF", "N1", "N3", "N4", "HL", "PRF", "TD1", "TD5"]
            },
            "997": {
                "required": ["ISA", "GS", "ST", "AK1", "SE", "GE", "IEA"],
                "optional": ["AK2", "AK5", "AK9"]
            }
        }
        
        self.edi_version_patterns = {
            "004010": r"ISA\*[^*]*\*[^*]*\*[^*]*\*[^*]*\*[^*]*\*[^*]*\*[^*]*\*[^*]*\*[^*]*\*[^*]*\*[^*]*\*[^*]*\*[^*]*\*[^*]*\*[^*]*\*[^*]*\*004010",
            "005010": r"ISA\*[^*]*\*[^*]*\*[^*]*\*[^*]*\*[^*]*\*[^*]*\*[^*]*\*[^*]*\*[^*]*\*[^*]*\*[^*]*\*[^*]*\*[^*]*\*[^*]*\*[^*]*\*[^*]*\*[^*]*\*005010"
        }
    
    def validate_format(self, edi_message: str, message_type: str) -> ValidationResult:
        """
        Validate EDI message format.
        
        Args:
            edi_message: Raw EDI message content
            message_type: EDI message type (850, 810, 856, 997)
            
        Returns:
            ValidationResult containing validation status and messages
        """
        messages = []
        has_errors = False
        
        try:
            logger.debug(f"Validating EDI message format for type {message_type}")
            
            # Check if message type is supported
            if message_type not in self.segment_patterns:
                messages.append(edi_service_pb2.ProcessingMessage(
                    level=edi_service_pb2.MESSAGE_LEVEL_ERROR,
                    code="UNSUPPORTED_MESSAGE_TYPE",
                    message=f"Message type {message_type} is not supported"
                ))
                has_errors = True
                return ValidationResult(is_valid=False, messages=messages, has_errors=has_errors)
            
            # Split message into segments
            segments = self._split_into_segments(edi_message)
            
            if not segments:
                messages.append(edi_service_pb2.ProcessingMessage(
                    level=edi_service_pb2.MESSAGE_LEVEL_ERROR,
                    code="EMPTY_MESSAGE",
                    message="EDI message is empty or contains no valid segments"
                ))
                has_errors = True
                return ValidationResult(is_valid=False, messages=messages, has_errors=has_errors)
            
            # Validate ISA segment (Interchange Control Header)
            isa_validation = self._validate_isa_segment(segments[0])
            messages.extend(isa_validation.messages)
            if isa_validation.has_errors:
                has_errors = True
            
            # Validate required segments
            required_segments = self.segment_patterns[message_type]["required"]
            segment_ids = [seg["segment_id"] for seg in segments]
            
            for required_segment in required_segments:
                if required_segment not in segment_ids:
                    messages.append(edi_service_pb2.ProcessingMessage(
                        level=edi_service_pb2.MESSAGE_LEVEL_ERROR,
                        code="MISSING_REQUIRED_SEGMENT",
                        message=f"Required segment {required_segment} is missing",
                        field=required_segment
                    ))
                    has_errors = True
            
            # Validate segment order and structure
            structure_validation = self._validate_segment_structure(segments, message_type)
            messages.extend(structure_validation.messages)
            if structure_validation.has_errors:
                has_errors = True
            
            # Validate segment elements
            element_validation = self._validate_segment_elements(segments, message_type)
            messages.extend(element_validation.messages)
            if element_validation.has_errors:
                has_errors = True
            
            is_valid = not has_errors
            logger.debug(f"Format validation completed. Valid: {is_valid}, Errors: {has_errors}")
            
            return ValidationResult(is_valid=is_valid, messages=messages, has_errors=has_errors)
            
        except Exception as e:
            logger.error(f"Error during format validation: {str(e)}", exc_info=True)
            messages.append(edi_service_pb2.ProcessingMessage(
                level=edi_service_pb2.MESSAGE_LEVEL_ERROR,
                code="VALIDATION_ERROR",
                message=f"Validation error: {str(e)}"
            ))
            return ValidationResult(is_valid=False, messages=messages, has_errors=True)
    
    def validate_business_rules(self, parsed_data: Any, message_type: str) -> ValidationResult:
        """
        Validate business rules for parsed EDI data.
        
        Args:
            parsed_data: Parsed EDI data
            message_type: EDI message type
            
        Returns:
            ValidationResult containing validation status and messages
        """
        messages = []
        has_errors = False
        
        try:
            logger.debug(f"Validating business rules for type {message_type}")
            
            if message_type == "850":
                # Purchase Order business rules
                po_validation = self._validate_purchase_order_rules(parsed_data)
                messages.extend(po_validation.messages)
                has_errors = po_validation.has_errors
                
            elif message_type == "810":
                # Invoice business rules
                invoice_validation = self._validate_invoice_rules(parsed_data)
                messages.extend(invoice_validation.messages)
                has_errors = invoice_validation.has_errors
                
            elif message_type == "856":
                # Advance Ship Notice business rules
                asn_validation = self._validate_asn_rules(parsed_data)
                messages.extend(asn_validation.messages)
                has_errors = asn_validation.has_errors
                
            elif message_type == "997":
                # Functional Acknowledgment business rules
                fa_validation = self._validate_functional_ack_rules(parsed_data)
                messages.extend(fa_validation.messages)
                has_errors = fa_validation.has_errors
            
            is_valid = not has_errors
            logger.debug(f"Business rules validation completed. Valid: {is_valid}, Errors: {has_errors}")
            
            return ValidationResult(is_valid=is_valid, messages=messages, has_errors=has_errors)
            
        except Exception as e:
            logger.error(f"Error during business rules validation: {str(e)}", exc_info=True)
            messages.append(edi_service_pb2.ProcessingMessage(
                level=edi_service_pb2.MESSAGE_LEVEL_ERROR,
                code="BUSINESS_RULE_ERROR",
                message=f"Business rule validation error: {str(e)}"
            ))
            return ValidationResult(is_valid=False, messages=messages, has_errors=True)
    
    def detect_edi_version(self, edi_message: str) -> str:
        """Detect EDI version from message."""
        for version, pattern in self.edi_version_patterns.items():
            if re.search(pattern, edi_message):
                return version
        return "Unknown"
    
    def detect_message_type(self, edi_message: str) -> str:
        """Detect message type from ST segment."""
        st_match = re.search(r"ST\*(\d{3})", edi_message)
        if st_match:
            return st_match.group(1)
        return "Unknown"
    
    def _split_into_segments(self, edi_message: str) -> List[Dict[str, Any]]:
        """Split EDI message into segments."""
        segments = []
        lines = edi_message.strip().split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            # Split segment into elements
            elements = line.split('*')
            if len(elements) < 2:
                continue
                
            segment_id = elements[0]
            segment_data = {
                'segment_id': segment_id,
                'elements': elements[1:],
                'line_number': i + 1,
                'position': len(segments) + 1
            }
            segments.append(segment_data)
        
        return segments
    
    def _validate_isa_segment(self, isa_segment: Dict[str, Any]) -> ValidationResult:
        """Validate ISA segment structure."""
        messages = []
        has_errors = False
        
        if isa_segment["segment_id"] != "ISA":
            messages.append(edi_service_pb2.ProcessingMessage(
                level=edi_service_pb2.MESSAGE_LEVEL_ERROR,
                code="INVALID_ISA_SEGMENT",
                message="First segment must be ISA",
                field="ISA"
            ))
            has_errors = True
            return ValidationResult(is_valid=False, messages=messages, has_errors=has_errors)
        
        elements = isa_segment["elements"]
        if len(elements) < 16:
            messages.append(edi_service_pb2.ProcessingMessage(
                level=edi_service_pb2.MESSAGE_LEVEL_ERROR,
                code="INSUFFICIENT_ISA_ELEMENTS",
                message="ISA segment must have at least 16 elements",
                field="ISA"
            ))
            has_errors = True
        
        # Validate ISA element lengths
        isa_element_lengths = [2, 10, 2, 10, 2, 15, 2, 15, 6, 4, 1, 5, 2, 1, 1, 1]
        for i, expected_length in enumerate(isa_element_lengths):
            if i < len(elements):
                element = elements[i]
                if len(element) > expected_length:
                    messages.append(edi_service_pb2.ProcessingMessage(
                        level=edi_service_pb2.MESSAGE_LEVEL_WARNING,
                        code="ISA_ELEMENT_TOO_LONG",
                        message=f"ISA element {i+1} exceeds maximum length of {expected_length}",
                        field=f"ISA.{i+1}"
                    ))
        
        return ValidationResult(is_valid=not has_errors, messages=messages, has_errors=has_errors)
    
    def _validate_segment_structure(self, segments: List[Dict[str, Any]], message_type: str) -> ValidationResult:
        """Validate segment structure and order."""
        messages = []
        has_errors = False
        
        # Check for proper segment sequence
        expected_sequence = ["ISA", "GS", "ST"]
        segment_ids = [seg["segment_id"] for seg in segments]
        
        for i, expected_segment in enumerate(expected_sequence):
            if i < len(segment_ids) and segment_ids[i] != expected_segment:
                messages.append(edi_service_pb2.ProcessingMessage(
                    level=edi_service_pb2.MESSAGE_LEVEL_ERROR,
                    code="INVALID_SEGMENT_ORDER",
                    message=f"Expected {expected_segment} at position {i+1}, found {segment_ids[i]}",
                    field=expected_segment
                ))
                has_errors = True
        
        # Check for proper closing segments
        if segment_ids[-3:] != ["SE", "GE", "IEA"]:
            messages.append(edi_service_pb2.ProcessingMessage(
                level=edi_service_pb2.MESSAGE_LEVEL_ERROR,
                code="INVALID_CLOSING_SEGMENTS",
                message="Message must end with SE, GE, IEA segments",
                field="closing_segments"
            ))
            has_errors = True
        
        return ValidationResult(is_valid=not has_errors, messages=messages, has_errors=has_errors)
    
    def _validate_segment_elements(self, segments: List[Dict[str, Any]], message_type: str) -> ValidationResult:
        """Validate segment elements."""
        messages = []
        has_errors = False
        
        for segment in segments:
            segment_id = segment["segment_id"]
            elements = segment["elements"]
            
            # Basic element validation
            if segment_id == "ST" and len(elements) < 2:
                messages.append(edi_service_pb2.ProcessingMessage(
                    level=edi_service_pb2.MESSAGE_LEVEL_ERROR,
                    code="INSUFFICIENT_ST_ELEMENTS",
                    message="ST segment must have at least 2 elements",
                    field="ST",
                    line_number=segment["line_number"]
                ))
                has_errors = True
            
            elif segment_id == "BEG" and len(elements) < 3:
                messages.append(edi_service_pb2.ProcessingMessage(
                    level=edi_service_pb2.MESSAGE_LEVEL_ERROR,
                    code="INSUFFICIENT_BEG_ELEMENTS",
                    message="BEG segment must have at least 3 elements",
                    field="BEG",
                    line_number=segment["line_number"]
                ))
                has_errors = True
        
        return ValidationResult(is_valid=not has_errors, messages=messages, has_errors=has_errors)
    
    def _validate_purchase_order_rules(self, po_data: edi_service_pb2.PurchaseOrderData) -> ValidationResult:
        """Validate Purchase Order business rules."""
        messages = []
        has_errors = False
        
        # PO number must be present
        if not po_data.po_number:
            messages.append(edi_service_pb2.ProcessingMessage(
                level=edi_service_pb2.MESSAGE_LEVEL_ERROR,
                code="MISSING_PO_NUMBER",
                message="Purchase Order number is required",
                field="po_number"
            ))
            has_errors = True
        
        # Must have at least one line item
        if not po_data.line_items:
            messages.append(edi_service_pb2.ProcessingMessage(
                level=edi_service_pb2.MESSAGE_LEVEL_ERROR,
                code="NO_LINE_ITEMS",
                message="Purchase Order must have at least one line item",
                field="line_items"
            ))
            has_errors = True
        
        # Validate line items
        for i, line_item in enumerate(po_data.line_items):
            if not line_item.line_number:
                messages.append(edi_service_pb2.ProcessingMessage(
                    level=edi_service_pb2.MESSAGE_LEVEL_ERROR,
                    code="MISSING_LINE_NUMBER",
                    message=f"Line item {i+1} must have a line number",
                    field=f"line_items[{i}].line_number"
                ))
                has_errors = True
            
            if line_item.quantity_ordered.value <= 0:
                messages.append(edi_service_pb2.ProcessingMessage(
                    level=edi_service_pb2.MESSAGE_LEVEL_ERROR,
                    code="INVALID_QUANTITY",
                    message=f"Line item {i+1} quantity must be greater than 0",
                    field=f"line_items[{i}].quantity_ordered"
                ))
                has_errors = True
        
        return ValidationResult(is_valid=not has_errors, messages=messages, has_errors=has_errors)
    
    def _validate_invoice_rules(self, invoice_data: edi_service_pb2.InvoiceData) -> ValidationResult:
        """Validate Invoice business rules."""
        messages = []
        has_errors = False
        
        # Invoice number must be present
        if not invoice_data.invoice_number:
            messages.append(edi_service_pb2.ProcessingMessage(
                level=edi_service_pb2.MESSAGE_LEVEL_ERROR,
                code="MISSING_INVOICE_NUMBER",
                message="Invoice number is required",
                field="invoice_number"
            ))
            has_errors = True
        
        # Must have at least one line item
        if not invoice_data.line_items:
            messages.append(edi_service_pb2.ProcessingMessage(
                level=edi_service_pb2.MESSAGE_LEVEL_ERROR,
                code="NO_LINE_ITEMS",
                message="Invoice must have at least one line item",
                field="line_items"
            ))
            has_errors = True
        
        return ValidationResult(is_valid=not has_errors, messages=messages, has_errors=has_errors)
    
    def _validate_asn_rules(self, asn_data: edi_service_pb2.AdvanceShipNoticeData) -> ValidationResult:
        """Validate Advance Ship Notice business rules."""
        messages = []
        has_errors = False
        
        # Shipment ID must be present
        if not asn_data.shipment_id:
            messages.append(edi_service_pb2.ProcessingMessage(
                level=edi_service_pb2.MESSAGE_LEVEL_ERROR,
                code="MISSING_SHIPMENT_ID",
                message="Shipment ID is required",
                field="shipment_id"
            ))
            has_errors = True
        
        return ValidationResult(is_valid=not has_errors, messages=messages, has_errors=has_errors)
    
    def _validate_functional_ack_rules(self, fa_data: edi_service_pb2.FunctionalAcknowledgmentData) -> ValidationResult:
        """Validate Functional Acknowledgment business rules."""
        messages = []
        has_errors = False
        
        # Original transaction set ID must be present
        if not fa_data.original_transaction_set_id:
            messages.append(edi_service_pb2.ProcessingMessage(
                level=edi_service_pb2.MESSAGE_LEVEL_ERROR,
                code="MISSING_ORIGINAL_TRANSACTION_SET_ID",
                message="Original transaction set ID is required",
                field="original_transaction_set_id"
            ))
            has_errors = True
        
        return ValidationResult(is_valid=not has_errors, messages=messages, has_errors=has_errors)
