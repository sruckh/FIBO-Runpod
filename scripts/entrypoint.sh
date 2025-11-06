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

    # Activate virtual environment and launch Gradio
    source .venv/bin/activate
    echo "🚀 Launching Gradio application..."
    gradio
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

touch /workspace/.fibo_installed

echo "🚀 Launching Gradio application..."
# Launch the gradio command installed by uv sync
gradio
