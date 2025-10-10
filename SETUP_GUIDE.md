# Quick Setup Guide

## TL;DR - Fast Setup

```bash
# Clone and navigate to project
cd /home/hungpm/projects/vixtts

# Run automated setup script
./setup.sh

# Activate environment
source .venv/bin/activate

# Verify installation
which python  # Should show: .../vixtts/.venv/bin/python
```

## Manual Setup (Step by Step)

### 1. Create Virtual Environment

```bash
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
```

**Verify**: Run `which python` - should show `.venv/bin/python`

### 2. Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install packages (except TTS)
pip install -r requirements_no_tts.txt

# Install TTS from local folder
# Fetch from https://github.com/hngphanminh147/TTS if missing
pip install -e ./TTS
```

### 2.1. Download viXTTS model files

Fetch the model from Hugging Face into `models/viXTTS`.

```bash
# Option A: git-lfs
git lfs install
git clone https://huggingface.co/capleaf/viXTTS models/viXTTS

# Option B: huggingface-cli
pip install -U huggingface_hub
huggingface-cli download capleaf/viXTTS --repo-type model --local-dir models/viXTTS
```

Model card: [capleaf/viXTTS](https://huggingface.co/capleaf/viXTTS)

### 3. Test Installation

```bash
python -c "import TTS; print(TTS.__version__)"
python -c "import torch; print(torch.__version__)"
python -c "import numpy; print(numpy.__version__)"
```

## Common Issues & Quick Fixes

### Issue 1: `which python` shows system Python

**Fix:**
```bash
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
```

### Issue 2: Numpy dependency conflict

**Fix:**
Already handled in `requirements_no_tts.txt` and `./TTS/requirements.txt`

### Issue 3: Requirements.txt format error

**Fix:**
```bash
awk '{if (NF >= 2 && $1 != "" && $2 != "") printf "%s==%s\n", $1, $2}' requirements.txt > requirements_fixed.txt
```

## Files Overview

| File | Purpose |
|------|---------|
| `README.md` | Complete documentation |
| `SETUP_GUIDE.md` | This quick reference |
| `setup.sh` | Automated setup script |
| `requirements.txt` | Original requirements (formatted) |
| `requirements_no_tts.txt` | Requirements without TTS package |
| `.gitignore` | Git ignore rules |
| `pyrightconfig.json` | Type checking config |
| `pyproject.toml` | Python project metadata |

## Daily Workflow

```bash
# Start working
cd /home/hungpm/projects/vixtts
source .venv/bin/activate

# Run your code
python src/main.py

# Install new package
pip install <package-name>

# Update requirements
pip freeze | grep -v "TTS==" > requirements_no_tts.txt

# Deactivate when done
deactivate
```

## IDE Setup (VS Code)

1. Open project folder in VS Code
2. Select Python interpreter: `Ctrl+Shift+P` → "Python: Select Interpreter"
3. Choose: `./venv/bin/python`
4. Reload window: `Ctrl+Shift+P` → "Developer: Reload Window"

Settings already configured in `.vscode/settings.json`

## Troubleshooting Checklist

- [ ] Python 3.10+ installed? → `python3 --version`
- [ ] Virtual environment activated? → `which python`
- [ ] Correct Python path? → Should contain `.venv`
- [ ] Dependencies installed? → `pip list | grep -i tts`
- [ ] Numpy version compatible? → `pip show numpy`

## Need More Help?

See [README.md](README.md) for detailed documentation and troubleshooting. 