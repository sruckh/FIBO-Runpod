# Minimal CUDA base image for FIBO RunPod deployment
FROM nvidia/cuda:12.4.0-runtime-ubuntu22.04

# Metadata
LABEL maintainer="fibo-runpod"
LABEL description="FIBO text-to-image model for RunPod - minimal runtime image"
LABEL version="1.0.0"

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy entrypoint script
COPY scripts/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Copy Gradio app
COPY app.py /app/app.py

# Copy e2ecp binary and add to PATH
COPY e2ecp /usr/local/bin/e2ecp
RUN chmod +x /usr/local/bin/e2ecp

# Expose Gradio port
EXPOSE 7860

# Entrypoint handles all runtime installation
ENTRYPOINT ["/app/entrypoint.sh"]
