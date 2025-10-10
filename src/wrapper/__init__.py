"""
Wrapper module for TTS models.

This module provides wrappers around TTS models that handle failures gracefully
and provide fallback mechanisms to prevent application crashes.

This module provides wrappers around TTS models that handle failures gracefully
and provide fallback mechanisms to prevent application crashes.
"""

from .model import XTTSWrapper
from .helper import paragraph_to_audio, normalize_text, fine_tune_audio
from .constants import DEFAULT_SAMPLE_RATE, DEFAUL_OUTPUT_FILE_NAME, DEFAULT_OUTPUT_FILE_LENGTH

__all__ = [
    'XTTSWrapper',
    'paragraph_to_audio',
    'normalize_text',
    'fine_tune_audio',
    'DEFAULT_SAMPLE_RATE',
    'DEFAUL_OUTPUT_FILE_NAME',
    'DEFAULT_OUTPUT_FILE_LENGTH'
]
