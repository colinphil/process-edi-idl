#!/usr/bin/env python3
"""
Build script for the Python EDI service.

This script handles code generation, testing, and building the service.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def run_command(cmd: list, cwd: Path = None) -> bool:
    """Run a command and return success status."""
    try:
        result = subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)
        print(f"✓ {' '.join(cmd)}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {' '.join(cmd)}")
        print(f"Error: {e.stderr}")
        return False


def generate_protobuf_code():
    """Generate Python protobuf code."""
    print("Generating protobuf code...")
    
    project_root = Path(__file__).parent
    proto_dir = project_root / "proto"
    generated_dir = project_root / "generated"
    
    # Ensure generated directory exists
    generated_dir.mkdir(exist_ok=True)
    
    # Generate protobuf code
    cmd = [
        "python3", "-m", "grpc_tools.protoc",
        "-I", str(proto_dir),
        "--python_out", str(generated_dir),
        "--grpc_python_out", str(generated_dir),
        str(proto_dir / "edi_service.proto")
    ]
    
    if not run_command(cmd):
        return False
    
    # Fix imports in generated files
    print("Fixing imports in generated files...")
    for file in generated_dir.glob("*_pb2_grpc.py"):
        with open(file, 'r') as f:
            content = f.read()
        
        content = content.replace('import edi_service_pb2', 'from . import edi_service_pb2')
        content = content.replace('import edi_message_types_pb2', 'from . import edi_message_types_pb2')
        
        with open(file, 'w') as f:
            f.write(content)
    
    print("✓ Protobuf code generated successfully")
    return True


def install_dependencies():
    """Install Python dependencies."""
    print("Installing dependencies...")
    
    project_root = Path(__file__).parent
    requirements_file = project_root / "requirements.txt"
    
    cmd = ["python3", "-m", "pip", "install", "-r", str(requirements_file)]
    
    if run_command(cmd):
        print("✓ Dependencies installed successfully")
        return True
    else:
        print("✗ Failed to install dependencies")
        return False


def run_tests():
    """Run unit tests."""
    print("Running tests...")
    
    project_root = Path(__file__).parent
    
    cmd = ["python3", "-m", "unittest", "discover", "-s", "tests", "-v"]
    
    if run_command(cmd, cwd=project_root):
        print("✓ Tests passed successfully")
        return True
    else:
        print("✗ Tests failed")
        return False


def lint_code():
    """Run code linting."""
    print("Running code linting...")
    
    project_root = Path(__file__).parent
    
    # Run flake8
    cmd = ["python3", "-m", "flake8", "src", "examples", "tests"]
    
    if run_command(cmd, cwd=project_root):
        print("✓ Code linting passed")
        return True
    else:
        print("✗ Code linting failed")
        return False


def format_code():
    """Format code with black."""
    print("Formatting code...")
    
    project_root = Path(__file__).parent
    
    cmd = ["python3", "-m", "black", "src", "examples", "tests"]
    
    if run_command(cmd, cwd=project_root):
        print("✓ Code formatted successfully")
        return True
    else:
        print("✗ Code formatting failed")
        return False


def build_docker():
    """Build Docker image."""
    print("Building Docker image...")
    
    project_root = Path(__file__).parent
    
    cmd = ["docker", "build", "-t", "edi-service", "."]
    
    if run_command(cmd, cwd=project_root):
        print("✓ Docker image built successfully")
        return True
    else:
        print("✗ Docker build failed")
        return False


def main():
    """Main build function."""
    print("Building Python EDI Service...")
    print("=" * 50)
    
    success = True
    
    # Generate protobuf code
    if not generate_protobuf_code():
        success = False
    
    # Install dependencies
    if not install_dependencies():
        success = False
    
    # Format code
    if not format_code():
        success = False
    
    # Lint code
    if not lint_code():
        success = False
    
    # Run tests
    if not run_tests():
        success = False
    
    # Build Docker image (optional)
    if os.getenv("BUILD_DOCKER", "false").lower() == "true":
        if not build_docker():
            success = False
    
    print("=" * 50)
    if success:
        print("✓ Build completed successfully!")
        sys.exit(0)
    else:
        print("✗ Build failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
