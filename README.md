# 🎨 FIBO RunPod - Text-to-Image Generation

[![Docker Hub](https://img.shields.io/docker/v/gemneye/fibo-runpod?label=Docker%20Hub&logo=docker)](https://hub.docker.com/r/gemneye/fibo-runpod)
[![Docker Pulls](https://img.shields.io/docker/pulls/gemneye/fibo-runpod)](https://hub.docker.com/r/gemneye/fibo-runpod)
[![GitHub](https://img.shields.io/badge/GitHub-sruckh%2FFIBO--Runpod-blue?logo=github)](https://github.com/sruckh/FIBO-Runpod)

**Production-ready Docker container for deploying [FIBO](https://github.com/Bria-AI/FIBO) (8B parameter JSON-native text-to-image AI model) on RunPod GPU cloud platform.**

This container provides a complete Gradio web interface with three generation modes (Generate, Refine, Inspire) for professional-grade, controllable image synthesis using structured JSON prompts.

---

## 📖 Repository Overview

### What This Image Provides

This Docker image is a **minimal runtime container** (~2GB base) that automatically installs FIBO and all dependencies at startup on RunPod's persistent storage. It includes:

- ✅ **Complete Gradio Web Interface** - Three-mode UI (Generate/Refine/Inspire) with all FIBO features
- ✅ **Automatic Installation** - Downloads and configures Python, PyTorch, FIBO, and models on first run
- ✅ **Persistent Caching** - Models and dependencies cached on RunPod volume for fast restarts (<30s)
- ✅ **GPU-Optimized** - CUDA 12.8.0 + cuDNN on Ubuntu 24.04 for maximum performance
- ✅ **Environment-Driven Config** - All settings via environment variables (HF_TOKEN, GOOGLE_API_KEY, etc.)
- ✅ **Gradio Share Links** - Reliable access via public gradio.live URLs (bypasses unreliable RunPod proxy)
- ✅ **Health Monitoring** - Built-in health checks and comprehensive logging

### Quick Deploy to RunPod

**1. Pull Image:**
```bash
docker pull gemneye/fibo-runpod:latest
```

**2. Configure in RunPod:**
- **Image**: `gemneye/fibo-runpod:latest`
- **GPU**: NVIDIA A100 40GB/80GB, H100, or RTX 6000 Ada (48GB+ VRAM required)
- **Volume**: `/workspace` (50GB-100GB persistent storage)
- **Port**: `7860/http` (Gradio interface)
- **Environment Variables**:
  - `HF_TOKEN=hf_xxxxx` (REQUIRED - get from https://huggingface.co/settings/tokens)
  - `GOOGLE_API_KEY=AIzaSyxxxxx` (OPTIONAL - for Gemini VLM, otherwise uses local)
  - `GRADIO_SHARE=true` (RECOMMENDED - creates stable gradio.live link)

**3. Launch & Access:**
- First startup: 5-10 minutes (downloads ~8GB models)
- Check pod logs for: `Running on public URL: https://xxxxx.gradio.live`
- Access Gradio UI via share link or RunPod port 7860
- Subsequent restarts: <30 seconds (cached)

### How to Use

**Generate Mode** 🎨 - Create images from text:
```
Input: "A serene lake at sunset with mountains in the background"
Output: Generated image + Structured JSON prompt
```

**Refine Mode** ✨ - Modify existing images:
```
Input: Source image + "Make the sky more dramatic with clouds"
Output: Refined image + Updated JSON prompt
```

**Inspire Mode** 🔍 - Extract prompts from images:
```
Input: Upload reference image
Output: Structured JSON prompt describing the image
```

### Container Architecture

```
┌─────────────────────────────────┐
│ Minimal Base Image (~2GB)       │
│ - CUDA 12.8.0 + cuDNN          │
│ - Ubuntu 24.04 LTS              │
│ - Entrypoint script only        │
└─────────────────────────────────┘
           ↓ Runtime Installation
┌─────────────────────────────────┐
│ /workspace (RunPod Volume)      │
│ - Python 3.12 + PyTorch 2.8.0+  │
│ - FIBO model + dependencies     │
│ - Cached models (~8GB)          │
│ - Generated images              │
└─────────────────────────────────┘
           ↓ Launch
┌─────────────────────────────────┐
│ Gradio Web Interface            │
│ - Port 7860                     │
│ - Three generation modes        │
│ - Real-time generation          │
└─────────────────────────────────┘
```

### Why This Approach?

- **Faster Pulls**: 2GB base vs 10GB+ bloated images
- **Easy Updates**: Dependencies updated at runtime, not baked into image
- **Cost Efficient**: Less Docker Hub storage, less RunPod bandwidth
- **Flexible**: Test different model/dependency versions without rebuilding
- **Persistent**: RunPod volume caches everything, installation only happens once

---

## 🎨 What is FIBO?

FIBO is Bria AI's 8-billion parameter text-to-image generation model featuring:
- **JSON-Native Control**: Structured prompts for deterministic, reproducible image generation
- **Three Generation Modes**: Generate, Refine, and Inspire workflows
- **High Quality**: Professional-grade image synthesis with precise control
- **Open Source**: Available under Bria AI's non-commercial license

## 🚀 Quick Start

### RunPod Template (Recommended)

This image is available as a pre-configured template on RunPod:

1. Go to RunPod → **Templates** → Search for "FIBO"
2. Click **Deploy** and select a GPU with **48GB+ VRAM**
3. Configure environment variables (add `HF_TOKEN`)
4. Wait 5-10 minutes for first-time model downloads
5. Access via Gradio share link in pod logs

### Docker Hub

```bash
docker pull gemneye/fibo-runpod:latest
```

## 🔧 Configuration

### Required Environment Variables

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `HF_TOKEN` | Hugging Face access token for model downloads | **Yes** | `hf_xxxxxxxxxxxxx` |

**How to get HF_TOKEN:**
1. Create account at [huggingface.co](https://huggingface.co)
2. Go to Settings → Access Tokens → Create new token
3. Grant **Read** permissions
4. Accept FIBO model license at [briaai/FIBO](https://huggingface.co/briaai/FIBO)

### Optional Environment Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `GOOGLE_API_KEY` | Google Gemini API key for faster VLM mode | None | `AIzaSyxxxxx` |
| `GRADIO_SERVER_NAME` | Network interface to bind | `0.0.0.0` | `0.0.0.0` |
| `GRADIO_SERVER_PORT` | Port for Gradio web interface | `7860` | `7860` |
| `GRADIO_SHARE` | Enable gradio.live public link | `true` | `true` or `false` |

**GRADIO_SHARE Note**: RunPod's proxy service can be unreliable. Setting `GRADIO_SHARE=true` (default) creates a stable `https://*.gradio.live` URL for reliable access.

### Exposed Ports

| Port | Protocol | Purpose |
|------|----------|---------|
| `7860` | HTTP | Gradio web interface |

## 📦 Volume Mounts

| Path | Purpose | Recommended Size |
|------|---------|------------------|
| `/workspace` | Persistent storage for models, cache, outputs | 50GB - 100GB |

**Persistence Strategy:**
- Models cached in `/workspace/.cache/huggingface/`
- Virtual environment in `/workspace/FIBO/.venv/`
- Generated images in `/workspace/FIBO/` (named by timestamp)
- Installation marker at `/workspace/.fibo_installed`

## 🎯 Features

### Three Generation Modes

**1. Generate Mode** 🎨
- Input: Text prompt + parameters (seed, steps, aspect ratio, negative prompt, guidance scale)
- Output: Generated image + Structured JSON prompt
- Use case: Create new images from text descriptions

**2. Refine Mode** ✨
- Input: Structured JSON prompt + refinement instructions + seed
- Output: Refined image + Updated JSON prompt
- Use case: Iteratively improve existing generations with precise control

**3. Inspire Mode** 🔍
- Input: Reference image + optional prompt + seed
- Output: Extracted structured JSON prompt
- Use case: Analyze existing images to extract their structured representation

### Supported Parameters

| Parameter | Type | Values/Range | Default |
|-----------|------|--------------|---------|
| VLM Mode | Choice | `gemini`, `local` | `gemini` |
| Seed | Integer | Any integer | Random |
| Steps | Integer | 20-100 | 50 |
| Aspect Ratio | Choice | 1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9 | 1:1 |
| Negative Prompt | Text | Any text | Empty |
| Guidance Scale | Float | 1.0-20.0 | 5.0 |

### Aspect Ratio to Resolution Mapping

| Aspect Ratio | Resolution (WxH) | Use Case |
|--------------|------------------|----------|
| 1:1 | 1024×1024 | Square (social media) |
| 16:9 | 1344×768 | Landscape (widescreen) |
| 9:16 | 768×1344 | Portrait (mobile) |
| 4:3 | 1152×896 | Classic landscape |
| 3:4 | 896×1152 | Classic portrait |
| 4:5 | 896×1088 | Instagram portrait |
| 5:4 | 1088×896 | Instagram landscape |
| 2:3 | 832×1248 | Tall portrait |
| 3:2 | 1248×832 | Wide landscape |

## 🖥️ System Requirements

### ⚠️ Critical Requirement: 48GB GPU VRAM

**FIBO requires a GPU with at least 48GB of VRAM for inference.**

### Recommended GPUs

| GPU Model | VRAM | Status | Notes |
|-----------|------|--------|-------|
| NVIDIA A100 80GB | 80GB | ✅ **Optimal** | Best performance, future-proof |
| NVIDIA A100 40GB | 40GB | ⚠️ **May work** | Not officially tested - close to minimum |
| NVIDIA H100 | 80GB | ✅ **Optimal** | Fastest performance |
| RTX 6000 Ada | 48GB | ✅ **Minimum** | Meets minimum requirement |
| RTX A6000 | 48GB | ✅ **Minimum** | Meets minimum requirement |
| RTX 4090 | 24GB | ❌ **Insufficient** | Not enough VRAM |
| RTX 4080 | 16GB | ❌ **Insufficient** | Not enough VRAM |
| RTX 3090 | 24GB | ❌ **Insufficient** | Not enough VRAM |

### System Requirements

**Minimum:**
- **GPU**: NVIDIA GPU with 48GB VRAM (RTX 6000 Ada / RTX A6000)
- **RAM**: 32GB system RAM
- **Storage**: 30GB container + 50GB volume
- **CUDA**: 12.8.0+

**Recommended:**
- **GPU**: NVIDIA A100 80GB
- **RAM**: 64GB system RAM
- **Storage**: 30GB container + 100GB volume

**Optimal:**
- **GPU**: NVIDIA H100 or A100 80GB
- **RAM**: 128GB system RAM
- **Storage**: 30GB container + 200GB volume

## ⏱️ Performance & Timing

| Metric | First Run | Subsequent Runs |
|--------|-----------|-----------------|
| **Cold Start** | 5-10 minutes | <30 seconds |
| **Model Download** | ~8GB (included in cold start) | Cached |
| **Generate Mode** | 30-120 seconds | 30-120 seconds |
| **Refine Mode** | 20-90 seconds | 20-90 seconds |
| **Inspire Mode** | 40-150 seconds | 40-150 seconds |

**Note**: First generation includes model loading time. Subsequent generations are faster.

## 🔐 Security & Authentication

### Hugging Face Authentication

The container automatically authenticates with Hugging Face using your `HF_TOKEN`:

```bash
hf auth login --token $HF_TOKEN --add-to-git-credential
```

**Gated Model Access**: FIBO is a gated model. You must:
1. Create Hugging Face account
2. Accept model license at https://huggingface.co/briaai/FIBO
3. Generate access token with **Read** permissions

### No Hardcoded Secrets

- All credentials passed via environment variables
- No secrets committed to Docker image
- Tokens stored in `/root/.cache/huggingface/` (inside container only)

## 📚 Usage Examples

### RunPod Deployment

**Via Template:**
1. RunPod Dashboard → Templates → "FIBO"
2. **Select GPU with 48GB+ VRAM** (A100 40GB/80GB, RTX 6000 Ada, RTX A6000)
3. Configure environment variables (add `HF_TOKEN`)
4. Deploy → Wait for cold start
5. Check logs for Gradio share link

**Via Manual Pod:**
```yaml
Image: gemneye/fibo-runpod:latest
GPU: A100 40GB or better (48GB+ VRAM required)
Volume: /workspace (50GB+)
Ports: 7860/http
Environment Variables:
  HF_TOKEN: hf_xxxxxxxxxxxxx
  GOOGLE_API_KEY: AIzaSyxxxxx (optional)
  GRADIO_SHARE: true
```

### Docker Run (Local/Remote)

**Prerequisites**: NVIDIA GPU with 48GB+ VRAM

```bash
docker run -d \
  --gpus all \
  -p 7860:7860 \
  -v $(pwd)/workspace:/workspace \
  -e HF_TOKEN=hf_xxxxxxxxxxxxx \
  -e GOOGLE_API_KEY=AIzaSyxxxxx \
  -e GRADIO_SHARE=true \
  gemneye/fibo-runpod:latest
```

### Docker Compose

```yaml
version: '3.8'

services:
  fibo:
    image: gemneye/fibo-runpod:latest
    ports:
      - "7860:7860"
    volumes:
      - ./workspace:/workspace
    environment:
      HF_TOKEN: hf_xxxxxxxxxxxxx
      GOOGLE_API_KEY: AIzaSyxxxxx
      GRADIO_SHARE: "true"
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

## 🔍 Accessing the Interface

### Primary Method: Gradio Share Link

Check pod logs for the public share link:

```
🚀 Launching FIBO Gradio application...
Running on local URL:  http://0.0.0.0:7860
Running on public URL: https://abc123xyz.gradio.live
```

Use the **`https://*.gradio.live`** URL for reliable access.

### Fallback: RunPod Proxy

If `GRADIO_SHARE=false`, access via RunPod's port 7860 proxy:
- RunPod Dashboard → Pod → Connect → Port 7860

**Note**: RunPod proxy can be unreliable. Share link is recommended.

## 🐛 Troubleshooting

### Common Issues

**Issue**: Insufficient GPU memory / CUDA out of memory
```bash
# Solution: Use GPU with 48GB+ VRAM
# Minimum supported: RTX 6000 Ada, RTX A6000, A100 40GB
# Recommended: A100 80GB, H100
# The model requires 48GB VRAM - smaller GPUs will not work
```

**Issue**: Container exits immediately
```bash
# Solution: Check HF_TOKEN is set correctly
docker logs <container_id>
# Look for: "⚠️ WARNING: HF_TOKEN not set"
```

**Issue**: Model download fails
```bash
# Solution: Verify token permissions and model license acceptance
# 1. Check token at https://huggingface.co/settings/tokens
# 2. Accept license at https://huggingface.co/briaai/FIBO
```

**Issue**: Gradio UI not accessible via RunPod proxy
```bash
# Solution: Use Gradio share link instead
# 1. Check pod logs for https://*.gradio.live URL
# 2. Ensure GRADIO_SHARE=true in environment variables
```

**Issue**: Generation takes too long (>5 minutes)
```bash
# This triggers timeout - check:
# 1. GPU is properly detected: nvidia-smi
# 2. GPU has 48GB+ VRAM: nvidia-smi --query-gpu=memory.total --format=csv
# 3. CUDA version compatible: 12.8.0+
# 4. Reduce steps parameter (try 30 instead of 50)
```

### Health Check

```bash
# Check if service is running
curl http://localhost:7860/

# Check GPU availability and VRAM
docker exec <container_id> nvidia-smi

# Verify GPU has sufficient memory
docker exec <container_id> nvidia-smi --query-gpu=memory.total --format=csv
# Should show: 48GB or more

# Check Python version
docker exec <container_id> python3 --version
# Should output: Python 3.12.x

# Check HF authentication
docker exec <container_id> hf whoami
```

## 🏗️ Architecture

### Technology Stack

- **Base Image**: `nvidia/cuda:12.8.0-cudnn-runtime-ubuntu24.04`
- **CUDA**: 12.8.0 with cuDNN
- **Python**: 3.12
- **Package Manager**: uv (fast Python package installer)
- **Web Framework**: Gradio 5.x
- **ML Framework**: PyTorch 2.8.0+

### Container Strategy

**Minimal Runtime Installation**:
- Small base image (~2GB)
- Dependencies installed at runtime
- Cached in persistent volume
- Fast restarts (<30s) after initial setup

### Directory Structure

```
/workspace/                         # Persistent volume (RunPod mount)
├── .fibo_installed                # Installation marker
├── .cache/                        # Cached downloads
│   ├── huggingface/              # Model weights
│   │   └── hub/
│   │       └── models--briaai--FIBO/
│   └── pip/                      # Python packages
├── FIBO/                          # Cloned repository
│   ├── .venv/                    # Virtual environment
│   ├── app.py                    # Gradio interface (copied from image)
│   ├── generate.py               # FIBO generation script
│   └── pyproject.toml            # Dependencies
└── outputs/                       # Generated images (optional)
```

## 📝 License

**FIBO Model**: Non-commercial use only. See [Bria AI FIBO License](https://huggingface.co/briaai/FIBO)

**Container Code**: This Docker container implementation is provided as-is for use with the FIBO model.

## 🔗 Links

- **Docker Hub**: https://hub.docker.com/r/gemneye/fibo-runpod
- **GitHub Repository**: https://github.com/sruckh/FIBO-Runpod
- **FIBO Model**: https://huggingface.co/briaai/FIBO
- **FIBO Source**: https://github.com/Bria-AI/FIBO
- **Bria Platform**: https://platform.bria.ai/labs/fibo
- **RunPod**: https://runpod.io

## 🤝 Support

For issues with:
- **This Docker image**: [GitHub Issues](https://github.com/sruckh/FIBO-Runpod/issues)
- **FIBO model**: [FIBO GitHub](https://github.com/Bria-AI/FIBO/issues)
- **RunPod platform**: [RunPod Support](https://runpod.io/support)

## 🎯 Version History

**v1.1.0** (Current)
- CUDA 12.8.0 + cuDNN
- Python 3.12
- Ubuntu 24.04 LTS
- Complete Gradio interface (Generate/Refine/Inspire)
- HF authentication with `hf auth login`
- All 9 aspect ratios supported
- Gradio share link enabled by default

**v1.0.0** (Initial)
- CUDA 12.4.0
- Python 3.10
- Ubuntu 22.04
- Basic functionality

---

**⚠️ IMPORTANT**: Requires GPU with 48GB+ VRAM | **Available as RunPod Template** | **Built with ❤️ for the AI community**
