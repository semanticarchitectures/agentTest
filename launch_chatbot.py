#!/usr/bin/env python3
"""
Chatbot Launcher
Choose between command-line or web interface for the Air Force Doctrine Chatbot.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Check if required packages are installed."""
    required_packages = [
        "llama-index",
        "llama-index-vector-stores-faiss", 
        "llama-index-llms-anthropic",
        "anthropic",
        "streamlit"
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing.append(package)
    
    return missing

def check_environment():
    """Check if environment is properly configured."""
    issues = []
    
    # Check API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        issues.append("ANTHROPIC_API_KEY environment variable not set")
    
    # Check storage directory
    if not Path("./storage").exists():
        issues.append("Vector database storage directory not found (./storage)")
    
    # Check required files
    required_files = ["storage/docstore.json", "storage/default__vector_store.json"]
    for file_path in required_files:
        if not Path(file_path).exists():
            issues.append(f"Required database file not found: {file_path}")
    
    return issues

def install_requirements():
    """Install missing requirements."""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install",
            "llama-index",
            "llama-index-vector-stores-faiss", 
            "llama-index-llms-anthropic",
            "anthropic",
            "streamlit"
        ])
        print("✅ Packages installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install packages: {e}")
        return False

def launch_cli():
    """Launch the command-line interface."""
    print("🚀 Launching command-line chatbot...")
    try:
        subprocess.run([sys.executable, "doctrine_chatbot.py"])
    except KeyboardInterrupt:
        print("\n👋 Chatbot session ended")
    except Exception as e:
        print(f"❌ Error launching CLI chatbot: {e}")

def launch_web():
    """Launch the web interface."""
    print("🌐 Launching web interface...")
    print("📱 Your browser should open automatically")
    print("🔗 If not, go to: http://localhost:8501")
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "web_chatbot.py",
            "--server.headless", "false",
            "--server.port", "8501"
        ])
    except KeyboardInterrupt:
        print("\n👋 Web server stopped")
    except Exception as e:
        print(f"❌ Error launching web interface: {e}")

def main():
    """Main launcher interface."""
    print("🎖️  AIR FORCE DOCTRINE CHATBOT LAUNCHER")
    print("="*50)
    
    # Check requirements
    missing_packages = check_requirements()
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        install = input("📦 Install missing packages? (y/n): ").lower().strip()
        if install == 'y':
            if not install_requirements():
                return
        else:
            print("❌ Cannot proceed without required packages")
            return
    
    # Check environment
    env_issues = check_environment()
    if env_issues:
        print("⚠️  Environment Issues:")
        for issue in env_issues:
            print(f"   • {issue}")
        
        if "ANTHROPIC_API_KEY" in str(env_issues):
            print("\n🔑 To set your API key:")
            print("   export ANTHROPIC_API_KEY='your_key_here'")
        
        if "storage" in str(env_issues):
            print("\n📂 Make sure you're in the directory with your vector database")
            print("   The 'storage' folder should contain your indexed documents")
        
        proceed = input("\n❓ Proceed anyway? (y/n): ").lower().strip()
        if proceed != 'y':
            return
    
    print("\n✅ Environment check complete!")
    
    # Choose interface
    print("\n🚀 Choose your interface:")
    print("1. 💻 Command Line Interface (CLI)")
    print("2. 🌐 Web Interface (Streamlit)")
    print("3. ❌ Exit")
    
    while True:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            launch_cli()
            break
        elif choice == "2":
            launch_web()
            break
        elif choice == "3":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Launcher interrupted by user")
    except Exception as e:
        print(f"❌ Launcher error: {e}")
