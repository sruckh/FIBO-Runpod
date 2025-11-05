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
    # Use same detection logic as first install
    if [ -f "app.py" ]; then
        python app.py
    elif command -v fibo &> /dev/null; then
        fibo
    elif [ -f "gradio_app.py" ]; then
        python gradio_app.py
    else
        echo "❌ ERROR: Could not find Gradio app entry point!"
        exit 1
    fi
    exit 0
fi

echo "📦 Installing system dependencies..."
apt-get update -qq
apt-get install -y -qq python3 python3-pip curl git ca-certificates

echo "📦 Installing uv package manager..."
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="/root/.cargo/bin:$PATH"

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

echo "🔍 DEBUG: Listing installed files..."
ls -la
echo ""
echo "🔍 DEBUG: Checking .venv/bin for installed commands..."
source .venv/bin/activate
ls -la .venv/bin/ | grep -E "fibo|gradio|app" || echo "No obvious entry points found"
echo ""
echo "🔍 DEBUG: Checking installed Python packages..."
pip list | grep -i fibo || echo "FIBO package not found"
echo ""

touch /workspace/.fibo_installed

echo "🚀 Launching Gradio application..."
# Try common entry points - adjust based on debug output
if [ -f "app.py" ]; then
    echo "Found app.py, launching..."
    python app.py
elif command -v fibo &> /dev/null; then
    echo "Found 'fibo' command, launching..."
    fibo
elif [ -f "gradio_app.py" ]; then
    echo "Found gradio_app.py, launching..."
    python gradio_app.py
else
    echo "❌ ERROR: Could not find Gradio app entry point!"
    echo "Please check debug output above to determine correct launch command."
    exit 1
fi
