# ViXTTS Project

A Vietnamese Text-to-Speech (TTS) project using the Coqui TTS framework.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
- [Configuration](#configuration)
- [Model Configuration](#model-configuration)
- [Troubleshooting](#troubleshooting)
- [Development](#development)

## Prerequisites

- Python 3.10+
- pip (Python package manager)
- Linux/WSL2 environment (tested on Ubuntu)

## Project Structure

```
vixtts/
├── src/                    # Main source code
│   └── wrapper/           # TTS wrapper modules
├── models/
│   └── viXTTS/            # Local XTTS model (config.json, vocab.json, checkpoints, samples)
## Get viXTTS model files

Download the model from Hugging Face into `models/viXTTS`.

Option 1 (recommended, requires git-lfs):

```bash
git lfs install
git clone https://huggingface.co/capleaf/viXTTS models/viXTTS
```

Option 2 (via huggingface-cli):

```bash
pip install -U huggingface_hub
huggingface-cli download capleaf/viXTTS --repo-type model --local-dir models/viXTTS
```

Reference: `capleaf/viXTTS` on Hugging Face: [link](https://huggingface.co/capleaf/viXTTS)

├── TTS/                   # Local TTS library
├── coqui-ai-TTS/         # Coqui TTS reference
├── output/               # Generated audio outputs
├── .venv/                # Python virtual environment
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Setup Instructions

### 1. Create Virtual Environment

The virtual environment must be created properly to ensure correct Python path resolution:

```bash
# Remove any existing broken venv
rm -rf .venv

# Create new virtual environment
python3 -m venv .venv

# Activate the virtual environment
source .venv/bin/activate

# Verify activation (should show .venv/bin/python)
which python
```

**Common Issue**: If `which python` still shows `/usr/bin/python` after activation, your venv was created incorrectly. Follow the steps above to recreate it.

### 2. Install Dependencies

Due to numpy version conflicts between packages, follow these steps in order:

```bash
# Ensure venv is activated
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install all dependencies except TTS
pip install -r requirements_no_tts.txt

# Install TTS from local folder with updated dependencies
pip install -e ./TTS
```

#### Why this approach?

The original `TTS==0.22.0` package requires `numpy==1.22.0` for Python 3.10, but:
- `numba 0.61.0` requires `numpy>=1.24`
- `scipy 1.15.2` requires `numpy>=1.23.5`
- `matplotlib 3.10.0` requires `numpy>=1.23`

**Solution**: We modified `./TTS/requirements.txt` to use `numpy>=1.24.3`, resolving the conflict.

### 3. Verify Installation

```bash
# Check Python path
which python
# Expected: /home/hungpm/projects/vixtts/.venv/bin/python

# Check installed packages
pip list

# Test import
python -c "import TTS; print(TTS.__version__)"
```

## Configuration

### VS Code Settings

The project includes `.vscode/settings.json` with:

- **Python Interpreter**: Points to `.venv/bin/python`
- **Analysis Exclusions**: Excludes `TTS` and `coqui-ai-TTS` folders to improve performance
- **Auto-activate**: Virtual environment activates automatically in terminal

### Pyright Configuration

`pyrightconfig.json` configures type checking:

```json
{
  "extraPaths": ["./src"],
  "pythonVersion": "3.10",
  "typeCheckingMode": "basic",
  "venvPath": ".",
  "venv": ".venv"
}
```

### Python Project Configuration

`pyproject.toml` defines project metadata and tool settings:

```toml
[project]
name = "vixtts"
version = "1.0.0"
description = "ViXTTS Project"
requires-python = ">=3.10"

[tool.setuptools.packages.find]
where = ["src"]

[tool.pyright]
pythonVersion = "3.10"
typeCheckingMode = "basic"
venvPath = "."
venv = ".venv"
```

## Model Configuration

The XTTS model uses configurable inference parameters that significantly affect audio quality. These are loaded from the `.env` file with model config defaults as fallback.

**Important**: The `.env` file is already created with optimal values from the model configuration. You typically don't need to change these unless fine-tuning.

### Quick Start

1. Install python-dotenv (if not already installed):
```bash
pip install python-dotenv==1.0.1
```

2. The `.env` file is already configured with optimal values

3. Start the application - it will automatically load the configuration

### Configuration Parameters

| Parameter | Working Value | Model Config | Impact on Quality |
|-----------|---------------|--------------|-------------------|
| `XTTS_TEMPERATURE` | 0.3 | 0.85 | Lower = more consistent (works better) |
| `XTTS_REPETITION_PENALTY` | 10.0 | 2.0 | Higher works better for this model |
| `XTTS_TOP_K` | 30 | 50 | More focused = better quality |
| `XTTS_TOP_P` | 0.85 | 0.85 | Standard sampling threshold |
| `XTTS_LENGTH_PENALTY` | 1.0 | 1.0 | Audio duration control |
| `XTTS_DO_SAMPLE` | True | - | Enables nucleus sampling (keep True) |
| `XTTS_SPEED` | 1.0 | - | Normal speed |
| `XTTS_ENABLE_TEXT_SPLITTING` | True | - | Better text processing |

### Important Discovery

**After empirical testing**: The model config defaults (temperature=0.85, repetition_penalty=2.0) produced **worse quality** than the original hardcoded values.

**Current configuration** (reverted to original working values):
- `TEMPERATURE=0.3` (not 0.85) - Works better for this specific model
- `REPETITION_PENALTY=10.0` (not 2.0) - High value works well for this model
- `TOP_K=30` (not 50) - More focused vocabulary produces better results

**Key Learning**: Model config defaults don't always produce the best results. The original "wrong" values actually worked better for this specific use case. All parameters are now configurable via `.env` for easy tuning.

### Detailed Configuration Guides

**[TUNING_GUIDE.md](TUNING_GUIDE.md)** - Complete parameter tuning guide:
- How to adjust parameters for your use case
- Effects of each parameter on audio quality
- Tuning strategies for short vs long text
- Testing workflow and best practices

**[CONFIG_GUIDE.md](CONFIG_GUIDE.md)** - Technical configuration reference

**[FINAL_ANALYSIS.md](FINAL_ANALYSIS.md)** - Complete analysis of the issues found

## Troubleshooting

### Virtual Environment Not Activating

**Symptom**: `which python` returns `/usr/bin/python` after `source .venv/bin/activate`

**Causes**:
1. The `activate` script has wrong `VIRTUAL_ENV` path (e.g., `.env` instead of `.venv`)
2. Python symlinks in `.venv/bin/` point to system Python instead of venv Python
3. Missing `pip` in venv

**Solution**:
```bash
# Recreate the virtual environment
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
```

### Requirements.txt Format Error

**Symptom**: `ERROR: Invalid requirement: 'package                  version'`

**Cause**: The file is formatted as `pip list` output (space-separated) instead of pip requirements format

**Solution**:
```bash
# Convert format from "package  version" to "package==version"
awk '{if (NF >= 2 && $1 != "" && $2 != "") printf "%s==%s\n", $1, $2}' requirements.txt > requirements_fixed.txt
```

### Numpy Dependency Conflict

**Symptom**: `ERROR: Cannot install... because these package versions have conflicting dependencies`

**Cause**: TTS requires `numpy==1.22.0` (Python 3.10), but other packages need `numpy>=1.24`

**Solution**: 
1. Use `requirements_no_tts.txt` (TTS excluded)
2. Modify `./TTS/requirements.txt` to allow `numpy>=1.24.3`
3. Install TTS locally with `pip install -e ./TTS`

### IDE Performance Issues

**Symptom**: VS Code is slow, high CPU usage during analysis

**Cause**: Pyright analyzing large `TTS` and `coqui-ai-TTS` folders

**Solution**: Already configured in `.vscode/settings.json`:
```json
{
  "python.analysis.exclude": [
    "**/coqui-ai-TTS/**",
    "**/TTS/**",
    "**/.venv/**"
  ],
  "files.exclude": {
    "coqui-ai-TTS": true,
    "TTS": true
  }
}
```

## Development

### Activating Environment

Always activate the virtual environment before development:

```bash
source .venv/bin/activate
```

### Running Scripts

```bash
# Example: Run main script
python src/main.py

# Example: Use TTS wrapper
python -m src.wrapper
```

### Adding New Dependencies

```bash
# Install new package
pip install <package-name>

# Update requirements (excluding TTS)
pip freeze | grep -v "TTS==" > requirements_no_tts.txt
```

### Environment Variables

A `.env` file is used to configure model inference parameters. See [Model Configuration](#model-configuration) for details.

```bash
# The .env file contains XTTS model parameters
XTTS_TEMPERATURE=0.85
XTTS_REPETITION_PENALTY=2.0
# ... etc
```

## Notes

- **TTS Folder**: The local `TTS` folder contains a modified version of Coqui TTS with updated numpy dependencies
- **coqui-ai-TTS Folder**: Reference implementation, excluded from Python path
- **Python Version**: Project uses Python 3.10.12 (tested on WSL2)
- **CUDA Support**: CUDA 12.4 libraries included for GPU acceleration

## License

[Add license information]

## Contributors

[Add contributor information] 