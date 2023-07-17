import torch
from transformers import AutoProcessor
from transformers import MusicgenForConditionalGeneration

from . import *


class AudioCraftModel:
    Small  = "small"
    Medium = "medium"
    Melody = "melody"
    Large  = "large"

class DepthMusic:
    def __init__(self, model: AudioCraftModel):
        self.DEVICE = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.MODEL_NAME = f"facebook/musicgen-{model}"

        # Initialize models
        self.TRANSFORMERS_PROCESSOR = AutoProcessor.from_pretrained(self.MODEL_NAME)
        self.TRANSFORMERS_MODEL     = MusicgenForConditionalGeneration.from_pretrained(self.MODEL_NAME)
        self.TRANSFORMERS_MODEL.to(self.DEVICE)

        # Chunks of recent audio
        self.chunks = []

    # # Properties

    @property
    def sample_rate(self):
        return self.TRANSFORMERS_MODEL.config.audio_encoder.sampling_rate

    @property
    def frame_rate(self):
        return self.TRANSFORMERS_MODEL.config.audio_encoder.frame_rate

    # # Unit conversion

    def tokens_to_seconds(self, tokens: int) -> float:
        return tokens / self.frame_rate

    def seconds_to_tokens(self, seconds: float) -> int:
        return int(seconds * self.frame_rate)

    # # Main functions

    @contextmanager
    def write_audio(self, name: str="output.opus"):
        ffmpeg = Popen([
            "ffmpeg",
            "-loglevel", "error",
            "-hide_banner",
            "-nostats",
            "-f", "f32le",
            "-ar", str(self.sample_rate),
            "-ac", "2",
            "-i", "pipe:0",
            "-c:a", "libopus",
            "-b:a", "96k",
            # dynaudionorm
            "-af", "dynaudnorm=f=150:g=15",
            name,
            "-y",
        ], stdin=PIPE)

        yield ffmpeg.stdin.write

        ffmpeg.stdin.close()

    # # Generation workflows

    def generate(self,
        # Transformers Processor
        text: str,
        audio: numpy.ndarray=None,
        duration: float=10,
        remove_audio: bool=True,
        extrapolate_tokens=1.0,

        # Transformers Model
        temperature: float=1.0,
        guidance_scale: float=5.0,
    ):
        # Create inputs configuration
        inputs = self.TRANSFORMERS_PROCESSOR(
            text=text,
            audio=audio,
            padding=True,
            return_tensors="pt",
            sampling_rate=self.sample_rate,
        )
        inputs.to(self.DEVICE)

        # Generate audio ()
        audio_values = self.TRANSFORMERS_MODEL.generate(
            **inputs,
            max_new_tokens=self.seconds_to_tokens(duration * extrapolate_tokens),
            # do_sample=True,
            temperature=temperature,
            # guidance_scale=guidance_scale,
        )

        # Get raw data generated
        data = audio_values.cpu()[0, 0].numpy()

        # Remove initial audio length from data
        if remove_audio and (audio is not None):
            data = data[len(audio):]

        # Remove the extra extrapolated per cent of data, if extrapolate_tokens=1.4
        # then length should go until 1/extrapolate_tokens
        data = data[:int(len(data)/extrapolate_tokens)]

        return data

    def crossfade(self, data: list, length: int):
        """Crossfade the start and end of the 1D data, length in samples"""
        data = numpy.array(data)
        data[:length ] *= numpy.linspace(0, 1, length)
        data[-length:] *= numpy.linspace(1, 0, length)
        return data

    def LR(self, last_n: int=None):
        L, R = [], []
        for chunk in self.chunks[-(last_n or 0):]:
            L += list(self.crossfade(chunk[0], 100))
            R += list(self.crossfade(chunk[1], 100))
        return numpy.array(L).reshape(-1), numpy.array(R).reshape(-1)

    def L(self, last_n: int=None): return self.LR(last_n)[0]
    def R(self, last_n: int=None): return self.LR(last_n)[1]

    def normalize(self, data: numpy.ndarray):
        return data #/ numpy.max(numpy.abs(data))

    def main(self,
        prompt: str,
        duration=30,
        initial_audio_size=3,
        context=10,
        diverge=1,
        imagine=1,
        mid=0.4,
    ):
        """
        Generate audio in a loop, with a context of previous audio
        - prompt: Initial text prompt
        - initial_audio_size: Seconds of initial audio to generate for mono reference
        - context: Seconds of context to keep in memory when generating new audio
        - diverge: For every multiple of diverge seconds glue the left and right audio together again
        - imagine: Imagine this many seconds into the future when gluing channels
        """

        # Generate initial audio
        print("Generating initial audio...")
        latest = self.generate(text=f"{prompt} intro", duration=initial_audio_size)
        self.chunks.append((latest, latest))

        for i in itertools.count(1):

            # Generate left and right audio, add to chunks
            left  = self.generate(text=prompt, audio=latest, duration=imagine, extrapolate_tokens=imagine/diverge)
            right = self.generate(text=prompt, audio=latest, duration=imagine, extrapolate_tokens=imagine/diverge)
            self.chunks.append((self.normalize(left), self.normalize(right)))

            # Mono of last N chunks that sums up to context duration
            N = int(context/diverge)
            latest = self.normalize(self.L(N) + self.R(N)) / 2

            # Check for duration
            time = self.L().shape[0] / self.sample_rate
            info(f"Generated [{time:.2f}/{duration:.2f}s] ({i} chunks)")

            if duration < time:
                break

        # # Calcualte final mix

        # Mono of LR
        mono = (self.L() + self.R())/2

        # Mix mono with LR separately ("mid side")
        mix = numpy.array([
            (self.L() * mid) + (1 - mid) * mono,
            (self.R() * mid) + (1 - mid) * mono,
        ])

        # Normalize mix
        return mix / numpy.max(numpy.abs(mix))

