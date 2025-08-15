#!/usr/bin/env python3
"""
SmoothBooks Setup Script
This script helps set up the SmoothBooks accounting software.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, cwd=None):
    """Run a command and return the result."""
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required.")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def check_node_version():
    """Check if Node.js is installed."""
    success, stdout, stderr = run_command("node --version")
    if not success:
        print("❌ Node.js is not installed. Please install Node.js 16 or higher.")
        return False
    print(f"✅ Node.js {stdout.strip()} detected")
    return True

def setup_backend():
    """Set up the backend environment."""
    print("\n🔧 Setting up Backend...")
    
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found!")
        return False
    
    # Create virtual environment
    venv_path = backend_dir / "venv"
    if not venv_path.exists():
        print("Creating virtual environment...")
        success, stdout, stderr = run_command("python -m venv venv", cwd=backend_dir)
        if not success:
            print(f"❌ Failed to create virtual environment: {stderr}")
            return False
        print("✅ Virtual environment created")
    
    # Install dependencies
    print("Installing Python dependencies...")
    if os.name == 'nt':  # Windows
        pip_cmd = "venv\\Scripts\\pip install -r requirements.txt"
    else:  # Unix/Linux/macOS
        pip_cmd = "venv/bin/pip install -r requirements.txt"
    
    success, stdout, stderr = run_command(pip_cmd, cwd=backend_dir)
    if not success:
        print(f"❌ Failed to install dependencies: {stderr}")
        return False
    print("✅ Python dependencies installed")
    
    # Create .env file if it doesn't exist
    env_file = backend_dir / ".env"
    env_example = backend_dir / "env.example"
    
    if not env_file.exists() and env_example.exists():
        print("Creating .env file from template...")
        shutil.copy(env_example, env_file)
        print("✅ .env file created (please update with your configuration)")
    
    return True

def setup_frontend():
    """Set up the frontend environment."""
    print("\n🔧 Setting up Frontend...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found!")
        return False
    
    # Install dependencies
    print("Installing Node.js dependencies...")
    success, stdout, stderr = run_command("npm install", cwd=frontend_dir)
    if not success:
        print(f"❌ Failed to install dependencies: {stderr}")
        return False
    print("✅ Node.js dependencies installed")
    
    return True

def create_start_scripts():
    """Create start scripts for different platforms."""
    print("\n📝 Creating start scripts...")
    
    # Windows batch file (already exists)
    if os.name == 'nt':
        print("✅ Windows start script (start.bat) already exists")
    
    # Unix/Linux/macOS shell script
    if os.name != 'nt':
        start_sh_content = """#!/bin/bash
echo "Starting SmoothBooks Accounting Software..."
echo ""

echo "Starting Backend Server..."
cd backend
source venv/bin/activate
python app.py &
BACKEND_PID=$!

echo ""
echo "Starting Frontend Server..."
cd ../frontend
npm start &
FRONTEND_PID=$!

echo ""
echo "SmoothBooks is starting up!"
echo "Backend: http://localhost:5000"
echo "Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers..."

# Wait for user to stop
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
"""
        
        with open("start.sh", "w") as f:
            f.write(start_sh_content)
        
        # Make executable
        os.chmod("start.sh", 0o755)
        print("✅ Unix/Linux/macOS start script (start.sh) created")

def main():
    """Main setup function."""
    print("🚀 SmoothBooks Setup Script")
    print("=" * 40)
    
    # Check prerequisites
    if not check_python_version():
        return
    
    if not check_node_version():
        return
    
    # Setup backend
    if not setup_backend():
        print("❌ Backend setup failed!")
        return
    
    # Setup frontend
    if not setup_frontend():
        print("❌ Frontend setup failed!")
        return
    
    # Create start scripts
    create_start_scripts()
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Update backend/.env with your configuration")
    print("2. Run the start script:")
    if os.name == 'nt':
        print("   - Windows: double-click start.bat")
    else:
        print("   - Unix/Linux/macOS: ./start.sh")
    print("3. Open http://localhost:3000 in your browser")
    print("\nFor more information, see README.md")

if __name__ == "__main__":
    main()
