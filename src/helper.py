import librosa
import numpy as np

import re
from num2words import num2words

from wrapper.constants import DEFAULT_SAMPLE_RATE, DEFAUL_OUTPUT_FILE_NAME

from wrapper.model import XTTSWrapper


def normalize_numbers(text: str):
    """Normalizes numbers in text to their textual representation.
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


def trim_silence(audio_data, sr, threshold=0.01, frame_length=2048, hop_length=512, keep_silence_duration=0.8):
    """Trims silence from the end of an audio signal, keeping some silence.

    Args:
        audio_data: The audio signal as a NumPy array.
        sr: The sample rate of the audio signal.
        threshold: The threshold below which audio is considered silence.
        frame_length: The length of the frames used to compute the RMS energy.
        hop_length: The number of samples between successive frames.
        keep_silence_duration: The duration of silence to keep at the end (in seconds).

    Returns:
        The trimmed audio signal as a NumPy array.
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
    text = normalize_numbers(text)

    return text


def fine_tune_audio(audio, **kwargs):
    sample_rate = kwargs.get("gpt_cond_latent", DEFAULT_SAMPLE_RATE)
    audio = trim_silence(audio, sr=sample_rate)

    return audio


def paragraph_to_audio(paragraph, wrapper: XTTSWrapper):
    sentences = paragraph.split(".")
    audio_list = []
    for index, sentence in enumerate(sentences):
        text = sentence.strip()
        if not text:
            continue

        # Normalize text before procesing
        text = normalize_text(text)

        print(f"Processing Sentence {index}: {text}")
        out_wav = wrapper.inference(
            text=text,
            language="vi",
            # gpt_cond_latent=gpt_cond_latent,
            # speaker_embedding=speaker_embedding,
            # temperature=0.3,
            # length_penalty=1.0,
            # repetition_penalty=10.0,
            # top_k=30,
            # top_p=0.85,
        )

        # Fine tune the audio output
        tuned_audio = fine_tune_audio(
            out_wav["wav"],
            sample_rate=DEFAULT_SAMPLE_RATE
        )

        # Append the trimmed audio to the list
        audio_list.append(tuned_audio)

    result = np.concatenate(audio_list)

    return result


# def text_to_audio(text, file_name=DEFAUL_OUTPUT_FILE_NAME):
#     paragraphs = text.split("\n\n")
#     audio_list = []
#     for index, paragraph in enumerate(paragraphs):
#         print(f"Processing Paragraph {index + 1}:")
#         audio = paragraph_to_audio(paragraph)
#         # Append audio for each paragraph
#         audio_list.append(audio)
#         result = np.concatenate(audio_list)

#     return result
