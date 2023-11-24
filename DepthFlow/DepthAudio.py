# isort: off
from . import *


class AudioCraftModel(BrokenEnum):
    Small  = "small"
    Medium = "medium"
    Melody = "melody"
    Large  = "large"

@attrs.define
class DepthAudioCraft:
    device: str = "cuda:0" if torch.cuda.is_available() else "cpu"
    model: AudioCraftModel = AudioCraftModel.Medium
    chunks: list = attrs.field(factory=list)

    # Internal objects
    transformers_processor: Any = None
    transformers_model:     Any = None

    def __attrs_post_init__(self):
        from transformers import AutoProcessor
        from transformers import MusicgenForConditionalGeneration

        self.transformers_processor = AutoProcessor.from_pretrained(f"facebook/musicgen-stereo-{self.model.value}")
        self.transformers_model     = MusicgenForConditionalGeneration.from_pretrained(f"facebook/musicgen-stereo-{self.model.value}")
        self.transformers_model.to(self.device)

    # Properties

    @property
    def sample_rate(self):
        return self.transformers_model.config.audio_encoder.sampling_rate

    @property
    def frame_rate(self):
        return self.transformers_model.config.audio_encoder.frame_rate

    # # Unit conversion

    def tokens_to_seconds(self, tokens: int) -> float:
        return tokens / self.frame_rate

    def seconds_to_tokens(self, seconds: float) -> int:
        return int(seconds * self.frame_rate)

    # # Audio processing

    def crossfade(self, data: numpy.ndarray, length: int):
        """Crossfade the start and end of the 1D data, length in samples"""
        for channel in range(data.shape[0]):
            data[channel][:length ] *= numpy.linspace(0, 1, length)
            data[channel][-length:] *= numpy.linspace(1, 0, length)
        return data

    def stereo_to_mono(self, data: numpy.ndarray):
        """Convert stereo audio to mono"""
        return (data[0] + data[1]) / 2

    def __generate__(self,
        prompt: str,
        context_chunks: int=2,
        chunk_duration: float=5,
        temperature: float=1.0,
        guidance_scale: float=5.0,
    ):
        audio = None
        crop  = 0

        # Get the last N chunks if available
        if (context := self.chunks[-context_chunks:]):
            audio = numpy.concatenate(context, axis=1)
            # Get only the last 20% of the audio
            audio = audio[:, -int(audio.shape[1] * 0.2):]
            crop  = audio.shape[1]

        # Create configuration for inputs
        inputs = self.transformers_processor(
            text=prompt,
            audio=audio,
            padding=False,
            return_tensors="pt",
            sampling_rate=self.sample_rate,
        )
        inputs.to(self.device)

        # Generate audio
        audio_values = self.transformers_model.generate(**inputs,
            max_new_tokens=self.seconds_to_tokens(chunk_duration),
            # temperature=temperature,
            # guidance_scale=guidance_scale,
        )

        # Get generated data and smooth the edges
        data = audio_values.cpu().numpy()[0][:, crop:]
        data = self.crossfade(data, 100)

        # Add to chunks
        self.chunks.append(data)

    def main(self,
        prompt: str,
        file_name: str="output.opus",
        duration: float=30,
        context_chunks: int=1,
        chunk_duration: float=5,
    ):
        total_chunks = int(duration / chunk_duration)

        with self.write_audio(file_name=file_name) as ffmpeg:
            for chunk in range(total_chunks):
                log.info(f"Generating chunk ({chunk+1}/{total_chunks})")

                # Generate chunk of audio
                self.__generate__(
                    prompt=prompt,
                    context_chunks=context_chunks,
                    chunk_duration=chunk_duration,
                )

                # Write to ffmpeg
                ffmpeg(self.chunks[-1].T.tobytes())

    @contextmanager
    def write_audio(self, file_name) -> Generator:
        ffmpeg = shell(
            "ffmpeg",
            "-loglevel", "error",
            "-hide_banner",
            "-nostats",
            "-f", "f32le",
            "-ar", self.sample_rate,
            "-ac", "2",
            "-i", "pipe:0",
            "-c:a", "libopus",
            "-b:a", "96k",
            # dynaudionorm
            "-af", "dynaudnorm=f=150:g=15",
            file_name,
            "-y",
            stdin=PIPE,
            Popen=True,
        )

        yield ffmpeg.stdin.write

        ffmpeg.stdin.close()

# audiocraft = DepthAudioCraft()
# audiocraft.main(
#     prompt="A chill, religious song with a soft piano melody, no beats, clean mix, gentle bass, no highs, harmonic, chords, atmospheric, no whitenose, no abrubt transitions, no ringing, short echoes and reverbs, no pads",
#     # prompt="A grand orchestral arrangement with thunderous percussion, epic brass fanfares, and soaring strings, creating a cinematic atmosphere fit for a heroic battle",
#     duration=600,
# )
