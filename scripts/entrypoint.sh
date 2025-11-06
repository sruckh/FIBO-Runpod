#!/bin/bash
set -e

echo "=================================="
echo "FIBO RunPod - Runtime Installer"
echo "=================================="

# Check if already installed (for restarts)
if [ -d "/workspace/FIBO" ] && [ -f "/workspace/.fibo_installed" ]; then
    echo "✅ FIBO already installed, skipping setup..."
    cd /workspace/FIBO

    # Export environment variables for FIBO
    export HF_TOKEN="${HF_TOKEN:-}"
    export GOOGLE_API_KEY="${GOOGLE_API_KEY:-}"

    # Activate virtual environment and launch Gradio app
    source .venv/bin/activate

    # Copy app.py to FIBO directory if not present
    if [ ! -f "app.py" ]; then
        cp /app/app.py .
    fi

    echo "🚀 Launching FIBO Gradio application..."
    python app.py
    exit 0
fi

echo "📦 Installing system dependencies..."
apt-get update -qq
apt-get install -y -qq python3 python3-pip curl git ca-certificates

echo "📦 Installing uv package manager..."
curl -LsSf https://astral.sh/uv/install.sh | sh
# Add uv to PATH (it installs to /root/.local/bin)
export PATH="/root/.local/bin:$PATH"

echo "📦 Cloning FIBO repository..."
# Ensure /workspace exists (RunPod mounts it, but create if needed)
if [ ! -d "/workspace" ]; then
    echo "⚠️  /workspace not found, creating directory..."
    mkdir -p /workspace
fi

cd /workspace
git clone https://github.com/Bria-AI/FIBO.git
cd FIBO

echo "📦 Installing Python dependencies with uv sync..."
uv sync

echo "✅ Installation complete!"

# Export environment variables for FIBO
export HF_TOKEN="${HF_TOKEN:-}"
export GOOGLE_API_KEY="${GOOGLE_API_KEY:-}"

# Activate virtual environment
source .venv/bin/activate

# Authenticate with Hugging Face if token provided
if [ -n "$HF_TOKEN" ]; then
    echo "🔐 Authenticating with Hugging Face..."
    huggingface-cli login --token "$HF_TOKEN" --add-to-git-credential
else
    echo "⚠️  WARNING: HF_TOKEN not set - model download will fail!"
    echo "   Please set HF_TOKEN environment variable in RunPod"
fi

touch /workspace/.fibo_installed

# Copy app.py to FIBO directory
cp /app/app.py .

echo "🚀 Launching FIBO Gradio application..."
# Launch the Gradio app
python app.py
