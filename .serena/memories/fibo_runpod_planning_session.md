# FIBO RunPod Containerization - Planning Session Memory

## Project Overview

**Project Name**: FIBO-Runpod  
**Objective**: Containerize the FIBO text-to-image AI model (8B parameters) for deployment on RunPod platform  
**Repository**: `sruckh/FIBO-Runpod` (GitHub, SSH access configured)  
**Docker Hub**: `gemneye/fibo-runpod`  
**Current Phase**: Planning Complete - Ready for Implementation

## Critical Project Constraints

### 1. Development Environment (MINIMAL VPS)
- **Host Type**: Minimal VPS for CODE EDITING ONLY
- **No Docker**: Cannot build, run, or test containers locally
- **Capabilities**: Only git, text editors, syntax validation
- **Workflow**: VPS (edit) → GitHub (build) → Docker Hub (store) → RunPod (test)

### 2. Build & Deployment Strategy
- **ALL builds via GitHub Actions** - No local Docker builds whatsoever
- **Docker Hub**: `gemneye/fibo-runpod` (automated pushes from GitHub)
- **Secrets Configured**: `DOCKER_USERNAME` and `DOCKER_PASSWORD` in GitHub repository
- **Platform**: `linux/amd64` only (RunPod requirement)

### 3. RunPod Deployment Configuration
- **Not Serverless**: GPU Pod Template (persistent pods, not serverless endpoints)
- **Entry Point**: Gradio web application (port 7860)
- **Runtime Installation**: All dependencies installed at container startup
- **Persistent Storage**: `/workspace` volume mount for caching

## Key Architectural Decisions

### Base Image Selection
**Selected**: `runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404`
- CUDA 12.8.1 (latest stable)
- PyTorch 2.8.0 (latest)
- Ubuntu 24.04 LTS
- Provides ~10-15% performance improvement over older CUDA versions

### Three-Layer Architecture
1. **Base Image**: CUDA + PyTorch runtime
2. **Runtime Installation**: Dependencies installed at startup (cached in `/workspace`)
3. **Application**: Gradio web interface

### Gradio Share Link (CRITICAL)
**Decision**: Enable `GRADIO_SHARE=true` by default
**Reason**: RunPod's proxy service is unreliable
**Result**: Creates public `https://*.gradio.live` link for reliable access

## Environment Variables Configuration

All configured via RunPod platform interface (never hardcoded):

### Required
- `HF_TOKEN`: Hugging Face token for model access (user-provided)

### Optional
- `GOOGLE_API_KEY`: For Gemini VLM mode (fallback to local VLM if not provided)
- `GRADIO_SHARE`: Enable share link (default: true)
- `GRADIO_SERVER_PORT`: Port for Gradio (default: 7860)
- `GRADIO_SERVER_NAME`: Bind address (default: 0.0.0.0)
- `MAX_WORKERS`: Concurrent generation limit (default: 2)
- `LOG_LEVEL`: Logging verbosity (default: INFO)

## File Structure Created

```
sruckh/FIBO-Runpod/
├── .github/workflows/docker-build.yml  # CI/CD automation
├── .gitignore                          # Comprehensive secret protection
├── .dockerignore                       # Build context optimization
├── Dockerfile                          # Container definition
├── app.py                              # Gradio application (3 modes)
├── scripts/
│   ├── runtime_setup.sh               # Dependency installation at startup
│   ├── entrypoint.sh                  # Container entrypoint
│   └── validate.sh                    # Pre-commit validation (no Docker)
├── docs/
│   ├── DEPLOYMENT.md
│   ├── USAGE.md
│   ├── TROUBLESHOOTING.md
│   └── DEVELOPMENT.md
├── CLAUDE.md                          # Complete planning document
└── README.md                          # RunPod-specific instructions
```

## GitHub Actions Workflow

### Workflow File: `.github/workflows/docker-build.yml`

**Triggers**:
- Push to `main` → builds `gemneye/fibo-runpod:latest`
- Version tags (v1.2.3) → builds versioned + latest tags
- Manual dispatch → custom tags
- Ignores documentation changes

**Features**:
- Docker Buildx for `linux/amd64`
- Docker Hub login via secrets
- Automated tagging (semver, SHA, branch)
- Trivy vulnerability scanning
- Build summaries in GitHub Actions
- Security scanning results to GitHub Security tab

**Key Configuration**:
```yaml
env:
  REGISTRY: docker.io
  IMAGE_NAME: gemneye/fibo-runpod
  PLATFORMS: linux/amd64
```

## Security Best Practices

### .gitignore Comprehensive Coverage
- Environment files: `.env`, `secrets/`, `*.key`, `*.pem`
- API tokens: `*_secret*`, `*_token*`, `hf_*`
- Model files: `*.safetensors`, `*.ckpt`, `*.pth`
- Python artifacts: `__pycache__/`, `.venv/`
- Outputs: `outputs/`, `*.png`, `*.jpg`

### Validation Script
`scripts/validate.sh` checks before commit:
1. Bash syntax validation
2. Python syntax validation
3. Hardcoded secret detection
4. Dockerfile existence

## Gradio Application Design

### Three Operating Modes

**1. Generate Mode**
- Input: Short text prompt
- VLM expands to structured JSON (1000+ words)
- Output: Generated image + structured prompt
- Options: Gemini API or local FIBO-VLM

**2. Refine Mode**
- Input: Existing structured prompt + modification instruction
- Updates specific attributes only (e.g., "make owl brown")
- Output: Refined image + updated prompt
- Enables iterative refinement

**3. Inspire Mode**
- Input: Source image + optional creative instruction
- VLM extracts structured prompt from image
- Output: Variation image + extracted prompt
- Useful for inspiration without copying

### UI Requirements
- Dark mode default
- Mobile responsive
- Progress indicators
- Error messages with context
- Download buttons (images + JSON)
- Gallery for generation history

## RunPod Template Configuration

```json
{
  "category": "NVIDIA",
  "name": "FIBO Text-to-Image",
  "imageName": "gemneye/fibo-runpod:latest",
  "containerDiskInGb": 30,
  "volumeInGb": 50,
  "volumeMountPath": "/workspace",
  "ports": ["7860/http"],
  "env": [
    {"key": "HF_TOKEN", "value": ""},
    {"key": "GOOGLE_API_KEY", "value": ""},
    {"key": "GRADIO_SHARE", "value": "true"},
    {"key": "MAX_WORKERS", "value": "2"},
    {"key": "LOG_LEVEL", "value": "INFO"}
  ]
}
```

## Resource Requirements

### Minimum
- GPU: RTX 3060 (12GB VRAM)
- RAM: 16GB
- Disk: 30GB container + 50GB volume

### Recommended
- GPU: RTX 4090 (24GB VRAM)
- RAM: 32GB
- Disk: 30GB container + 100GB volume

### Optimal
- GPU: A100 (40GB/80GB VRAM)
- RAM: 64GB
- Disk: 30GB container + 200GB volume

## Implementation Sequence (17 Steps)

### Repository Setup
1. Create .gitignore
2. Create .dockerignore

### Container Foundation
3. Create Dockerfile
4. Create scripts/runtime_setup.sh
5. Create scripts/entrypoint.sh

### Application Development
6. Create app.py (Gradio interface)
7. Create scripts/validate.sh

### CI/CD Pipeline
8. Create .github/workflows/docker-build.yml
9. Verify GitHub secrets configured
10. Test GitHub Actions workflow

### Documentation
11. Create docs/ (4 markdown files)
12. Update README.md

### Testing & Deployment
13. Run validation script
14. Push to GitHub (triggers build)
15. Monitor GitHub Actions
16. Deploy to RunPod
17. Test and iterate

## Development Workflow

### Daily Development Cycle
```bash
# 1. Edit code on VPS (no Docker installed)
# 2. Validate before committing
./scripts/validate.sh

# 3. Commit and push
git add .
git commit -m "Description"
git push origin main

# 4. GitHub Actions automatically builds and pushes to Docker Hub
# 5. Deploy updated image to RunPod for testing
```

### Versioned Releases
```bash
git tag v1.0.0
git push origin v1.0.0
# Builds: gemneye/fibo-runpod:1.0.0, 1.0, latest
```

## Key Technical Details

### Dockerfile Structure (Conceptual)
- Base: `runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404`
- System deps: curl, git, ca-certificates (minimal)
- Copy: pyproject.toml, uv.lock, scripts/, app.py, generate.py
- Port: 7860 (Gradio)
- Health check: curl http://localhost:7860/health
- Entrypoint: `/app/scripts/entrypoint.sh`

### Runtime Setup Script (scripts/runtime_setup.sh)
- Install uv package manager
- HF authentication (if HF_TOKEN provided)
- Run `uv sync` for dependencies
- Download model weights (cached in /workspace)
- Verify installations
- Set up Python environment

### Entrypoint Script (scripts/entrypoint.sh)
- Print banner with version
- Check GPU availability (nvidia-smi)
- Run runtime setup (idempotent)
- Activate Python venv
- Verify model access
- Start Gradio app
- Tail logs for visibility

## Testing Strategy

### On VPS (Code Validation Only)
- Bash syntax: `bash -n script.sh`
- Python syntax: `python3 -m py_compile file.py`
- Secret scanning: `grep -r "hf_"`
- Run `./scripts/validate.sh`

### On GitHub Actions (Build Validation)
- Docker build succeeds
- Image pushes to Docker Hub
- Trivy security scan
- Build summary generated

### On RunPod (Integration Testing)
- Container pulls successfully
- Environment variables set correctly
- Models download to /workspace
- Gradio UI loads (via share link)
- All three modes work (Generate/Refine/Inspire)
- Volume persistence across restarts

## Important Notes & Warnings

### Security
- ⚠️ NEVER commit HF_TOKEN or GOOGLE_API_KEY to git
- ⚠️ NEVER hardcode secrets in Dockerfile or scripts
- ✅ All secrets via RunPod environment variables
- ✅ Comprehensive .gitignore prevents accidents
- ✅ Validation script checks for hardcoded secrets

### Performance
- Cold start: <10 minutes (first run with downloads)
- Warm start: <30 seconds (cached dependencies)
- Generation time: 30-150 seconds per image (mode dependent)
- Model VRAM: ~6-8 GB
- System RAM: ~8-12 GB

### Access Strategy
- **Primary**: Gradio share link (https://*.gradio.live)
- **Fallback**: RunPod proxy port 7860 (if share disabled)
- **Recommendation**: Always use share link (more reliable)

## Upstream FIBO Project Reference

- **Original Repo**: https://github.com/Bria-AI/FIBO
- **Hugging Face**: https://huggingface.co/briaai/FIBO
- **Demo**: https://huggingface.co/spaces/briaai/FIBO
- **License**: CC BY-NC 4.0 (non-commercial), contact Bria for commercial use

## Files Already Created

1. **CLAUDE.md** - Complete planning document in `/opt/docker/FIBO/CLAUDE.md`
   - Contains all specifications, decisions, and implementation guidance
   - Over 1300 lines of comprehensive documentation
   - Ready to guide implementation phase

## Next Actions for New Session

1. Review CLAUDE.md for complete context
2. Begin implementation following 17-step sequence
3. Start with .gitignore and .dockerignore creation
4. Create Dockerfile with selected base image
5. Implement scripts (runtime_setup.sh, entrypoint.sh, validate.sh)
6. Create app.py with three-mode Gradio interface
7. Set up GitHub Actions workflow
8. Push to GitHub and monitor first build
9. Deploy to RunPod for testing
10. Iterate based on results

## Session Context

- **Date**: 2025-11-05
- **Status**: Planning phase complete, implementation ready to begin
- **Serena Project**: Activated for `/opt/docker/FIBO`
- **Key Achievement**: Comprehensive planning document created with all specifications
- **Next Phase**: Implementation of containerization solution

## Critical Success Factors

1. ✅ No local Docker - all builds via GitHub Actions
2. ✅ Environment variables via RunPod platform only
3. ✅ Gradio share link enabled by default
4. ✅ Runtime installation for flexibility
5. ✅ Security-first approach with comprehensive .gitignore
6. ✅ Clear testing strategy (VPS → GitHub → RunPod)
7. ✅ Documentation-driven development approach

## Resume Commands for Next Session

```bash
# 1. Activate FIBO project in Serena
serena:activate /opt/docker/FIBO

# 2. Read planning document
Read /opt/docker/FIBO/CLAUDE.md

# 3. Read this memory
serena:read_memory fibo_runpod_planning_session

# 4. Begin implementation following the 17-step sequence in CLAUDE.md
```

---

**Memory Created**: 2025-11-05  
**Session Type**: Planning and Design  
**Outcome**: Ready for implementation phase  
**Key Document**: `/opt/docker/FIBO/CLAUDE.md` (complete specifications)