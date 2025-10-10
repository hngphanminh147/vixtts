# Safe Model Wrapper

This module provides a fault-tolerant wrapper for TTS models that prevents application crashes when the underlying model changes or fails.

## Features

- **Fault Tolerance**: Handles model loading failures, inference errors, and configuration issues
- **Fallback Mechanisms**: Generates silence audio when the model fails
- **Retry Logic**: Automatically retries failed operations with configurable delays
- **Health Monitoring**: Provides comprehensive health status and error tracking
- **Model Recovery**: Can reload models after failures
- **Logging**: Detailed logging for debugging and monitoring

## Quick Start

### Basic Usage

```python
from src.wrapper import create_model_wrapper

# Create a safe model wrapper (default)
model = create_model_wrapper(
    model_dir="path/to/model",
    audio_path="path/to/reference/audio.wav",
    safe=True  # Enable safety features
)

# Perform inference
result = model.inference("Hello world", "en")

# Check if fallback was used
if result.get("fallback", False):
    print("Used fallback audio due to model issues")
else:
    print("Successfully generated audio")
```

### Advanced Usage

```python
from src.wrapper import SafeModelWrapper

# Create with custom configuration
model = SafeModelWrapper(
    model_dir="path/to/model",
    audio_path="path/to/reference/audio.wav",
    max_retries=5,
    retry_delay=2.0,
    enable_fallback=True
)

# Check model health
health = model.get_health_status()
print(f"Model state: {health['state']}")
print(f"Error count: {health['error_count']}")

# Perform inference with custom parameters
result = model.inference(
    text="Hello world",
    language="en",
    temperature=0.7,
    top_k=50
)
```

## API Reference

### SafeModelWrapper

#### Constructor

```python
SafeModelWrapper(
    model_dir: str,
    audio_path: str,
    max_retries: int = 3,
    retry_delay: float = 1.0,
    enable_fallback: bool = True
)
```

**Parameters:**
- `model_dir`: Path to the model directory
- `audio_path`: Path to the reference audio file
- `max_retries`: Maximum number of retry attempts
- `retry_delay`: Delay between retry attempts (seconds)
- `enable_fallback`: Whether to enable fallback mechanisms

#### Methods

##### `inference(text: str, language: str, **kwargs) -> Dict[str, Any]`

Perform inference with error handling and fallback mechanisms.

**Parameters:**
- `text`: Text to synthesize
- `language`: Language code (e.g., "en", "vi")
- `**kwargs`: Additional inference parameters

**Returns:**
- Dictionary containing:
  - `wav`: Audio data as numpy array
  - `fallback`: Boolean indicating if fallback was used
  - `error`: Error message if fallback was used
  - `timestamp`: Timestamp of the operation

##### `get_health_status() -> Dict[str, Any]`

Get comprehensive health status of the model.

**Returns:**
- Dictionary containing:
  - `state`: Current model state
  - `error_count`: Number of errors encountered
  - `last_error`: Last error message
  - `last_successful_inference`: Timestamp of last successful inference
  - `model_loaded`: Whether model is loaded
  - `config_loaded`: Whether config is loaded
  - `conditioning_available`: Whether conditioning latents are available
  - `cuda_available`: Whether CUDA is available
  - `fallback_enabled`: Whether fallback is enabled

##### `get_state() -> ModelState`

Get the current model state.

**Returns:**
- `ModelState` enum value

##### `reload_model() -> bool`

Reload the model from disk.

**Returns:**
- `True` if reload was successful, `False` otherwise

### Factory Functions

#### `create_model_wrapper(model_dir: str, audio_path: str, safe: bool = True, **kwargs)`

Factory function to create a model wrapper with optional safety features.

**Parameters:**
- `model_dir`: Path to the model directory
- `audio_path`: Path to the reference audio file
- `safe`: Whether to use the safe wrapper (default: True)
- `**kwargs`: Additional arguments for the wrapper

**Returns:**
- `XTTSWrapper` or `SafeModelWrapper` instance

## Model States

The wrapper tracks the model state using the `ModelState` enum:

- `UNINITIALIZED`: Model not yet initialized
- `LOADING`: Model is being loaded
- `READY`: Model is ready for inference
- `ERROR`: Model encountered an error
- `DEGRADED`: Model is in degraded mode (fallback enabled)

## Error Handling

The wrapper handles various types of errors:

1. **Model Loading Errors**: File not found, invalid configuration, etc.
2. **Inference Errors**: GPU memory issues, model corruption, etc.
3. **Configuration Errors**: Missing files, invalid parameters, etc.
4. **Runtime Errors**: CUDA errors, memory allocation failures, etc.

## Fallback Mechanisms

When the model fails, the wrapper can:

1. **Generate Silence**: Create silent audio of configurable length
2. **Retry Operations**: Automatically retry failed operations
3. **Model Reload**: Attempt to reload the model from disk
4. **Graceful Degradation**: Continue operation with reduced functionality

## Logging

The wrapper provides comprehensive logging:

```python
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

# The wrapper will log:
# - Model initialization progress
# - Inference attempts and results
# - Error conditions and recovery attempts
# - Fallback usage
```

## Integration with Helper Functions

The safe wrapper integrates seamlessly with existing helper functions:

```python
from src.wrapper import create_model_wrapper, paragraph_to_audio

# Create safe model
model = create_model_wrapper("path/to/model", "path/to/audio.wav", safe=True)

# Use with paragraph processing
paragraph = "This is a test paragraph. It has multiple sentences."
audio_map = paragraph_to_audio(model, paragraph)

# Check results
for key, audio in audio_map.items():
    if audio.shape[0] == 24000:  # Fallback audio length
        print(f"Segment {key} used fallback audio")
    else:
        print(f"Segment {key} generated successfully")
```

## Best Practices

1. **Always use the safe wrapper** for production applications
2. **Monitor model health** regularly using `get_health_status()`
3. **Handle fallback cases** appropriately in your application logic
4. **Configure appropriate retry settings** based on your use case
5. **Enable logging** for debugging and monitoring
6. **Test error scenarios** to ensure your application handles them gracefully

## Example: Complete Application

```python
import logging
from src.wrapper import create_model_wrapper

# Setup logging
logging.basicConfig(level=logging.INFO)

def process_text(text: str, model_dir: str, audio_path: str):
    """Process text with fault-tolerant TTS."""
    
    # Create safe model wrapper
    model = create_model_wrapper(
        model_dir=model_dir,
        audio_path=audio_path,
        safe=True,
        max_retries=3,
        retry_delay=1.0
    )
    
    # Check initial health
    health = model.get_health_status()
    if health['state'] != 'ready':
        print(f"Model not ready: {health['state']}")
        return None
    
    # Process text
    try:
        result = model.inference(text, "en")
        
        if result.get("fallback", False):
            print("⚠️  Used fallback audio")
            return None
        else:
            print("✅ Successfully generated audio")
            return result["wav"]
            
    except Exception as e:
        print(f"❌ Processing failed: {e}")
        return None

# Usage
audio = process_text("Hello world", "path/to/model", "path/to/audio.wav")
if audio is not None:
    # Save or process the audio
    pass
```

## Troubleshooting

### Common Issues

1. **Model not loading**: Check file paths and permissions
2. **CUDA errors**: Ensure GPU memory is available
3. **Configuration errors**: Verify model files are complete
4. **Fallback always used**: Check model health and error logs

### Debug Mode

Enable debug logging for detailed information:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Health Monitoring

Regularly check model health:

```python
health = model.get_health_status()
if health['error_count'] > 10:
    print("High error count, consider reloading model")
    model.reload_model()
```
