# Text-to-Speech Application

A Flask-based application that converts text to speech using the XTTS model, with support for Vietnamese language.

## Directory Structure

```
src/
├── app.py # Main Flask application and API endpoints
├── wrapper/
│ ├── model.py # XTTS model wrapper implementation
│ ├── helper.py # Helper functions for text processing and audio handling
│ └── constants.py # Constants used throughout the application
└── README.md # This file
TTS/ # A library for Text-to-Speech generation
```

## API Endpoints

### 1. `/paragraph_to_audio` (POST)

Converts a paragraph of text to audio.

**Request:**

```
{
    "text": "Your paragraph text here"
}
```

**Response:**

- Audio file (wav format)

### 2. `/paragraph_to_sentence_audios` (POST)

Converts a paragraph into separate audio files for each sentence.

**Request:**

```
{
    "text": "Your paragraph text here",
    "concatenate": true // Optional, defaults to false
}
```

**Response:**

- If `concatenate=true`: Single audio file with all sentences
- If `concatenate=false`: ZIP file containing individual audio files for each sentence

## Key Components

### XTTSWrapper (model.py)

The main wrapper class for the XTTS model that handles:

- Model initialization and configuration
- Text-to-speech inference
- Audio conditioning and processing

**Key Methods:**

- `__init__(model_dir, audio_path)`: Initialize the model
- `inference(text, language, **kwargs)`: Generate speech from text
- `get_conditioning_latents(audio_path)`: Get audio conditioning data

### Helper Functions (helper.py)

#### Text Processing

- `paragraph_to_audio`: Converts paragraphs to audio segments
- `text_to_audio`: Processes multi-paragraph text
- `normalize_text`: Text normalization utilities
- `convert_special_chars_to_dots`: Converts special characters to periods

#### Audio Processing

- `fine_tune_audio`: Audio processing and enhancement
- Audio concatenation and segmentation utilities

## Setup and Usage

1. **Prerequisites**

   - Python 3.8+
   - CUDA-capable GPU (recommended)

2. **Installation**

   ```bash
   pip install -r requirements.txt
   ```

3. **Model Setup**
   Fetch the model from Hugging Face into `models/viXTTS`:
   ```bash
   git lfs install && git clone https://huggingface.co/capleaf/viXTTS models/viXTTS
   # or
   pip install -U huggingface_hub && \
   huggingface-cli download capleaf/viXTTS --repo-type model --local-dir models/viXTTS
   ```
   Ensure `models/viXTTS` contains:
   - `config.json`, `vocab.json`
   - checkpoint files (e.g., `model.pth`)
   - reference audio (e.g., `vi_sample.wav`)
   
   Model card: [capleaf/viXTTS](https://huggingface.co/capleaf/viXTTS)

4. **Running the Application**
   ```bash
   python src/app.py
   ```

## Dependencies

- Flask: Web framework
- TTS: Text-to-Speech library
- MarkItDown: Convert various files to Markdown
- torch: Deep learning framework
- numpy: Numerical computing
- scipy: Scientific computing
- librosa: Audio processing

## Configuration

### Model Parameters

- Temperature: 0.3 (default)
- Length Penalty: 1.0 (default)
- Repetition Penalty: 10.0 (default)
- Top K: 30 (default)
- Top P: 0.85 (default)

### Audio Settings

- Sample Rate: 22050 Hz (default)
- Output Format: WAV

## Notes

- The application is optimized for Vietnamese language
- Audio files are temporarily stored in the `output` directory
- Regular cleanup of the output directory is recommended
- The model requires significant GPU memory for optimal performance

## Error Handling

The application includes error handling for:

- Invalid file uploads
- Missing text input
- Model initialization failures
- Audio processing errors

## Contributing

Feel free to submit issues and enhancement requests!
