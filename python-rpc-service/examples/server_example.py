#!/usr/bin/env python3
"""
EDI Service Server Example

This script demonstrates how to run the EDI gRPC service.
"""

import os
import sys
import logging
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.edi_service import serve
from src.utils import setup_logging

logger = setup_logging(__name__)


def main():
    """Main entry point for the server."""
    # Get configuration from environment variables
    host = os.getenv("EDI_SERVICE_HOST", "localhost")
    port = int(os.getenv("EDI_SERVICE_PORT", "50051"))
    max_workers = int(os.getenv("EDI_MAX_WORKERS", "10"))
    
    logger.info(f"Starting EDI Service Server")
    logger.info(f"Host: {host}")
    logger.info(f"Port: {port}")
    logger.info(f"Max Workers: {max_workers}")
    
    try:
        serve(host, port, max_workers)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
