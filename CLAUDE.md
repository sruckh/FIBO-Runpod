# CLAUDE.md - FIBO RunPod Deployment Project

This file provides guidance to Claude Code when working with the FIBO text-to-image AI model project, specifically for containerization and deployment to RunPod platform.

## 🎯 Project Overview

**FIBO** is an 8B-parameter, JSON-native text-to-image AI model that will be containerized for deployment on the RunPod platform. This is NOT a localhost development project - all dependencies and modules will be downloaded and installed at runtime on the RunPod host.

### Core Requirements
- **Platform**: RunPod GPU Pod Template (NOT serverless)
- **Entry Point**: Gradio web application
- **Architecture**: Minimal container with runtime installation
- **Distribution**: Docker Hub registry (`gemneye/fibo-runpod`)
- **GPU**: NVIDIA GPU required for inference
- **No Local Dependencies**: Zero installation on local machine
- **Build Environment**: GitHub Actions ONLY (no local Docker builds)
- **Development Host**: Minimal VPS - code editing only, no containerization

### Repository Information
- **GitHub Repository**: `sruckh/FIBO-Runpod` (SSH access configured)
- **Docker Hub**: `gemneye/fibo-runpod`
- **CI/CD**: GitHub Actions for automated builds
- **Secrets**: `DOCKER_USERNAME` and `DOCKER_PASSWORD` configured in repository secrets
- **Security**: No private information or secrets committed to repository

## ⚠️ CRITICAL: Development Environment Constraints

**This is a MINIMAL VPS host for CODE EDITING ONLY**

### What This VPS Can Do:
- ✅ Edit code files (Dockerfile, Python, bash scripts)
- ✅ Git operations (commit, push, pull)
- ✅ Syntax validation (bash -n, python -m py_compile)
- ✅ Text editing and file management
- ✅ Run validation scripts

### What This VPS CANNOT Do:
- ❌ Build Docker images
- ❌ Run Docker containers
- ❌ Test containerized applications
- ❌ Install Docker or container runtimes
- ❌ Pull or push Docker images directly

### Build & Test Strategy:
```
VPS (Code Editing) → GitHub (CI/CD) → Docker Hub (Storage) → RunPod (Testing)
```

**All containerization happens on GitHub Actions runners, NOT on this VPS.**

---

## 🏗️ Architecture Design

### Container Strategy
```yaml
approach: "minimal_base_with_runtime_installation"
philosophy: "ship_configuration_not_dependencies"
benefits:
  - Smaller image size for faster pulls
  - Runtime flexibility for updates
  - Reduced Docker Hub storage costs
  - Easy version management
```

### Three-Layer Architecture
```
Layer 1: Base Image (CUDA + Python)
  ├─> NVIDIA CUDA runtime base
  ├─> Python 3.10+
  └─> Minimal system utilities

Layer 2: Runtime Installation Script
  ├─> uv package manager installation
  ├─> Hugging Face CLI setup
  ├─> Project dependencies (from pyproject.toml)
  └─> Model weight downloads (lazy loading)

Layer 3: Application Entry Point
  ├─> Gradio web interface
  ├─> FIBO model initialization
  └─> Health check endpoints
```

## 📋 Implementation Plan

### Phase 1: Container Foundation (Week 1)

#### 1.1 Base Image Selection
**Decision Criteria**:
- CUDA compatibility: 12.8.1 (latest stable)
- PyTorch version: 2.8.0+ (latest)
- Python version: 3.10+ (3.11 or 3.12 preferred)
- Base size: Optimized for RunPod infrastructure
- RunPod compatibility: `linux/amd64` platform

**Recommended Base Images** (in priority order):
```dockerfile
# Option 1: RunPod's latest PyTorch base (RECOMMENDED)
FROM runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404

# Option 2: Alternative RunPod PyTorch base
FROM runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04

# Option 3: NVIDIA CUDA official (if RunPod images unavailable)
FROM nvidia/cuda:12.8.1-cudnn9-devel-ubuntu24.04
```

**Rationale**:
- **Latest CUDA 12.8.1**: Best performance and compatibility with modern GPUs (RTX 4090, H100, A100, etc.)
- **PyTorch 2.8.0**: Latest stable release with performance improvements, better memory efficiency, and bug fixes
- **Ubuntu 24.04**: LTS release with updated system libraries and better security patches
- **RunPod optimized**: Pre-configured for RunPod infrastructure, includes common ML dependencies
- **Reduced installation time**: Newer base = fewer dependencies to install at runtime
- **Better GPU utilization**: CUDA 12.8.1 has improved scheduling and memory management
- **Future-proof**: Compatible with upcoming GPU architectures (Blackwell, etc.)

**Key Benefits for FIBO**:
- CUDA 12.8.1 provides ~10-15% performance improvement over CUDA 11.8 for transformer models
- PyTorch 2.8.0 includes native support for newer attention mechanisms used in DiT architectures
- Better VRAM management allows for larger batch sizes or higher resolution generations
- Ubuntu 24.04 includes updated Python system libraries that may be required by newer dependencies

#### 1.2 Dockerfile Structure Design
```dockerfile
# Multi-stage build pattern (if needed for optimization)
# Stage 1: Builder (for any compilation needs)
# Stage 2: Runtime (minimal production image)

# Key sections:
# - Base image declaration
# - System dependencies (curl, git, etc.)
# - Working directory setup
# - File copying (only essential files)
# - Entrypoint script setup
# - Port exposure (7860 for Gradio)
# - Health check configuration
```

**Files to Copy into Container**:
```
COPY scripts/runtime_setup.sh /app/scripts/
COPY scripts/entrypoint.sh /app/scripts/
# DO NOT COPY: .venv/, models/, __pycache__/, pyproject.toml, uv.lock, generate.py, app.py, examples/
```

#### 1.3 Runtime Installation Strategy

**Installation Script Design** (`scripts/runtime_setup.sh`):
```bash
#!/bin/bash
# Purpose: Install all dependencies at container startup
# Execution time: 5-10 minutes (first run only)
# Persistence: Uses RunPod volume mount for caching

STEPS:
1. Check if already installed (idempotency)
2. Clone the FIBO-Runpod repository
3. Install uv package manager
4. Authenticate with Hugging Face (if HF_TOKEN provided)
5. Run uv sync to install dependencies
6. Download model weights (lazy loading)
7. Verify installations
8. Set up Python environment
```

**Caching Strategy**:
- Use RunPod's persistent volume mount at `/workspace`
- Cache location: `/workspace/.cache/`
- Structure:
  ```
  /workspace/
  ├── .cache/
  │   ├── huggingface/  (model weights)
  │   ├── pip/          (Python packages)
  │   └── uv/           (uv cache)
  ├── .venv/            (virtual environment)
  └── outputs/          (generated images)
  ```

### Phase 2: Gradio Application Development (Week 2)

#### 2.1 Gradio Interface Design

**Three Mode Interface** (matching FIBO capabilities):
```python
# Tab 1: Generate Mode
inputs:
  - prompt: gr.Textbox (long text support)
  - model_mode: gr.Radio (["gemini", "local"])
  - seed: gr.Number
  - advanced_options: gr.Accordion (guidance_scale, steps, etc.)
outputs:
  - generated_image: gr.Image
  - structured_prompt: gr.JSON (expandable)

# Tab 2: Refine Mode
inputs:
  - structured_prompt: gr.JSON (from previous generation)
  - refinement_instruction: gr.Textbox
  - seed: gr.Number
outputs:
  - refined_image: gr.Image
  - updated_prompt: gr.JSON

# Tab 3: Inspire Mode
inputs:
  - source_image: gr.Image (upload)
  - creative_instruction: gr.Textbox (optional)
  - seed: gr.Number
outputs:
  - inspired_image: gr.Image
  - extracted_prompt: gr.JSON
```

**UI Requirements**:
- Dark mode by default (easier on eyes)
- Responsive layout (mobile-friendly)
- Progress indicators for long operations
- Error messages with helpful context
- Download buttons for outputs (images + JSON prompts)
- Gallery view for generation history

#### 2.2 Application Entry Point

**File**: `app.py` (new file to create)
```python
# Key components:
# 1. Environment variable handling (including GRADIO_SHARE)
# 2. Model initialization (lazy loading)
# 3. Gradio interface construction with share parameter
# 4. Exception handling and logging
# 5. Health check endpoint
# 6. Graceful shutdown handling

# Gradio launch example:
# share_enabled = os.environ.get("GRADIO_SHARE", "true").lower() == "true"
# app.launch(
#     server_name=os.environ.get("GRADIO_SERVER_NAME", "0.0.0.0"),
#     server_port=int(os.environ.get("GRADIO_SERVER_PORT", "7860")),
#     share=share_enabled  # Creates gradio.live tunnel when True
# )
```

**Environment Variables** (Configured via RunPod Platform Interface):
```bash
# ============================================
# REQUIRED - Set via RunPod Template/Pod Config
# ============================================
HF_TOKEN=<hugging_face_token>
# Purpose: Authenticate with Hugging Face to download FIBO model
# Where: Set in RunPod template "Environment Variables" section
# Obtain: https://huggingface.co/settings/tokens
# Required permissions: Read access to briaai/FIBO

# ============================================
# OPTIONAL - Set via RunPod Template/Pod Config
# ============================================
GOOGLE_API_KEY=<gemini_api_key>
# Purpose: Enable Gemini VLM for prompt expansion (alternative to local VLM)
# Where: Set in RunPod template "Environment Variables" section
# Obtain: https://aistudio.google.com/app/apikey
# Default: Uses local FIBO-VLM if not provided

# ============================================
# OPTIONAL - Application Configuration
# ============================================
GRADIO_SERVER_PORT=7860
# Purpose: Port for Gradio web interface
# Default: 7860 (set in Dockerfile, rarely needs override)

GRADIO_SERVER_NAME=0.0.0.0
# Purpose: Network interface to bind
# Default: 0.0.0.0 (set in Dockerfile, do not change)

GRADIO_SHARE=true
# Purpose: Enable Gradio share link (gradio.live tunnel)
# Where: Can be set in RunPod environment variables
# Default: true (recommended - RunPod proxy can be unreliable)
# Note: Creates public https://*.gradio.live URL for reliable access

MAX_WORKERS=2
# Purpose: Maximum concurrent image generation requests
# Where: Can be set in RunPod environment variables for tuning
# Default: 2 (adjust based on GPU VRAM)

LOG_LEVEL=INFO
# Purpose: Application logging verbosity
# Where: Can be set in RunPod environment variables
# Options: DEBUG, INFO, WARNING, ERROR
# Default: INFO
```

**Important Notes**:
- **Do NOT hardcode secrets** in Dockerfile or scripts
- **All sensitive values** (HF_TOKEN, GOOGLE_API_KEY) are passed via RunPod's environment variable interface
- **Users configure** these values when launching the pod through RunPod's web UI
- **Application reads** from `os.environ.get()` at runtime
- **Validation** should occur at startup with clear error messages if required vars are missing

#### 2.3 Error Handling Strategy

**Critical Error Scenarios**:
1. **Model Loading Failure**
   - Cause: Invalid HF_TOKEN or network issues
   - Handling: Retry with exponential backoff, clear error message in UI

2. **GPU Out of Memory**
   - Cause: Large batch or insufficient VRAM
   - Handling: Automatic batch size reduction, suggest lower resolution

3. **VLM API Failures**
   - Cause: Gemini API rate limits or invalid key
   - Handling: Fallback to local VLM, queue retry

4. **Generation Timeouts**
   - Cause: Complex prompts or high step counts
   - Handling: Progress updates, allow cancellation

### Phase 3: RunPod Integration (Week 3)

#### 3.1 Container Configuration

**RunPod Template Specification**:
```json
{
  "category": "NVIDIA",
  "name": "FIBO Text-to-Image",
  "imageName": "yourdockerhub/fibo-runpod:latest",
  "containerDiskInGb": 30,
  "volumeInGb": 50,
  "volumeMountPath": "/workspace",
  "ports": ["7860/http"],
  "env": [
    {
      "key": "HF_TOKEN",
      "value": ""
    },
    {
      "key": "GOOGLE_API_KEY",
      "value": ""
    },
    {
      "key": "GRADIO_SERVER_PORT",
      "value": "7860"
    },
    {
      "key": "GRADIO_SERVER_NAME",
      "value": "0.0.0.0"
    },
    {
      "key": "GRADIO_SHARE",
      "value": "true"
    },
    {
      "key": "MAX_WORKERS",
      "value": "2"
    },
    {
      "key": "LOG_LEVEL",
      "value": "INFO"
    }
  ],
  "readme": "# FIBO Text-to-Image\n\nJSON-native controllable image generation with 8B parameters.\n\n## Required Environment Variables\n\n- **HF_TOKEN**: Your Hugging Face token (get from https://huggingface.co/settings/tokens)\n- **GOOGLE_API_KEY**: (Optional) Google Gemini API key for enhanced VLM mode\n\n## How to Use\n\n1. Set your HF_TOKEN in the environment variables before launching\n2. Launch the pod (GPU with 12GB+ VRAM recommended)\n3. Wait 5-10 minutes for first-time setup (models download to /workspace)\n4. Check logs for the Gradio share link (https://*.gradio.live)\n5. Access UI via:\n   - **Gradio Share Link** (recommended - more reliable)\n   - RunPod exposed port 7860 (if proxy is working)\n6. Start generating images with Generate/Refine/Inspire modes!\n\n## Access Options\n\n**Primary**: Look for the Gradio share link in the pod logs:\n```\nRunning on public URL: https://abc123xyz.gradio.live\n```\n\n**Fallback**: Use RunPod's port 7860 proxy if share link disabled.\n\n## Note on Access\n\nBy default, GRADIO_SHARE=true creates a public gradio.live link for reliable access. RunPod's proxy service can be unreliable. If you need private-only access, set GRADIO_SHARE=false in environment variables.\n\nSee full documentation: [link to docs]"
}
```

**Environment Variable Configuration Flow**:
```
User launches pod via RunPod UI
       ↓
Fills in environment variables (HF_TOKEN, etc.)
       ↓
RunPod injects these as environment variables into container
       ↓
Container starts → entrypoint.sh reads from environment
       ↓
app.py uses os.environ.get() to access values
       ↓
Application validates and uses secrets securely
```
```

**Resource Requirements**:
```yaml
minimum:
  gpu: "RTX 3060 (12GB VRAM)"
  ram: "16GB"
  disk: "30GB container + 50GB volume"

recommended:
  gpu: "RTX 4090 (24GB VRAM)"
  ram: "32GB"
  disk: "30GB container + 100GB volume"

optimal:
  gpu: "A100 (40GB/80GB VRAM)"
  ram: "64GB"
  disk: "30GB container + 200GB volume"
```

#### 3.2 Entrypoint Script Design

**File**: `scripts/entrypoint.sh`
```bash
#!/bin/bash
set -e

# Execution flow:
1. Print banner with version info
2. Check GPU availability (nvidia-smi)
3. Run runtime setup script (if needed)
4. Activate Python virtual environment
5. Verify model access
6. Start Gradio application
7. Tail logs for RunPod console visibility

# Key features:
- Idempotent (safe to restart)
- Verbose logging for debugging
- Health check support
- Graceful error messages
```

#### 3.3 Health Check Implementation

**Purpose**: Allow RunPod to verify container readiness

**Implementation**:
```python
# In app.py:
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "gpu_available": torch.cuda.is_available(),
        "vram_used_gb": torch.cuda.memory_allocated() / 1e9
    }
```

**Dockerfile Health Check**:
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
  CMD curl -f http://localhost:7860/health || exit 1
```

### Phase 4: Build & Deployment Pipeline (Week 4)

#### 4.1 GitHub Actions CI/CD Workflow

**Repository**: `sruckh/FIBO-Runpod`
**Docker Hub**: `gemneye/fibo-runpod`
**Secrets Configured**: `DOCKER_USERNAME`, `DOCKER_PASSWORD`

**Workflow File**: `.github/workflows/docker-build.yml`

**Purpose**: Automated Docker image building and deployment to Docker Hub on:
- Push to `main` branch
- Push of version tags (e.g., `v1.0.0`)
- Manual workflow dispatch

**Workflow Design**:
```yaml
name: Build and Push Docker Image

on:
  push:
    branches:
      - main
    tags:
      - 'v*.*.*'
  workflow_dispatch:
    inputs:
      tag:
        description: 'Optional custom tag'
        required: false
        default: 'latest'

jobs:
  build-and-push:
    runs-on: ubuntu-latest

    steps:
      1. Checkout repository code
      2. Set up Docker Buildx (for multi-platform builds)
      3. Login to Docker Hub (using secrets)
      4. Extract metadata (tags, labels)
      5. Build and push Docker image (linux/amd64)
      6. Generate build summary
      7. Optional: Create GitHub release notes
      8. Optional: Update RunPod template via API

env:
  REGISTRY: docker.io
  IMAGE_NAME: gemneye/fibo-runpod
  PLATFORMS: linux/amd64
```

**Tagging Strategy**:
```yaml
# Automatic tagging based on git events:
- main branch push → gemneye/fibo-runpod:latest
- v1.2.3 tag push → gemneye/fibo-runpod:v1.2.3 + gemneye/fibo-runpod:latest
- Manual dispatch → gemneye/fibo-runpod:{custom-tag}

# Additional automatic tags:
- Branch name (for feature branches)
- Git SHA (for traceability)
- Build date (for audit trail)
```

**Security Considerations**:
```yaml
security:
  secrets_handling:
    - DOCKER_USERNAME: Stored in GitHub repository secrets
    - DOCKER_PASSWORD: Stored in GitHub repository secrets
    - Never echo secrets in logs
    - Use GitHub's secret masking

  code_scanning:
    - Run Dockerfile linting (hadolint)
    - Scan for secrets in code (trufflehog/gitleaks)
    - Container vulnerability scanning (Trivy)

  no_private_data:
    - Never commit HF_TOKEN
    - Never commit GOOGLE_API_KEY
    - Never commit personal information
    - .gitignore includes: .env, secrets/, *.key, *.pem
```

#### 4.2 Development Workflow (Code Only - No Local Builds)

**⚠️ CRITICAL**: This VPS host is minimal and **DOES NOT** build Docker images locally. All builds happen automatically via GitHub Actions.

**Development Workflow**:
```bash
# 1. Edit code on VPS (Dockerfile, scripts, etc.)
# 2. Test code syntax/logic (Python, bash validation)
# 3. Commit changes to git
git add .
git commit -m "Description of changes"

# 4. Push to GitHub - triggers automatic build
git push origin main
# → GitHub Actions builds and pushes to gemneye/fibo-runpod:latest

# For versioned releases
git tag v1.0.0
git push origin v1.0.0
# → GitHub Actions builds and pushes versioned tags
```

**What Happens on Git Push**:
```
Local VPS (code editing)
       ↓
   Git Push
       ↓
GitHub Repository (sruckh/FIBO-Runpod)
       ↓
GitHub Actions (automated build)
       ↓
Docker Hub (gemneye/fibo-runpod)
       ↓
RunPod (deployment)
```

**No Local Docker Required**:
- ❌ No `docker build` commands on VPS
- ❌ No `docker push` commands on VPS
- ❌ No Docker installation needed on VPS
- ✅ Only git, text editors, and basic shell tools
- ✅ All containerization handled by GitHub Actions

#### 4.3 Testing Strategy

**⚠️ No Local Container Testing**: Cannot test Docker containers on this minimal VPS.

**Code Validation** (on VPS before git push):

**Script**: `scripts/validate.sh` (to be created)
```bash
#!/bin/bash
# Purpose: Validate code before git push (no Docker required)

set -e

echo "🔍 Validating FIBO RunPod code..."

# 1. Validate shell scripts
echo "Checking bash syntax..."
bash -n scripts/entrypoint.sh
bash -n scripts/runtime_setup.sh
echo "✅ Bash scripts valid"

# 2. Validate Python syntax
echo "Checking Python syntax..."
if command -v python3 &> /dev/null; then
    python3 -m py_compile app.py 2>/dev/null || echo "⚠️  app.py not found (may not be created yet)"
fi
echo "✅ Python syntax valid"

# 3. Check for hardcoded secrets
echo "Checking for hardcoded secrets..."
SECRET_CHECK=$(grep -r "hf_" . --exclude-dir=.git --exclude-dir=.venv || true)
if [ -n "$SECRET_CHECK" ]; then
    echo "❌ Found potential HuggingFace tokens in code!"
    echo "$SECRET_CHECK"
    exit 1
fi

SECRET_CHECK=$(grep -r "AIzaSy" . --exclude-dir=.git --exclude-dir=.venv || true)
if [ -n "$SECRET_CHECK" ]; then
    echo "❌ Found potential Google API keys in code!"
    echo "$SECRET_CHECK"
    exit 1
fi
echo "✅ No hardcoded secrets found"

# 4. Validate Dockerfile exists
if [ ! -f "Dockerfile" ]; then
    echo "⚠️  Dockerfile not found"
else
    echo "✅ Dockerfile exists"
fi

echo ""
echo "✅ All validation checks passed!"
echo "Safe to commit and push to GitHub."
```

**Usage**:
```bash
# Before committing changes
./scripts/validate.sh

# If validation passes, commit and push
git add .
git commit -m "Your commit message"
git push origin main
```

**Testing Flow**:
```
1. Code validation on VPS
       ↓
2. Push to GitHub
       ↓
3. GitHub Actions builds (first test)
       ↓
4. If build succeeds → Deploy to RunPod
       ↓
5. RunPod Testing (real environment)
```

**RunPod Testing** (Primary Testing Environment):
```yaml
test_checklist:
  - [ ] Container pulls successfully
  - [ ] Environment variables are set
  - [ ] Runtime installation completes
  - [ ] Models download correctly
  - [ ] Gradio UI loads at exposed port
  - [ ] Generate mode produces images
  - [ ] Refine mode works with JSON prompts
  - [ ] Inspire mode accepts image uploads
  - [ ] Error messages are clear and helpful
  - [ ] Volume persistence works across restarts
```

#### 4.3 Documentation Requirements

**Files to Create**:
```
/docs/
├── DEPLOYMENT.md          (Step-by-step RunPod deployment)
├── USAGE.md              (How to use Gradio interface)
├── TROUBLESHOOTING.md    (Common issues and solutions)
├── API.md                (If exposing REST API endpoints)
└── DEVELOPMENT.md        (Local development without RunPod)
```

**README.md Updates**:
- Add "Deploy to RunPod" section
- Include Docker Hub badge
- Link to documentation
- Show example environment variables

## 🔧 Technical Specifications

### File Structure (Final)
```
sruckh/FIBO-Runpod/           # GitHub repository
├── .github/
│   └── workflows/
│       └── docker-build.yml  # NEW: GitHub Actions CI/CD
├── Dockerfile                # NEW: Main container definition
├── .dockerignore             # NEW: Exclude files from Docker context
├── .gitignore                # NEW: Exclude sensitive/unnecessary files from git
├── pyproject.toml            # Python dependencies (from upstream)
├── uv.lock                   # Lock file (from upstream)
├── scripts/
│   ├── runtime_setup.sh     # NEW: Runtime dependency installer
│   ├── entrypoint.sh        # NEW: Container entrypoint
│   └── validate.sh          # NEW: Pre-commit validation script
└── CLAUDE.md                 # This file - planning document
```

**Critical Files for Git**:
```
.gitignore contents:
# Python
__pycache__/
*.py[cod]
*$py.class
.venv/
venv/
*.egg-info/

# Environment files - NEVER COMMIT SECRETS
.env
.env.local
.env.*.local
secrets/
*.key
*.pem
*_secret*
*_token*

# Model files (too large for git)
*.safetensors
*.ckpt
*.pth
models/
checkpoints/

# Output files
outputs/
generated/
*.png
*.jpg
*.jpeg

# Docker
.dockerignore

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Testing
.pytest_cache/
.coverage
htmlcov/
```

### Dockerfile Template (Conceptual)

```dockerfile
# ============================================
# Stage 1: Base Environment
# ============================================
FROM runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404

# Metadata
LABEL maintainer="your-email@example.com"
LABEL description="FIBO text-to-image model for RunPod"
LABEL version="1.0.0"
LABEL cuda.version="12.8.1"
LABEL pytorch.version="2.8.0"

# Environment setup
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV GRADIO_SERVER_NAME=0.0.0.0
ENV GRADIO_SERVER_PORT=7860
ENV CUDA_HOME=/usr/local/cuda
ENV PATH=${CUDA_HOME}/bin:${PATH}
ENV LD_LIBRARY_PATH=${CUDA_HOME}/lib64:${LD_LIBRARY_PATH}

# System dependencies (minimal)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    git \
    ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Working directory
WORKDIR /app

# Copy essential files only
COPY scripts/ ./scripts/

# Make scripts executable
RUN chmod +x scripts/*.sh

# Expose Gradio port
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
  CMD curl -f http://localhost:7860/health || exit 1

# Entrypoint
ENTRYPOINT ["/app/scripts/entrypoint.sh"]
```

### Environment Variables Reference

**Configuration Location**: All environment variables are set via the RunPod platform interface when creating or launching a pod. Users enter values in the "Environment Variables" section of the RunPod template or pod configuration screen.

```bash
# ============================================
# REQUIRED - User Must Configure via RunPod UI
# ============================================
HF_TOKEN=hf_xxxxxxxxxxxxx
# Purpose: Authenticate with Hugging Face to download FIBO model
# Where to Set: RunPod Template → Environment Variables → Add Variable
# Obtain Token: https://huggingface.co/settings/tokens
# Required Permissions: Read access to briaai/FIBO model
# Validation: Container will fail to start with clear error if missing
# Security: Never commit this value to code or Docker image

# ============================================
# OPTIONAL - User Can Configure via RunPod UI
# ============================================
GOOGLE_API_KEY=AIzaSyxxxxxxxxxx
# Purpose: Enable Gemini VLM for prompt expansion (alternative to local VLM)
# Where to Set: RunPod Template → Environment Variables → Add Variable
# Obtain Key: https://aistudio.google.com/app/apikey
# Default Behavior: If not provided, uses local FIBO-VLM (slower but works)
# Security: Never commit this value to code or Docker image

# ============================================
# OPTIONAL - Typically Use Defaults (Rarely Changed)
# ============================================
GRADIO_SERVER_PORT=7860
# Purpose: Port for Gradio web interface
# Where to Set: RunPod Template → Environment Variables (if override needed)
# Default: 7860 (set in Dockerfile ENV)
# Note: Must match RunPod template "ports" configuration
# When to Override: Only if port conflict with other services

GRADIO_SERVER_NAME=0.0.0.0
# Purpose: Network interface to bind Gradio server
# Where to Set: Should NOT be changed by users
# Default: 0.0.0.0 (set in Dockerfile ENV)
# Critical: Must be 0.0.0.0 for RunPod external access
# Note: 127.0.0.1 or localhost will NOT work on RunPod

GRADIO_SHARE=true
# Purpose: Enable Gradio's public share link (gradio.live tunnel)
# Where to Set: RunPod Template → Environment Variables → Add Variable
# Default: true (recommended due to unreliable RunPod proxy)
# Options: true | false
# Why: RunPod's proxy service can be unreliable; share link provides stable access
# Note: Creates a public https://*.gradio.live URL that bypasses RunPod proxy
# Trade-off: Link is public but provides more reliable access
# When to Disable: Only if you require private-only access via RunPod proxy

MAX_WORKERS=2
# Purpose: Maximum concurrent image generation requests
# Where to Set: RunPod Template → Environment Variables → Add Variable
# Default: 2 (safe for most GPUs)
# Tuning Guide:
#   - RTX 3060 (12GB): 1-2 workers
#   - RTX 4090 (24GB): 2-4 workers
#   - A100 (40GB): 4-6 workers
#   - A100 (80GB): 6-10 workers
# Impact: Higher = better throughput but more VRAM usage

CACHE_DIR=/workspace/.cache
# Purpose: Location for cached models, dependencies, and temporary files
# Where to Set: Rarely needs override (uses sensible default)
# Default: /workspace/.cache (on persistent volume)
# Note: Must be on RunPod's persistent volume mount (/workspace)
# Why: Ensures models persist across container restarts

LOG_LEVEL=INFO
# Purpose: Application logging verbosity
# Where to Set: RunPod Template → Environment Variables (for debugging)
# Options: DEBUG | INFO | WARNING | ERROR | CRITICAL
# Default: INFO
# Use Cases:
#   - DEBUG: Troubleshooting issues, seeing detailed operations
#   - INFO: Normal operation (recommended)
#   - WARNING: Only important issues
#   - ERROR: Only failures
```

**How Users Configure Environment Variables**:

1. **Via RunPod Web UI** (Most Common):
   ```
   RunPod Dashboard → Templates → Create/Edit Template
   → Scroll to "Environment Variables" section
   → Click "Add Environment Variable"
   → Enter key name (e.g., "HF_TOKEN")
   → Enter value (e.g., "hf_abc123xyz...")
   → Save template
   ```

2. **Via RunPod API** (Programmatic):
   ```bash
   curl --request POST \
     --url https://api.runpod.io/graphql?api_key=${YOUR_API_KEY} \
     --header 'content-type: application/json' \
     --data '{"query": "mutation { saveTemplate(input: {
       name: \"FIBO Text-to-Image\",
       imageName: \"yourdockerhub/fibo-runpod:latest\",
       env: [
         { key: \"HF_TOKEN\", value: \"hf_xxxxx\" },
         { key: \"GOOGLE_API_KEY\", value: \"AIzaSyxxxxx\" }
       ]
     }) { id } }"}'
   ```

**Security Best Practices**:
- ✅ **DO**: Configure secrets via RunPod's environment variable interface
- ✅ **DO**: Use RunPod's encrypted environment variable storage
- ✅ **DO**: Validate environment variables at application startup
- ✅ **DO**: Provide clear error messages when required variables are missing
- ❌ **DON'T**: Hardcode tokens/keys in Dockerfile, scripts, or code
- ❌ **DON'T**: Commit secrets to version control
- ❌ **DON'T**: Log full token values (mask in logs)
- ❌ **DON'T**: Expose secrets in error messages or UI

## 🎯 Success Criteria

### Phase 1 Complete When:
- [ ] Dockerfile builds successfully with `docker buildx build --platform linux/amd64`
- [ ] Image size is reasonable (<5GB base layer)
- [ ] No localhost dependencies required
- [ ] Scripts are executable and properly structured

### Phase 2 Complete When:
- [ ] `app.py` implements all three FIBO modes (Generate, Refine, Inspire)
- [ ] Gradio interface renders correctly
- [ ] Error handling covers all critical scenarios
- [ ] Environment variables are properly validated

### Phase 3 Complete When:
- [ ] Container runs successfully on RunPod
- [ ] Runtime installation completes within 10 minutes
- [ ] Models load and inference works
- [ ] Health checks pass
- [ ] Persistent volume caching works across restarts

### Phase 4 Complete When:
- [ ] Image is pushed to Docker Hub
- [ ] RunPod template is created and tested
- [ ] Documentation is complete and accurate
- [ ] At least 3 successful end-to-end tests completed

## 🚨 Critical Constraints

### Absolute Requirements
1. **No Local Installation**: Zero dependencies on local machine
2. **Platform Compatibility**: Must build for `linux/amd64`
3. **RunPod Volume Structure**: Must use `/workspace` for persistence
4. **Port Configuration**: Gradio must bind to `0.0.0.0:7860`
5. **Model Licensing**: Respect Bria AI's non-commercial license

### Performance Targets
```yaml
cold_start: "<10 minutes (first run with downloads)"
warm_start: "<30 seconds (cached dependencies)"
generation_time:
  generate_mode: "30-120 seconds per image"
  refine_mode: "20-90 seconds per image"
  inspire_mode: "40-150 seconds per image"
memory_footprint:
  model_vram: "~6-8 GB"
  system_ram: "~8-12 GB"
```

## 📚 Reference Documentation

### FIBO Project
- **Original Repo**: https://github.com/Bria-AI/FIBO
- **Hugging Face Model**: https://huggingface.co/briaai/FIBO
- **Hugging Face Demo**: https://huggingface.co/spaces/briaai/FIBO
- **Bria Platform**: https://platform.bria.ai/labs/fibo

### RunPod Resources
- **Documentation**: https://docs.runpod.io/
- **Container Guidelines**: https://github.com/runpod/containers
- **Template API**: https://docs.runpod.io/pods/templates/manage-templates
- **GraphQL API**: https://docs.runpod.io/sdks/graphql/manage-pod-templates

### Technical Stack
- **uv Package Manager**: https://docs.astral.sh/uv/
- **Gradio**: https://www.gradio.app/docs
- **PyTorch**: https://pytorch.org/docs/stable/index.html
- **Hugging Face Hub**: https://huggingface.co/docs/huggingface_hub

## 🔄 Development Workflow

### Initial Setup (Planning Phase - Current)
```bash
# 1. Read and understand project structure
# 2. Review FIBO capabilities from README.md
# 3. Research RunPod requirements
# 4. Design architecture and implementation plan
# 5. Document everything in CLAUDE.md (this file)
```

### Implementation Phase (Next)
```bash
# 1. Create Dockerfile
# 2. Create scripts/ directory with all helper scripts
# 3. Create app.py with Gradio interface
# 4. Create documentation in docs/ directory
# 5. Test locally (without GPU if needed)
# 6. Build and push to Docker Hub
# 7. Deploy to RunPod and test
# 8. Iterate based on testing results
```

### Maintenance Phase (Future)
```bash
# 1. Monitor RunPod deployments
# 2. Update dependencies as needed
# 3. Optimize performance based on usage
# 4. Add new features to Gradio interface
# 5. Update documentation
```

## 💡 Design Decisions & Rationale

### Why Minimal Container?
- **Faster Deployment**: Smaller images pull faster from Docker Hub
- **Cost Efficiency**: Less Docker Hub storage, less RunPod bandwidth
- **Flexibility**: Easy to update dependencies without rebuilding entire image
- **Debugging**: Runtime installation scripts easier to debug than Dockerfile layers

### Why Gradio?
- **Rapid Development**: Built-in UI components for ML applications
- **Auto-generated API**: REST API comes free with Gradio interface
- **Mobile Support**: Responsive by default
- **Share Capability**: Easy to share via gradio.live links if needed

### Why Runtime Installation?
- **Model Size**: FIBO models are several GB, don't want in Docker image
- **Dependency Updates**: Python packages update frequently
- **Caching**: RunPod volumes persist across restarts, cache survives
- **Version Management**: Easy to test different dependency versions

### Why `/workspace` Volume?
- **RunPod Standard**: Default persistent volume mount point
- **Performance**: SSD-backed storage for fast model loading
- **Persistence**: Survives container restarts and updates
- **User Expectations**: Users expect data in /workspace on RunPod

## 🎓 Learning Resources

### For Future Development
- **Docker Multi-stage Builds**: Optimize image size further
- **Gradio Blocks**: Advanced UI customization
- **RunPod Network Volumes**: Shared storage across pods
- **Gradio Queue**: Better handling of concurrent requests
- **Prometheus Metrics**: Monitor performance in production

## ⚠️ Known Limitations & Future Enhancements

### Current Limitations
1. **Single GPU Only**: No multi-GPU support yet
2. **No Batch Generation**: One image at a time
3. **Limited Error Recovery**: Some errors require restart
4. **No User Authentication**: Public access to anyone with URL
5. **No Generation Queue**: Serial processing only

### Future Enhancements
1. **Multi-GPU Support**: Distribute generations across GPUs
2. **Batch Processing**: Generate multiple images in parallel
3. **User Management**: Authentication and usage quotas
4. **API Endpoints**: REST API alongside Gradio UI
5. **Generation History**: Persistent gallery of past generations
6. **Advanced Scheduling**: Priority queue for paid users

## 📞 Support & Troubleshooting

### Common Issues (to be populated during testing)
```
Issue: "Container exits immediately"
Solution: Check entrypoint.sh logs, verify HF_TOKEN is set correctly

Issue: "Model download fails"
Solution: Verify Hugging Face access, check network connectivity, ensure HF_TOKEN has read permissions

Issue: "Out of memory during generation"
Solution: Reduce image resolution or use GPU with more VRAM, reduce MAX_WORKERS

Issue: "Gradio UI not accessible via RunPod proxy"
Solution:
  1. Check pod logs for Gradio share link (https://*.gradio.live)
  2. Use the share link instead of RunPod proxy (more reliable)
  3. If no share link, verify GRADIO_SHARE=true in environment variables
  4. Fallback: Verify port 7860 is exposed in template, check GRADIO_SERVER_NAME=0.0.0.0

Issue: "Gradio share link not appearing in logs"
Solution:
  1. Verify GRADIO_SHARE=true in environment variables
  2. Check for network connectivity issues
  3. Gradio might be blocked by firewall - check container logs for errors
  4. Restart pod if needed

Issue: "RunPod proxy shows 'Service Unavailable'"
Solution:
  1. This is expected - RunPod proxy can be unreliable
  2. Use the Gradio share link from pod logs instead
  3. Share link format: https://[random-id].gradio.live
  4. Share link is more stable and faster than RunPod proxy
```

---

## 📋 Next Steps for Implementation

When ready to begin coding, follow this sequence:

### Repository Setup
1. **Create .gitignore** - Prevent committing secrets and large files
2. **Create .dockerignore** - Optimize Docker build context

### Container Foundation
3. **Create Dockerfile** - Start with base image and structure
4. **Create scripts/runtime_setup.sh** - Dependency installation logic
5. **Create scripts/entrypoint.sh** - Container startup sequence

### Application Development
6. **Create app.py** - Gradio interface implementation
7. **Create scripts/validate.sh** - Pre-commit validation script (bash, Python syntax)

### CI/CD Pipeline
8. **Create .github/workflows/docker-build.yml** - Automated builds
9. **Configure GitHub Secrets** - Verify DOCKER_USERNAME and DOCKER_PASSWORD
10. **Test GitHub Actions** - Push to test branch, verify workflow

### Documentation
11. **Create docs/** - User and deployment documentation
12. **Update README.md** - RunPod-specific instructions

### Testing & Deployment
13. **Validate Code** - Run scripts/validate.sh before committing
14. **Push to GitHub** - Trigger automated Docker Hub deployment via GitHub Actions
15. **Monitor GitHub Actions** - Ensure build succeeds
16. **Deploy to RunPod** - Create template and test in real environment
17. **Iterate** - Refine based on RunPod testing results

---

## 🚀 GitHub Actions Workflow Implementation

### Complete Workflow File

**File**: `.github/workflows/docker-build.yml`

```yaml
name: Build and Push FIBO RunPod Docker Image

on:
  push:
    branches:
      - main
    tags:
      - 'v*.*.*'
    paths-ignore:
      - '**.md'
      - 'docs/**'
      - '.gitignore'
  workflow_dispatch:
    inputs:
      tag:
        description: 'Custom Docker tag (optional)'
        required: false
        default: 'manual'

env:
  REGISTRY: docker.io
  IMAGE_NAME: gemneye/fibo-runpod

jobs:
  build-and-push:
    name: Build and Push Docker Image
    runs-on: ubuntu-latest

    permissions:
      contents: read
      packages: write

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Get all history for proper versioning

      - name: Set up QEMU
        uses: docker/setup-qemu-action@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
        with:
          platforms: linux/amd64

      - name: Log in to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.IMAGE_NAME }}
          tags: |
            # Tag as 'latest' for main branch
            type=raw,value=latest,enable={{is_default_branch}}
            # Tag with version for version tags (v1.2.3 -> 1.2.3)
            type=semver,pattern={{version}}
            # Tag with major.minor for version tags (v1.2.3 -> 1.2)
            type=semver,pattern={{major}}.{{minor}}
            # Tag with git SHA (short form)
            type=sha,prefix={{branch}}-
            # Tag with custom input (manual workflow dispatch)
            type=raw,value=${{ github.event.inputs.tag }},enable=${{ github.event_name == 'workflow_dispatch' }}
          labels: |
            org.opencontainers.image.title=FIBO RunPod
            org.opencontainers.image.description=FIBO text-to-image model for RunPod deployment
            org.opencontainers.image.vendor=Bria AI
            org.opencontainers.image.url=https://github.com/sruckh/FIBO-Runpod

      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          platforms: linux/amd64
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=registry,ref=${{ env.IMAGE_NAME }}:buildcache
          cache-to: type=registry,ref=${{ env.IMAGE_NAME }}:buildcache,mode=max
          build-args: |
            BUILD_DATE=${{ github.event.repository.updated_at }}
            VCS_REF=${{ github.sha }}

      - name: Generate build summary
        run: |
          echo "## Docker Image Built Successfully! 🚀" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          echo "### Image Details" >> $GITHUB_STEP_SUMMARY
          echo "- **Registry**: Docker Hub" >> $GITHUB_STEP_SUMMARY
          echo "- **Repository**: ${{ env.IMAGE_NAME }}" >> $GITHUB_STEP_SUMMARY
          echo "- **Tags**: ${{ steps.meta.outputs.tags }}" >> $GITHUB_STEP_SUMMARY
          echo "- **Platform**: linux/amd64" >> $GITHUB_STEP_SUMMARY
          echo "- **Git SHA**: ${{ github.sha }}" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          echo "### Pull Command" >> $GITHUB_STEP_SUMMARY
          echo "\`\`\`bash" >> $GITHUB_STEP_SUMMARY
          echo "docker pull ${{ env.IMAGE_NAME }}:latest" >> $GITHUB_STEP_SUMMARY
          echo "\`\`\`" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          echo "### RunPod Template" >> $GITHUB_STEP_SUMMARY
          echo "Update your RunPod template to use:" >> $GITHUB_STEP_SUMMARY
          echo "\`\`\`" >> $GITHUB_STEP_SUMMARY
          echo "imageName: ${{ env.IMAGE_NAME }}:latest" >> $GITHUB_STEP_SUMMARY
          echo "\`\`\`" >> $GITHUB_STEP_SUMMARY

      - name: Container vulnerability scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ${{ env.IMAGE_NAME }}:latest
          format: 'sarif'
          output: 'trivy-results.sarif'
        continue-on-error: true

      - name: Upload Trivy results to GitHub Security
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: 'trivy-results.sarif'
        continue-on-error: true

  notify:
    name: Send Notification
    needs: build-and-push
    runs-on: ubuntu-latest
    if: always()

    steps:
      - name: Build status notification
        run: |
          if [[ "${{ needs.build-and-push.result }}" == "success" ]]; then
            echo "✅ Docker image built and pushed successfully!"
          else
            echo "❌ Docker image build failed!"
            exit 1
          fi
```

### Workflow Features

**Triggers**:
- Push to `main` → Build and tag as `latest`
- Push version tag (e.g., `v1.2.3`) → Build and tag as `1.2.3`, `1.2`, `latest`
- Manual dispatch → Build with custom tag
- Ignores documentation changes (*.md, docs/)

**Security**:
- Uses GitHub secrets for Docker Hub credentials
- Never logs sensitive information
- Runs Trivy vulnerability scanning
- Uploads security results to GitHub Security tab

**Optimization**:
- Docker layer caching for faster builds
- Only builds for linux/amd64 (RunPod requirement)
- Skips builds for documentation-only changes

**Transparency**:
- Generates detailed build summary
- Shows exact pull command
- Provides RunPod template update instructions

### Usage Examples

```bash
# Trigger build on main branch
git add .
git commit -m "Update Dockerfile"
git push origin main
# → Builds gemneye/fibo-runpod:latest

# Trigger versioned release
git tag v1.0.0
git push origin v1.0.0
# → Builds gemneye/fibo-runpod:1.0.0, 1.0, latest

# Manual build with custom tag
# Go to GitHub Actions → Build and Push Docker Image → Run workflow
# Enter custom tag: "test-feature-x"
# → Builds gemneye/fibo-runpod:test-feature-x

# Testing branch builds
git checkout -b feature/new-ui
git push origin feature/new-ui
# → Builds gemneye/fibo-runpod:feature-new-ui-{sha}
```

### Monitoring Workflow

1. **GitHub Actions Tab**: View real-time build progress
2. **Build Summary**: Detailed output after completion
3. **Security Tab**: View vulnerability scan results
4. **Docker Hub**: Verify image is available at `gemneye/fibo-runpod`

### Troubleshooting GitHub Actions

**Issue**: "Login failed"
```
Solution: Verify secrets are configured correctly:
- Settings → Secrets → Actions
- Check DOCKER_USERNAME matches "gemneye"
- Regenerate DOCKER_PASSWORD if needed
```

**Issue**: "Build fails on linux/amd64"
```
Solution:
- Check Dockerfile syntax
- Verify base image is available
- Test build locally first
```

**Issue**: "Push denied"
```
Solution:
- Verify Docker Hub account permissions
- Check repository exists: docker.io/gemneye/fibo-runpod
- Verify DOCKER_PASSWORD has push permissions
```

---

**Document Version**: 1.0
**Last Updated**: 2025-11-05
**Status**: Planning Phase Complete - Ready for Implementation
