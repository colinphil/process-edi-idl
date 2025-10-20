"""
EDI Parser Implementation

This module handles parsing of EDI messages into structured data.
"""

import re
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime

from generated import edi_service_pb2
from src.utils import setup_logging

logger = setup_logging(__name__)


@dataclass
class ParseResult:
    """Result of EDI message parsing."""
    success: bool
    data: Optional[Any] = None
    segments: List[edi_service_pb2.EdiSegment] = None
    error_message: Optional[str] = None


class EdiParser:
    """Parser for EDI messages."""
    
    def __init__(self):
        """Initialize the EDI parser."""
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
    
    def parse_message(self, edi_message: str, message_type: str) -> ParseResult:
        """
        Parse an EDI message into structured data.
        
        Args:
            edi_message: Raw EDI message content
            message_type: EDI message type (850, 810, 856, 997)
            
        Returns:
            ParseResult containing parsed data or error information
        """
        try:
            logger.debug(f"Parsing EDI message of type {message_type}")
            
            # Split message into segments
            segments = self._split_into_segments(edi_message)
            
            # Parse segments into structured data
            if message_type == "850":
                data = self._parse_purchase_order(segments)
            elif message_type == "810":
                data = self._parse_invoice(segments)
            elif message_type == "856":
                data = self._parse_advance_ship_notice(segments)
            elif message_type == "997":
                data = self._parse_functional_acknowledgment(segments)
            else:
                return ParseResult(
                    success=False,
                    error_message=f"Unsupported message type: {message_type}"
                )
            
            # Convert segments to protobuf format
            pb_segments = self._convert_segments_to_pb(segments)
            
            return ParseResult(
                success=True,
                data=data,
                segments=pb_segments
            )
            
        except Exception as e:
            logger.error(f"Error parsing EDI message: {str(e)}", exc_info=True)
            return ParseResult(
                success=False,
                error_message=f"Parsing error: {str(e)}"
            )
    
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
    
    def _convert_segments_to_pb(self, segments: List[Dict[str, Any]]) -> List[edi_service_pb2.EdiSegment]:
        """Convert segments to protobuf format."""
        pb_segments = []
        for segment in segments:
            pb_segment = edi_service_pb2.EdiSegment(
                segment_id=segment['segment_id'],
                elements=segment['elements'],
                line_number=segment['line_number'],
                position=segment['position']
            )
            pb_segments.append(pb_segment)
        return pb_segments
    
    def _parse_purchase_order(self, segments: List[Dict[str, Any]]) -> edi_service_pb2.PurchaseOrderData:
        """Parse EDI 850 Purchase Order."""
        po_data = edi_service_pb2.PurchaseOrderData()
        
        for segment in segments:
            segment_id = segment['segment_id']
            elements = segment['elements']
            
            if segment_id == "BEG":
                # Purchase Order Beginning Segment
                if len(elements) >= 2:
                    po_data.po_number = elements[1] if len(elements) > 1 else ""
                if len(elements) >= 3:
                    po_data.po_date = elements[2] if len(elements) > 2 else ""
                    
            elif segment_id == "PO1":
                # Purchase Order Line Item
                line_item = edi_service_pb2.PurchaseOrderLineItem()
                if len(elements) >= 1:
                    line_item.line_number = elements[0]
                if len(elements) >= 2:
                    line_item.quantity_ordered.value = float(elements[1]) if elements[1] else 0.0
                if len(elements) >= 3:
                    line_item.quantity_ordered.unit_of_measure = elements[2]
                if len(elements) >= 4:
                    line_item.unit_price.value = float(elements[3]) if elements[3] else 0.0
                if len(elements) >= 5:
                    line_item.product.description = elements[4]
                if len(elements) >= 6:
                    line_item.product.product_id = elements[5]
                
                po_data.line_items.append(line_item)
                
            elif segment_id == "N1":
                # Name/Address Segment
                if len(elements) >= 2:
                    entity_code = elements[0]
                    name = elements[1]
                    
                    party = edi_service_pb2.Party(
                        entity_identifier_code=entity_code,
                        name=name
                    )
                    
                    if entity_code == "BY":  # Buyer
                        po_data.buyer.CopyFrom(party)
                    elif entity_code == "SE":  # Seller
                        po_data.seller.CopyFrom(party)
                    elif entity_code == "ST":  # Ship To
                        po_data.ship_to.CopyFrom(party)
                    elif entity_code == "BT":  # Bill To
                        po_data.bill_to.CopyFrom(party)
        
        return po_data
    
    def _parse_invoice(self, segments: List[Dict[str, Any]]) -> edi_service_pb2.InvoiceData:
        """Parse EDI 810 Invoice."""
        invoice_data = edi_service_pb2.InvoiceData()
        
        for segment in segments:
            segment_id = segment['segment_id']
            elements = segment['elements']
            
            if segment_id == "BIG":
                # Invoice Beginning Segment
                if len(elements) >= 1:
                    invoice_data.invoice_date = elements[0]
                if len(elements) >= 2:
                    invoice_data.invoice_number = elements[1]
                if len(elements) >= 3:
                    invoice_data.due_date = elements[2]
                    
            elif segment_id == "IT1":
                # Invoice Line Item
                line_item = edi_service_pb2.InvoiceLineItem()
                if len(elements) >= 1:
                    line_item.line_number = elements[0]
                if len(elements) >= 2:
                    line_item.quantity_invoiced.value = float(elements[1]) if elements[1] else 0.0
                if len(elements) >= 3:
                    line_item.quantity_invoiced.unit_of_measure = elements[2]
                if len(elements) >= 4:
                    line_item.unit_price.value = float(elements[3]) if elements[3] else 0.0
                if len(elements) >= 5:
                    line_item.product.description = elements[4]
                if len(elements) >= 6:
                    line_item.product.product_id = elements[5]
                
                invoice_data.line_items.append(line_item)
                
            elif segment_id == "N1":
                # Name/Address Segment
                if len(elements) >= 2:
                    entity_code = elements[0]
                    name = elements[1]
                    
                    party = edi_service_pb2.Party(
                        entity_identifier_code=entity_code,
                        name=name
                    )
                    
                    if entity_code == "BT":  # Bill To
                        invoice_data.bill_to.CopyFrom(party)
                    elif entity_code == "RE":  # Remit To
                        invoice_data.remit_to.CopyFrom(party)
                    elif entity_code == "SF":  # Ship From
                        invoice_data.ship_from.CopyFrom(party)
                    elif entity_code == "ST":  # Ship To
                        invoice_data.ship_to.CopyFrom(party)
        
        return invoice_data
    
    def _parse_advance_ship_notice(self, segments: List[Dict[str, Any]]) -> edi_service_pb2.AdvanceShipNoticeData:
        """Parse EDI 856 Advance Ship Notice."""
        asn_data = edi_service_pb2.AdvanceShipNoticeData()
        
        for segment in segments:
            segment_id = segment['segment_id']
            elements = segment['elements']
            
            if segment_id == "BSN":
                # Ship Notice Beginning Segment
                if len(elements) >= 1:
                    asn_data.shipment_id = elements[0]
                if len(elements) >= 2:
                    asn_data.shipment_date = elements[1]
                if len(elements) >= 3:
                    asn_data.expected_delivery_date = elements[2]
                    
            elif segment_id == "HL":
                # Hierarchical Level
                # This would be used to parse shipment details
                pass
                
            elif segment_id == "N1":
                # Name/Address Segment
                if len(elements) >= 2:
                    entity_code = elements[0]
                    name = elements[1]
                    
                    party = edi_service_pb2.Party(
                        entity_identifier_code=entity_code,
                        name=name
                    )
                    
                    if entity_code == "SF":  # Ship From
                        asn_data.ship_from.CopyFrom(party)
                    elif entity_code == "ST":  # Ship To
                        asn_data.ship_to.CopyFrom(party)
                    elif entity_code == "BT":  # Bill To
                        asn_data.bill_to.CopyFrom(party)
                    elif entity_code == "CA":  # Carrier
                        asn_data.carrier.CopyFrom(party)
        
        return asn_data
    
    def _parse_functional_acknowledgment(self, segments: List[Dict[str, Any]]) -> edi_service_pb2.FunctionalAcknowledgmentData:
        """Parse EDI 997 Functional Acknowledgment."""
        fa_data = edi_service_pb2.FunctionalAcknowledgmentData()
        
        for segment in segments:
            segment_id = segment['segment_id']
            elements = segment['elements']
            
            if segment_id == "AK1":
                # Functional Group Response Header
                if len(elements) >= 1:
                    fa_data.original_transaction_set_id = elements[0]
                if len(elements) >= 2:
                    fa_data.original_control_number = elements[1]
                if len(elements) >= 3:
                    fa_data.acknowledgment_code = elements[2]
                    
            elif segment_id == "AK2":
                # Transaction Set Response Header
                transaction_ack = edi_service_pb2.TransactionSetAcknowledgment()
                if len(elements) >= 1:
                    transaction_ack.transaction_set_id = elements[0]
                if len(elements) >= 2:
                    transaction_ack.control_number = elements[1]
                if len(elements) >= 3:
                    transaction_ack.acknowledgment_code = elements[2]
                
                fa_data.transaction_set_acks.append(transaction_ack)
                
            elif segment_id == "AK5":
                # Transaction Set Response Trailer
                if len(elements) >= 1:
                    fa_data.acknowledgment_code = elements[0]
        
        return fa_data
