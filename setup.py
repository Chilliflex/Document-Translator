#!/usr/bin/env python3
"""
Setup script for NLP Document Translator
"""
import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description=""):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}")
    print(f"Running: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout.strip():
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Error: {e.stderr}")
        return False

def setup_project():
    """Main setup function"""
    print("🌍 NLP Document Translator - Setup Script")
    print("=" * 50)
    
    # Create directories
    directories = [
        "src", "static/uploads", "output/translated_documents", 
        "sample_documents"
    ]
    
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"   Created: {dir_path}")
    
    # Create conda environment
    venv_path = "./venv"
    
    success = run_command(
        f"conda create -p {venv_path} python=3.10 -y",
        "Creating conda environment with Python 3.10"
    )
    
    if success:
        # Get pip path
        if os.name == 'nt':  # Windows
            pip_cmd = f"{venv_path}\\Scripts\\pip"
        else:  # Unix/Linux/macOS
            pip_cmd = f"{venv_path}/bin/pip"
        
        run_command(
            f"{pip_cmd} install -r requirements.txt",
            "Installing required packages"
        )
    
    print("\n🎉 Setup completed!")
    print("\nTo start: conda activate ./venv && streamlit run app.py")

if __name__ == "__main__":
    setup_project()