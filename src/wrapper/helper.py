import librosa
import numpy as np

import re
from num2words import num2words

from .model import XTTSWrapper

from wrapper.constants import DEFAULT_SAMPLE_RATE, DEFAUL_OUTPUT_FILE_NAME, DEFAULT_OUTPUT_FILE_LENGTH

import os


def normalize_numbers(text: str):
    """Converts numerical digits in text to their Vietnamese word representation.

    Args:
        text (str): Input text containing numbers to convert.

    Returns:
        str: Text with all numbers converted to Vietnamese words.

    Example:
        >>> normalize_numbers("Tôi có 2 con mèo")
        "Tôi có hai con mèo"
    """

    # Define patterns for different types of numbers
    patterns = [
        # Cardinal numbers (1, 2, 3, ...)
        (r"(\d+)", lambda m: num2words(int(m.group(1)), lang='vi')),
        # Decimal numbers (1.5, 2.7, ...)
        (r"(\d+)\.(\d+)", lambda m: num2words(float(m.group(0)), lang='vi')),
    ]

    # Apply patterns sequentially
    for pattern, replacement_func in patterns:
        text = re.sub(pattern, replacement_func, text)

    return text


def trim_silence(audio_data, sr, threshold=0.01, frame_length=2048, hop_length=512, keep_silence_duration=0.2):
    """Trims silence from the end of an audio signal, keeping some silence.

    Args:
        audio_data (np.array): The audio signal as a NumPy array.
        sr (int): The sample rate of the audio signal.
        threshold (float): The threshold below which audio is considered silence.
        frame_length (int): The length of the frames used to compute the RMS energy.
        hop_length (int): The number of samples between successive frames.
        keep_silence_duration (float): The duration of silence to keep at the end (in seconds).
            Default: 0.2 seconds (reduced from 0.8 to fix stretched audio for short text)

    Returns:
        np.array: The trimmed audio signal as a NumPy array.
    """

    # Compute the RMS energy of the audio signal.
    rms = librosa.feature.rms(
        y=audio_data, frame_length=frame_length, hop_length=hop_length)[0]

    # Find the last frame where the RMS energy is above the threshold.
    last_frame = np.where(rms > threshold)[0][-1]

    # Convert the frame index to a sample index.
    last_sample = librosa.frames_to_samples(last_frame, hop_length=hop_length)

    # Calculate the number of samples to keep as silence.
    keep_silence_samples = int(keep_silence_duration * sr)

    # Adjust the last sample index to keep some silence.
    trimmed_audio_data = audio_data[:min(
        last_sample + keep_silence_samples, len(audio_data))]

    return trimmed_audio_data


def normalize_text(text: str):
    """Applies all text normalization steps to prepare for TTS processing.

    Currently includes:
    - Number normalization

    Args:
        text (str): Raw input text to normalize.

    Returns:
        str: Normalized text ready for TTS processing.
    """
    # Convert symbols to (.)

    text = normalize_numbers(text)

    return text


def fine_tune_audio(audio, **kwargs):
    """Applies post-processing adjustments to the generated audio.

    Currently includes:
    - Silence trimming

    Args:
        audio (np.array): Raw audio data from TTS model.
        **kwargs: Additional arguments passed to processing functions.
            - sample_rate: Sample rate (defaults to DEFAULT_SAMPLE_RATE)
            - keep_silence_duration: Silence to keep at end in seconds (defaults to env var or 0.2)

    Returns:
        np.array: Processed audio data.
    """

    sample_rate = kwargs.get("sample_rate", DEFAULT_SAMPLE_RATE)

    # Get keep_silence_duration from env or use 0.2 as default (better for short text)
    keep_silence = float(os.getenv('XTTS_KEEP_SILENCE_DURATION', '0.2'))
    # audio_duration = len(audio) / sample_rate
    # if audio_duration < 2.0:
    #     keep_silence = 0.1
    # elif audio_duration < 5.0:
    #     keep_silence = 0.15
    # else:
    #     keep_silence = 0.2

    # keep_silence = float(
    #     os.getenv('XTTS_KEEP_SILENCE_DURATION', str(keep_silence)))

    audio = trim_silence(audio, sr=sample_rate,
                         keep_silence_duration=keep_silence)

    return audio


def split_into_sentences(paragraph: str, max_len: int = 250, language: str = "vi"):
    """Split text into sentences and further chunk long sentences for model limits.

    - Handles unicode ellipsis (… ) and triple dots (...).
    - Splits on [.!?] and ellipses, allowing closing quotes/parens before whitespace.
    - Preserves punctuation with the sentence/chunk.
    - For sentences exceeding max_len, further splits at soft boundaries:
      commas, semicolons, colons, dashes, and common Vietnamese conjunctions.
    """
    if not paragraph:
        return []

    text = paragraph.strip()

    # Normalize unicode ellipsis to three dots and protect ellipses with a token
    text = text.replace("…", "...")
    ELLIPSIS_TOKEN = "⟦ELLIPSIS⟧"
    text = text.replace("...", ELLIPSIS_TOKEN)

    # Base sentence split boundaries
    boundary_pattern = r"(?:" + re.escape(ELLIPSIS_TOKEN) + \
        r"|[.!?])(?:[\"'”’)\]]*)\s+"

    base_sentences = []
    start = 0
    for match in re.finditer(boundary_pattern, text):
        end = match.end()
        chunk = text[start:end].strip()
        if chunk:
            base_sentences.append(chunk.replace(ELLIPSIS_TOKEN, "..."))
        start = end
    tail = text[start:].strip()
    if tail:
        base_sentences.append(tail.replace(ELLIPSIS_TOKEN, "..."))

    # Helper: finalize a buffer as a chunk
    def flush(buffer_tokens):
        chunk = " ".join(buffer_tokens).strip()
        return chunk if chunk else None

    # Secondary split for long sentences
    chunks = []
    # Soft delimiters and VN conjunction words for nicer splits
    # comma, semicolon, colon, hyphen, en/em dash
    soft_delims_regex = r"([,;:\-\u2013\u2014])"
    vi_conj = set(["và", "nhưng", "hoặc", "rồi", "thì", "là", "nên",
                  "vì", "bởi", "tuy", "dù"]) if language == "vi" else set()

    for sent in base_sentences:
        sentence = sent.strip()
        if len(sentence) <= max_len:
            chunks.append(sentence)
            continue

        # Pre-split on soft delimiters while keeping them
        parts = re.split(soft_delims_regex, sentence)
        # Re-attach delimiters to preceding tokens
        merged = []
        i = 0
        while i < len(parts):
            token = parts[i]
            if i + 1 < len(parts) and re.fullmatch(soft_delims_regex, parts[i + 1] or ""):
                token = (token or "") + (parts[i + 1] or "")
                i += 2
            else:
                i += 1
            if token:
                merged.append(token.strip())

        # Greedy pack tokens up to max_len, prefer to break after delimiters or conjunctions
        buffer = []
        current_len = 0

        def smart_can_add(tok, cur_len):
            return (cur_len + (1 if cur_len > 0 else 0) + len(tok)) <= max_len

        for tok in merged:
            tok_stripped = tok.strip()
            if not tok_stripped:
                continue

            if smart_can_add(tok_stripped, current_len):
                buffer.append(tok_stripped)
                current_len += (1 if current_len > 0 else 0) + \
                    len(tok_stripped)
                continue

            # Try to move last buffer token to next chunk to keep punctuation together if needed
            if buffer:
                last = buffer[-1]
                last_word = last.lower().strip(".,;:-—– ")
                if last_word in vi_conj or (len(last) == 1 and last in ",;:-"):
                    # pop the last soft boundary for next chunk
                    buffer.pop()

            out = flush(buffer)
            if out:
                chunks.append(out)

            buffer = [tok_stripped]
            current_len = len(tok_stripped)

        out = flush(buffer)
        if out:
            chunks.append(out)

    return chunks

# refine-inference-param-cal1.md


def calculate_inference_params(text: str):
    """Calculate optimal inference parameters for xTTS based on text characteristics."""
    text = text.strip()
    text_len = len(text)
    punctuation_count = sum(1 for c in text if c in ',.!?;:—-')
    punctuation_density = punctuation_count / max(text_len, 1)
    words = text.lower().split()
    unique_words = len(set(words))
    word_count = len(words)
    word_diversity = unique_words / max(word_count, 1)

    params = {}

    # --- Handle very short sentences ---
    if word_count < 15:
        # Reduce speed to avoid stretching
        params['speed'] = 1.04
        # params['speed'] = 1.0
        # Prevent model from "stretching"
        params['length_penalty'] = 0.75
        params['temperature'] = 0.8
        params['repetition_penalty'] = 1.5
        params['enable_text_splitting'] = False
        return params

    # --- Adjust for medium/long sentences ---
    # Speed control
    if punctuation_density > 0.05:
        # Reduce speed if there are many punctuation marks
        params['speed'] = 0.98
    elif text_len > 200:
        params['speed'] = 0.95
    else:
        params['speed'] = 1.0

    # Length penalty (prevent over/under generation)
    if text_len < 80:
        params['length_penalty'] = 1.0
    elif text_len > 200:
        params['length_penalty'] = 1.1
    else:
        params['length_penalty'] = 1.05

    # Temperature
    if word_diversity > 0.7:
        params['temperature'] = 0.75
    elif word_diversity < 0.5:
        params['temperature'] = 0.7
    else:
        params['temperature'] = 0.72

    # Repetition penalty
    if word_count > 50 and word_diversity < 0.6:
        params['repetition_penalty'] = 4.0
    elif word_count > 30:
        params['repetition_penalty'] = 3.0
    else:
        params['repetition_penalty'] = 2.0

    # Enable sentence-based splitting, not length-based
    params['enable_text_splitting'] = False

    return params


def split_text_smart(text: str):
    """
    Split text by sentence boundaries using punctuation, 
    avoiding splitting mid-clause.
    """
    # Split by '.', '!', '?', ';', ':' but keep punctuation
    sentences = re.split(r'(?<=[.!?;:])\s+', text.strip())
    sentences = [s for s in sentences if s]
    return sentences


def paragraph_to_audio(model: XTTSWrapper, paragraph: str, language: str = "vi"):
    """Converts a paragraph of text into a dictionary of audio segments for each sentence.

    Args:
        model (XTTSWrapper): The XTTS model wrapper instance to use for inference.
        paragraph (str): A paragraph of text to convert to speech.

    Returns:
        dict: A dictionary mapping sentence identifiers to audio data.
              Keys are formatted as "index_sentence_text" and values are numpy arrays
              containing the audio data for each sentence.

    Note:
        - Splits paragraph into sentences by period
        - Normalizes each sentence before processing
        - Returns a dictionary where each key is "index_text" and value is the audio data
        - Audio data is processed and fine-tuned (silence trimming, etc.)
    """

    sentences = split_into_sentences(paragraph, language=language)
    audio_map = {}
    for index, sentence in enumerate(sentences):
        print(f"Processing Sentence {index}: {sentence}")
        text = sentence.strip()
        if not text:
            continue

        # Normalize text before procesing
        text = normalize_text(text)

        # Calculate inference parameters based on text characteristics
        # inference_params = calculate_inference_params(text)
        inference_params = calculate_inference_params(text)

        out_wav = model.inference(
            text=text,
            language=language,
            **inference_params
        )

        # out_wav = model.inference(
        #     text=text,
        #     language=language,
        # )

        # Fine tune the audio output
        tuned_audio = fine_tune_audio(
            out_wav["wav"], sample_rate=DEFAULT_SAMPLE_RATE)

        # Map the audio to its corresponding text
        audio_name = f"{index}_{sentence[:DEFAULT_OUTPUT_FILE_LENGTH]}"
        audio_map[audio_name] = tuned_audio

    return audio_map
