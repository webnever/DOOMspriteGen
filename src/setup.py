# DOOM Sprite Generator - Initial Setup
# This script sets up your development environment

import subprocess
import sys

def install_requirements():
    """Install required packages for our DOOM sprite generator"""
    
    required_packages = [
        "torch",                    # PyTorch for deep learning
        "torchvision",             # Computer vision utilities
        "diffusers",               # Hugging Face diffusion models
        "transformers",            # Text processing
        "accelerate",              # Training acceleration
        "datasets",                # Dataset handling
        "Pillow",                  # Image processing
        "numpy",                   # Numerical operations
        "matplotlib",              # Visualization
        "wandb",                   # Experiment tracking (optional)
    ]
    
    print("Installing required packages...")
    for package in required_packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✓ {package} installed successfully")
        except subprocess.CalledProcessError:
            print(f"✗ Failed to install {package}")
    
    print("\n🎮 Setup complete! Ready to build your DOOM sprite generator.")

def check_gpu():
    """Check if CUDA (GPU) is available for training"""
    try:
        import torch
        if torch.cuda.is_available():
            print(f"🚀 GPU detected: {torch.cuda.get_device_name(0)}")
            print(f"   Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
        else:
            print("⚠️  No GPU detected. Training will be slower on CPU.")
    except ImportError:
        print("PyTorch not installed yet.")

if __name__ == "__main__":
    print("=== DOOM Sprite Generator Setup ===")
    install_requirements()
    check_gpu()