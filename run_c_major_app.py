#!/usr/bin/env python3
"""
Startup script for the C Major constrained music generation app.
This script checks dependencies and provides instructions for running the application.
"""

import sys
import os
import subprocess

def check_dependencies():
    """Check if required dependencies are installed"""
    
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'numpy',
        'torch', 
        'gradio',
        'transformers',
        'safetensors',
        'peft',
        'tqdm'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - MISSING")
            missing_packages.append(package)
    
    return missing_packages

def check_model_files():
    """Check if model files are available"""
    
    print("\n🔍 Checking for model files...")
    
    # Common model file patterns
    model_patterns = [
        "**/*.ckpt",
        "**/*.bin", 
        "**/*.safetensors"
    ]
    
    import glob
    model_files = []
    for pattern in model_patterns:
        model_files.extend(glob.glob(pattern, recursive=True))
    
    # Filter out adapter files (LoRA)
    model_files = [f for f in model_files if "adapter_model" not in f]
    
    if model_files:
        print(f"  ✅ Found {len(model_files)} model file(s):")
        for f in model_files[:3]:  # Show first 3
            print(f"     {f}")
        if len(model_files) > 3:
            print(f"     ... and {len(model_files) - 3} more")
    else:
        print("  ⚠️  No model files found")
        print("     You'll need to download a model from HuggingFace")
        print("     The app will try to download automatically when you load a model")
    
    return len(model_files) > 0

def show_usage_instructions():
    """Show instructions for using the C major constrained app"""
    
    print("\n" + "="*60)
    print("🎵 C MAJOR MUSIC GENERATION APP")
    print("="*60)
    
    print("\n📋 What's New:")
    print("  • All generated music is automatically constrained to C major")
    print("  • Key signature is forced to C major (no sharps/flats)")
    print("  • Only C major scale notes can be generated (C, D, E, F, G, A, B)")
    print("  • Works with all instruments and settings")
    
    print("\n🚀 How to Run:")
    print("  1. Install dependencies: pip install -r requirements.txt")
    print("  2. Run the app: python app.py")
    print("  3. Open your browser to the displayed URL (usually http://localhost:7860)")
    print("  4. Load a model using the 'Get Models' and 'Load' buttons")
    print("  5. Generate music - it will automatically be in C major!")
    
    print("\n🎼 Usage Tips:")
    print("  • The key signature setting is now ignored (always C major)")
    print("  • Try different instruments - they'll all play in C major")
    print("  • Experiment with different tempos and time signatures")
    print("  • The generated MIDI files will only contain C major scale notes")
    
    print("\n🧪 Testing:")
    print("  • Run 'python test_c_major.py' to verify the constraint works")
    print("  • Run 'python demo_c_major.py' to see a demonstration")
    print("  • Check the generated MIDI files in any music software")

def main():
    """Main function"""
    
    print("🎵 C Major Music Generation - Startup Check")
    print("="*50)
    
    # Check dependencies
    missing_deps = check_dependencies()
    
    # Check model files
    has_models = check_model_files()
    
    # Show results
    print("\n" + "="*50)
    print("📊 SYSTEM STATUS")
    print("="*50)
    
    if missing_deps:
        print("❌ MISSING DEPENDENCIES:")
        for dep in missing_deps:
            print(f"   • {dep}")
        print("\n💡 To install missing dependencies:")
        print("   pip install -r requirements.txt")
        print("   or")
        print(f"   pip install {' '.join(missing_deps)}")
    else:
        print("✅ All dependencies are installed!")
    
    if not has_models:
        print("\n⚠️  NO MODEL FILES FOUND:")
        print("   • The app will download models automatically when needed")
        print("   • Or you can pre-download from: https://huggingface.co/skytnt/midi-model-tv2o-medium")
    else:
        print("\n✅ Model files are available!")
    
    # Show usage instructions
    show_usage_instructions()
    
    # Final recommendation
    print("\n" + "="*60)
    if not missing_deps:
        print("🎯 READY TO GO!")
        print("   Run: python app.py")
        print("   All generated music will be in C major! 🎵")
    else:
        print("🔧 SETUP NEEDED:")
        print("   Install dependencies first, then run: python app.py")
    print("="*60)

if __name__ == "__main__":
    main()
