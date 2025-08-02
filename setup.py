#!/usr/bin/env python3
"""
Setup Script for AI Agent vs Agentic AI Comparison Project
==========================================================

This script helps users set up the environment and run the demonstrations.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        sys.exit(1)

def check_api_keys():
    """Check if API keys are configured"""
    print("\n🔑 Checking API key configuration...")
    
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not openai_key and not anthropic_key:
        print("⚠️  No API keys found. The demo will run with mock responses.")
        print("   To use real LLM capabilities, set one of these environment variables:")
        print("   export OPENAI_API_KEY='your-openai-api-key'")
        print("   export ANTHROPIC_API_KEY='your-anthropic-api-key'")
    else:
        if openai_key:
            print("✅ OpenAI API key found")
        if anthropic_key:
            print("✅ Anthropic API key found")

def create_env_file():
    """Create a sample .env file"""
    env_file = Path(".env")
    if not env_file.exists():
        print("\n📄 Creating sample .env file...")
        with open(env_file, "w") as f:
            f.write("# AI Agent vs Agentic AI Environment Configuration\n")
            f.write("# Uncomment and add your API keys\n\n")
            f.write("# OPENAI_API_KEY=your-openai-api-key-here\n")
            f.write("# ANTHROPIC_API_KEY=your-anthropic-api-key-here\n")
        print("✅ Sample .env file created")

def run_demo_menu():
    """Interactive menu to run demos"""
    print("\n" + "="*60)
    print("🚀 AI AGENT VS AGENTIC AI DEMO MENU")
    print("="*60)
    
    options = [
        ("1", "Run Traditional AI Agent Demo", "python ai_agent.py"),
        ("2", "Run Agentic AI System Demo", "python agentic_ai.py"),
        ("3", "Run Comprehensive Comparison", "python comparison_demo.py"),
        ("4", "View Project Structure", None),
        ("5", "Exit", None)
    ]
    
    while True:
        print("\nSelect an option:")
        for option, description, _ in options:
            print(f"  {option}. {description}")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            print("\n🤖 Running Traditional AI Agent Demo...")
            run_command("python ai_agent.py")
        elif choice == "2":
            print("\n🧠 Running Agentic AI System Demo...")
            run_command("python agentic_ai.py")
        elif choice == "3":
            print("\n📊 Running Comprehensive Comparison...")
            run_command("python comparison_demo.py")
        elif choice == "4":
            show_project_structure()
        elif choice == "5":
            print("\n👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")

def run_command(command):
    """Run a command and handle errors"""
    try:
        subprocess.run(command.split(), check=True)
        print("✅ Demo completed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Demo failed with error: {e}")
    except KeyboardInterrupt:
        print("\n⏹️  Demo interrupted by user")

def show_project_structure():
    """Show the project structure"""
    print("\n📁 Project Structure:")
    print("├── ai_agent.py              # Traditional AI Agent implementation")
    print("├── agentic_ai.py            # Agentic AI System implementation")
    print("├── comparison_demo.py       # Comprehensive comparison demo")
    print("├── requirements.txt         # Python dependencies")
    print("├── setup.py                 # This setup script")
    print("├── README.md                # Comprehensive documentation")
    print("└── .env                     # Environment configuration (created)")
    
    print("\n📚 Key Files:")
    print("• ai_agent.py: Rule-based traditional AI agent")
    print("• agentic_ai.py: Autonomous agentic AI system")
    print("• comparison_demo.py: Side-by-side comparison")
    print("• README.md: Complete documentation and guide")

def main():
    """Main setup function"""
    print("🔧 AI Agent vs Agentic AI - Setup Script")
    print("="*50)
    
    # Check Python version
    check_python_version()
    
    # Install dependencies
    install_dependencies()
    
    # Create sample .env file
    create_env_file()
    
    # Check API keys
    check_api_keys()
    
    print("\n✅ Setup completed successfully!")
    
    # Run demo menu
    run_demo_menu()

if __name__ == "__main__":
    main()