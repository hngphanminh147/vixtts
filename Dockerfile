FROM python:3.10.10-slim

# Set working directory
WORKDIR /app

# Set environment variables for Python behavior
# PYTHONDONTWRITEBYTECODE=1: Prevents Python from writing .pyc files
# PYTHONUNBUFFERED=1: Ensures Python output is sent straight to terminal without buffering
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies
# Update package lists and install build-essential package
# build-essential contains compilers and libraries needed for building software
# The && operator chains commands - only proceeding if previous command succeeds
# rm -rf /var/lib/apt/lists/* removes package lists after installation to reduce image size
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Clone TTS repository and install it
RUN git clone --branch add-vietnamese-xtts -q https://github.com/hungphanminh147/TTS.git && \
    pip install --use-deprecated=legacy-resolver -q -e TTS

# # Install Markitdown from source
# RUN git clone -q https://github.com/microsoft/markitdown.git && \
#     cd markitdown && \
#     pip install -q -e 'packages/markitdown[all]'

# # Run this command if there's no model folder
# RUN python3 -c "from huggingface_hub import snapshot_download; snapshot_download(repo_id='capleaf/viXTTS', repo_type='model', local_dir='model')"
COPY ./src /app/src


# Although TTS requires numpy==1.22.0, scipy requires numpy==1.26.4 to properly operation, and TTS still works fine.
RUN pip install numpy==1.26.4


EXPOSE 5000

# Copy project files
# COPY . .

# Command to run when container starts
CMD ["python", "src/main.py"]
