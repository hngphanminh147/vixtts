import torch
import os
from dotenv import load_dotenv

from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts

# Load environment variables from .env file
load_dotenv()


class XTTSWrapper:
    def __init__(self, model_dir: str, audio_path: str):
        """
        Initializes the XTTSWrapper with the given model directory.

        Args:
            model_dir (str): The path to the directory containing the XTTS model and config.
        """
        self.config = XttsConfig()
        self.config.load_json(f"{model_dir}/config.json")
        self.model = Xtts.init_from_config(self.config)
        self.model.load_checkpoint(
            self.config, checkpoint_dir=model_dir, vocab_path=f"{model_dir}/vocab.json")
        self.model.eval()

        if torch.cuda.is_available():
            self.model.cuda()

        # Load inference parameters from environment variables with model config as fallback
        self.temperature = float(os.getenv(
            'XTTS_TEMPERATURE', self.config.temperature))
        self.length_penalty = float(os.getenv(
            'XTTS_LENGTH_PENALTY', self.config.length_penalty))
        self.repetition_penalty = float(os.getenv(
            'XTTS_REPETITION_PENALTY', self.config.repetition_penalty))
        self.top_k = int(os.getenv('XTTS_TOP_K', self.config.top_k))
        self.top_p = float(os.getenv(
            'XTTS_TOP_P', self.config.top_p))

        print(f"XTTS Model Parameters:")
        print(f"  Temperature: {self.temperature}")
        print(f"  Length Penalty: {self.length_penalty}")
        print(f"  Repetition Penalty: {self.repetition_penalty}")
        print(f"  Top K: {self.top_k}")
        print(f"  Top P: {self.top_p}")

        self.get_conditioning_latents(audio_path)

    def get_config(self):
        return self.config

    def get_conditioning_latents(self, audio_path: str):
        """
        Gets the conditioning latents for the given audio path.

        Args:
            audio_path (str): The path to the audio file.

        Returns:
            Tuple[torch.Tensor, torch.Tensor]: The GPT conditioning latent and speaker embedding.
        """

        self.model_gpt_cond_latent, self.model_speaker_embedding = self.model.get_conditioning_latents(
            audio_path=audio_path,
            gpt_cond_len=int(self.model.config.gpt_cond_len),
            max_ref_length=int(self.model.config.max_ref_len),
            sound_norm_refs=bool(self.model.config.sound_norm_refs),
        )

        return self.model_gpt_cond_latent, self.model_speaker_embedding

    def inference(self, text: str, language: str, **kwargs):
        """
        Performs inference on the given text.

        Args:
            text (str): The text to synthesize.
            language (str): The language of the text.
            **kwargs: Additional keyword arguments for the inference.

        Returns:
            Dict[str, Any]: The inference results, including the synthesized audio as a NumPy array under the key "wav".
        """

        # Use default values if not provided in kwargs
        # torch.Tensor
        gpt_cond_latent = kwargs.pop(
            "gpt_cond_latent", self.model_gpt_cond_latent)
        # torch.Tensor
        speaker_embedding = kwargs.pop(
            "speaker_embedding", self.model_speaker_embedding)
        temperature = kwargs.pop("temperature", self.temperature)
        length_penalty = kwargs.pop(
            "length_penalty", self.length_penalty)
        repetition_penalty = kwargs.pop(
            "repetition_penalty", self.repetition_penalty)
        top_k = kwargs.pop("top_k", self.top_k)
        top_p = kwargs.pop("top_p", self.top_p)

        # Additional parameters that significantly affect quality
        # Load from environment variables with defaults
        do_sample = kwargs.pop("do_sample", os.getenv(
            'XTTS_DO_SAMPLE', 'True').lower() == 'true')
        speed = kwargs.pop("speed", float(os.getenv('XTTS_SPEED', '1.0')))
        enable_text_splitting = kwargs.pop(
            "enable_text_splitting", os.getenv('XTTS_ENABLE_TEXT_SPLITTING', 'True').lower() == 'true')

        print(
            f"Inference Parameters: temperature: {temperature}, length_penalty: {length_penalty}, repetition_penalty: {repetition_penalty}, top_k: {top_k}, top_p: {top_p}, do_sample: {do_sample}, speed: {speed}, enable_text_splitting: {enable_text_splitting}")

        return self.model.inference(
            text=text,
            language=language,
            gpt_cond_latent=gpt_cond_latent,
            speaker_embedding=speaker_embedding,
            temperature=temperature,
            length_penalty=length_penalty,
            repetition_penalty=repetition_penalty,
            top_k=top_k,
            top_p=top_p,
            do_sample=do_sample,
            speed=speed,
            enable_text_splitting=enable_text_splitting,
            **kwargs,
        )
