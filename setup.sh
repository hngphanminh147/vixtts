#!/bin/bash
set -e  # Exit on error

echo "=========================================="
echo "ViXTTS Project Setup Script"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
    print_error "Python 3.10+ required. Found: $PYTHON_VERSION"
    exit 1
fi
print_success "Python $PYTHON_VERSION found"

# Remove existing venv if present
if [ -d ".venv" ]; then
    print_warning "Removing existing virtual environment..."
    rm -rf .venv
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv .venv
print_success "Virtual environment created"

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source .venv/bin/activate

# Verify activation
PYTHON_PATH=$(which python)
if [[ "$PYTHON_PATH" != *".venv"* ]]; then
    print_error "Virtual environment activation failed!"
    print_error "Expected: */vixtts/.venv/bin/python"
    print_error "Got: $PYTHON_PATH"
    exit 1
fi
print_success "Virtual environment activated: $PYTHON_PATH"

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
print_success "pip upgraded to $(pip --version | awk '{print $2}')"

# Check if requirements_no_tts.txt exists
if [ ! -f "requirements_no_tts.txt" ]; then
    print_warning "requirements_no_tts.txt not found, creating it..."
    grep -v "^TTS==" requirements.txt > requirements_no_tts.txt
    sed -i 's/numpy==1.26.4/numpy>=1.24.3/' requirements_no_tts.txt
    print_success "requirements_no_tts.txt created"
fi

# Install dependencies
echo ""
echo "Installing dependencies (this may take several minutes)..."
pip install -r requirements_no_tts.txt
print_success "Dependencies installed"

# Check if TTS folder exists and install
if [ -d "TTS" ]; then
    echo ""
    echo "Installing TTS from local folder..."
    
    # Update TTS requirements if needed
    if grep -q "numpy==1.22.0;python_version" TTS/requirements.txt 2>/dev/null; then
        print_warning "Updating TTS numpy requirement..."
        sed -i 's/numpy==1.22.0;python_version<="3.10"/numpy>=1.24.3/' TTS/requirements.txt
    fi
    
    pip install -e ./TTS
    print_success "TTS installed from local folder"
else
    echo ""
    print_warning "TTS folder not found, cloning from remote repository..."
    if ! command -v git >/dev/null 2>&1; then
        print_error "git is required to clone the TTS repository. Please install git and re-run."
        exit 1
    fi
    GIT_URL="https://github.com/hngphanminh147/TTS"
    echo "Cloning $GIT_URL into $(pwd)/TTS ..."
    if [ -d "TTS" ]; then
        print_warning "TTS directory appeared during setup; proceeding with local install."
    else
        git clone --depth 1 "$GIT_URL" TTS || { print_error "Failed to clone TTS repository."; exit 1; }
        print_success "Cloned TTS repository"
    fi

    # Update TTS requirements if needed (post-clone)
    if grep -q "numpy==1.22.0;python_version" TTS/requirements.txt 2>/dev/null; then
        print_warning "Updating TTS numpy requirement..."
        sed -i 's/numpy==1.22.0;python_version<="3.10"/numpy>=1.24.3/' TTS/requirements.txt
    fi

    echo "Installing TTS from cloned folder..."
    pip install -e ./TTS
    print_success "TTS installed from cloned repository"
fi

# Verify installation
echo ""
echo "Verifying installation..."
python -c "import numpy; print(f'numpy: {numpy.__version__}')" 2>/dev/null && print_success "numpy imported successfully"
python -c "import torch; print(f'torch: {torch.__version__}')" 2>/dev/null && print_success "torch imported successfully"

if [ -d "TTS" ]; then
    python -c "import TTS; print(f'TTS: {TTS.__version__}')" 2>/dev/null && print_success "TTS imported successfully"
fi

# Final instructions
echo ""
echo "=========================================="
print_success "Setup completed successfully!"
echo "=========================================="
echo ""
echo "To activate the virtual environment, run:"
echo "  source .venv/bin/activate"
echo ""
echo "To verify your Python path:"
echo "  which python"
echo "  (should show: $(pwd)/.venv/bin/python)"
echo ""
echo "To start development:"
echo "  python src/main.py"
echo "" 