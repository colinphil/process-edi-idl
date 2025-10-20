#!/usr/bin/env python3
"""
Basic tests for the EDI service.
"""

import sys
import unittest
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.edi_parser import EdiParser
from src.edi_validator import EdiValidator
from examples.test_messages import TEST_MESSAGES


class TestEdiParser(unittest.TestCase):
    """Test cases for EDI parser."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = EdiParser()
    
    def test_parse_850_message(self):
        """Test parsing EDI 850 message."""
        edi_message = TEST_MESSAGES["850"]
        result = self.parser.parse_message(edi_message, "850")
        
        self.assertTrue(result.success)
        self.assertIsNotNone(result.data)
        self.assertIsNotNone(result.segments)
        self.assertGreater(len(result.segments), 0)
    
    def test_parse_invalid_message_type(self):
        """Test parsing with invalid message type."""
        edi_message = TEST_MESSAGES["850"]
        result = self.parser.parse_message(edi_message, "999")
        
        self.assertFalse(result.success)
        self.assertIsNotNone(result.error_message)
    
    def test_split_into_segments(self):
        """Test splitting EDI message into segments."""
        edi_message = TEST_MESSAGES["850"]
        segments = self.parser._split_into_segments(edi_message)
        
        self.assertGreater(len(segments), 0)
        self.assertEqual(segments[0]["segment_id"], "ISA")
        self.assertEqual(segments[-1]["segment_id"], "IEA")


class TestEdiValidator(unittest.TestCase):
    """Test cases for EDI validator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = EdiValidator()
    
    def test_validate_850_format(self):
        """Test validating EDI 850 format."""
        edi_message = TEST_MESSAGES["850"]
        result = self.validator.validate_format(edi_message, "850")
        
        self.assertTrue(result.is_valid)
        self.assertFalse(result.has_errors)
    
    def test_validate_invalid_format(self):
        """Test validating invalid EDI format."""
        edi_message = TEST_MESSAGES["invalid"]
        result = self.validator.validate_format(edi_message, "850")
        
        self.assertFalse(result.is_valid)
        self.assertTrue(result.has_errors)
        self.assertGreater(len(result.messages), 0)
    
    def test_detect_edi_version(self):
        """Test detecting EDI version."""
        edi_message = TEST_MESSAGES["850"]
        version = self.validator.detect_edi_version(edi_message)
        
        self.assertEqual(version, "005010")
    
    def test_detect_message_type(self):
        """Test detecting message type."""
        edi_message = TEST_MESSAGES["850"]
        message_type = self.validator.detect_message_type(edi_message)
        
        self.assertEqual(message_type, "850")


if __name__ == "__main__":
    unittest.main()
