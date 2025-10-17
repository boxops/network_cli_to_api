#!/usr/bin/env python3
"""
Quick setup script for Network API Gateway
"""

import os
import sys
import secrets
import subprocess
from pathlib import Path


def print_header(text):
    """Print formatted header"""
    print(f"\n{'=' * 60}")
    print(f"  {text}")
    print(f"{'=' * 60}\n")


def check_python_version():
    """Check if Python version is 3.8+"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        sys.exit(1)
    print(f"✓ Python version: {sys.version.split()[0]}")


def create_env_file():
    """Create .env file from template"""
    env_example = Path(".env.example")
    env_file = Path(".env")

    if env_file.exists():
        response = input(".env file already exists. Overwrite? (y/N): ")
        if response.lower() != "y":
            print("Skipping .env creation")
            return

    if not env_example.exists():
        print("❌ .env.example not found")
        return

    # Read template
    with open(env_example, "r") as f:
        content = f.read()

    # Generate secret key
    secret_key = secrets.token_urlsafe(32)
    content = content.replace("your-secret-key-here-change-in-production", secret_key)

    # Write .env
    with open(env_file, "w") as f:
        f.write(content)

    print(f"✓ Created .env file with generated SECRET_KEY")


def create_directories():
    """Create necessary directories"""
    dirs = ["data", "session_logs", "logs"]
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
    print(f"✓ Created directories: {', '.join(dirs)}")


def create_virtualenv():
    """Create virtual environment if it doesn't exist"""
    venv_path = Path("venv")

    if venv_path.exists():
        print("✓ Virtual environment already exists")
        return True

    print("\nCreating virtual environment...")
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✓ Virtual environment created successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to create virtual environment")
        return False


def get_venv_python():
    """Get path to virtual environment Python"""
    if os.name == "nt":  # Windows
        return Path("venv/Scripts/python.exe")
    else:  # Unix/Linux/Mac
        return Path("venv/bin/python")


def get_venv_pip():
    """Get path to virtual environment pip"""
    if os.name == "nt":  # Windows
        return Path("venv/Scripts/pip.exe")
    else:  # Unix/Linux/Mac
        return Path("venv/bin/pip")


def install_dependencies():
    """Install Python dependencies in virtual environment"""
    print("\nInstalling dependencies in virtual environment...")

    pip_path = get_venv_pip()

    if not pip_path.exists():
        print("❌ Virtual environment pip not found")
        return False

    try:
        subprocess.run([str(pip_path), "install", "--upgrade", "pip"], check=True)
        subprocess.run([str(pip_path), "install", "-r", "requirements.txt"], check=True)
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False


def run_tests():
    """Run tests to verify installation"""
    print("\nRunning tests...")

    python_path = get_venv_python()

    try:
        subprocess.run([str(python_path), "-m", "pytest", "-v", "--tb=short"], check=True)
        print("✓ All tests passed")
    except subprocess.CalledProcessError:
        print("⚠ Some tests failed (this may be normal if you haven't set up test devices)")
    except FileNotFoundError:
        print("⚠ pytest not found, skipping tests")


def print_next_steps():
    """Print next steps"""
    print_header("Setup Complete!")

    print("Next steps:")
    print("\n1. Review and update .env file:")
    print("   nano .env")

    print("\n2. Activate virtual environment:")
    if os.name == "nt":
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")

    print("\n3. Start the application:")
    print("   ./start.sh")
    print("   # or")
    print("   python -m uvicorn app.main:app --reload")

    print("\n4. Access the API documentation:")
    print("   http://localhost:8080/docs")

    print("\n5. Default admin credentials:")
    print("   Username: admin")
    print("   Password: changeme")
    print("   ⚠ CHANGE THIS IMMEDIATELY!")

    print("\n6. Add your first device:")
    print("   - Login at /docs")
    print("   - Use POST /devices endpoint")
    print("   - Test connection with POST /devices/{id}/test")

    print("\nFor more information:")
    print("   - Developer Guide: DEVELOPER_GUIDE.md")
    print("   - Deployment Guide: DEPLOYMENT.md")
    print("   - API Docs: http://localhost:8080/docs\n")


def main():
    """Main setup function"""
    print_header("Network API Gateway - Setup")

    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    # Run setup steps
    check_python_version()
    create_env_file()
    create_directories()

    # Create virtual environment
    if not create_virtualenv():
        print("\n⚠ Continuing without virtual environment setup")
        print("You may need to create it manually: python3 -m venv venv")
        return

    # Ask about dependencies
    response = input("\nInstall Python dependencies in virtual environment? (Y/n): ")
    if response.lower() != "n":
        if not install_dependencies():
            print("\n⚠ Failed to install dependencies")
            print("You can install them manually:")
            print("  source venv/bin/activate")
            print("  pip install -r requirements.txt")
            return

    # Ask about tests
    response = input("\nRun tests? (y/N): ")
    if response.lower() == "y":
        run_tests()

    print_next_steps()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
        sys.exit(1)
