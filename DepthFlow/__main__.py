from DepthFlow import *


class DepthFlowGradio:
    def __init__(self):
        self.depthmusic = DepthMusic("small")

    def webui(self, share: bool=False):
        self.components = DotMap()

        with gradio.Blocks(title="DepthFlow") as self.gradio_interface:
            gradio.Markdown(f"DepthFlow WebUI Prototype - [GPU {torch.cuda.get_device_name()}] - [Torch {torch.__version__}]")

            with gradio.Tab("DepthVideo"):
                with gradio.Row():
                    self.components.parallax_imageA = gradio.Image(label="Image A")

                with gradio.Blocks():
                    self.components.parallax_duration     = gradio.Slider(label="Duration (seconds)", minimum=1, maximum=120, value=10, step=1, interactive=True)
                    self.components.parallax_fps          = gradio.Slider(label="FPS", minimum=1, maximum=120, value=60, step=1, interactive=True)
                    self.components.parallax_factor       = gradio.Slider(label="Parallax Factor", minimum=0, maximum=1, value=0.08, step=0.01, interactive=True)
                    self.components.parallax_camera_focus = gradio.Slider(label="Camera Focus", minimum=0, maximum=1, value=1, step=0.01, interactive=True)

                self.components.parallax_generate = gradio.Button("Generate")
                self.components.parallax_video    = gradio.Video(label="Generated Video", format="mp4")

            with gradio.Tab("DepthAudio"):
                gradio.Markdown('\n'.join([
                    "# Ideas:",
                    "- An 80s driving pop song with heavy drums and synth pads in the backgroun",
                    "- a light and cheerly EDM track, chorus, with syncopated drums, aery pads, and strong emotions bpm: 130",
                    "- A cheerful song with acoustic guitars with a lofi feel and a catchy melody, not fading away",
                    "- upbeat tropical house with a strong beat and a catchy melody, clean and short drums, no transitions, no whitenoise",
                    "- lofi slow bpm electro chill with organic samples and rhodes"
                ]))

                self.components.music_prompt   = gradio.Textbox(label="Music Prompt", value="lofi slow bpm electro chill with organic samples and rhodes")
                with gradio.Blocks():
                    # self.components.music_model              = gradio.Radio(["small", "medium", "melody", "large"], value="small", label="AudioCraft Model")
                    self.components.music_duration           = gradio.Slider(label="Duration (seconds)", minimum=1, maximum=120, value=10, step=0.5, interactive=True)
                    self.components.music_initial_audio_size = gradio.Slider(label="Initial Audio Size (seconds)", minimum=0, maximum=10, value=2, step=0.5, interactive=True)
                    self.components.music_context_length     = gradio.Slider(label="Context Length (seconds)", minimum=0, maximum=20, value=5, step=0.5, interactive=True)
                    self.components.music_diverge_every      = gradio.Slider(label="Diverge Every (seconds)", minimum=0, maximum=10, value=1, step=0.5, interactive=True)
                    self.components.music_imagine_overshoot  = gradio.Slider(label="Imagine Overshoot (seconds)", minimum=0, maximum=10, value=1, step=0.5, interactive=True)
                    self.components.music_mid                = gradio.Slider(label="Mid eq factor", minimum=0, maximum=1, value=0.4, step=0.01, interactive=True)

                self.components.music_generate = gradio.Button("Generate")
                self.components.music_output   = gradio.Audio(label="Generated Audio", type="filepath")

            # # Actions

            # Set of all components, identified by inputs[component]
            inputs = set(self.components.values())

            self.components.music_generate.click(self.generate_audio, inputs=inputs, outputs=self.components.music_output)
            self.components.parallax_generate.click(self.generate_parallax, inputs=inputs, outputs=self.components.parallax_video)

        # Launch interface
        self.gradio_interface.launch(
            share=share, # Generate public link
            inbrowser=True, # Open URL on default browser
            server_name="0.0.0.0" # Be available on local network
        )

    def fish_components(self, components):
        """
        Gradio needs inputs=List, outputs=List, so we convert every self.component.name to self.name as their value
        Requires sending inputs=set(self.components.values()) when adding event listeners. Call this before callable actions
        """
        for name, component in self.components.items():
            setattr(self, name, components[component])

    def generate_audio(self, components):
        self.fish_components(components)

        audio = self.depthmusic.main(
            prompt=self.music_prompt,
            duration=self.music_duration,
            initial_audio_size=self.music_initial_audio_size,
            context=self.music_context_length,
            diverge=self.music_diverge_every,
            imagine=self.music_imagine_overshoot,
        )
        sample_rate = int(self.depthmusic.sample_rate)

        # Return (sample_rate, audio)
        return (sample_rate, audio.T)

    def generate_parallax(self, components):
        self.fish_components(components)

        from PIL import Image

        # FIXME: Initializing DepthFlowGL on __init__ causes a segfault, something to do with Gradio threads ofc
        self.depthflowgl = DepthFlowGL()
        self.depthflowgl.init()

        # Input Path or URL
        self.depthflowgl.upload_texture(
            index=DepthFlowTextureIndex.A,
            image=Image.fromarray(self.parallax_imageA),
        )
        self.depthflowgl.upload_texture(
            index=DepthFlowTextureIndex.B,
            image="https://w.wallhaven.cc/full/85/wallhaven-85dv52.png"
        )

        initial_variables = DEPTHFLOW_DEFAULT_SHADER_VARIABLES
        initial_variables.parallax_factor = self.parallax_factor
        initial_variables.camera_focus    = self.parallax_camera_focus

        # Create a timeline
        timeline = BrokenTimeline(initial_variables=initial_variables)

        # FIXME: Realistically speaking, how to
        class CircleCamera(BrokenKeyframe):
            def __call__(self, variables, T, t, tau):
                variables.camera_position = (lambda z: (z.real, z.imag)) (numpy.exp(2*math.pi*T*1j * 0.25))
                variables.camera_rotation = 0.03*(0.1*math.sin(tau) + 0.2*math.sin(2*tau) + 0.03*math.sin(10*tau))
                variables.camera_zoom = 1 - variables.parallax_factor
                # variables.parallax_factor = 0.15
                # variables.camera_focus = 1
                # variables.blend = 1.0 * atan(500*(tau/10 - 0.5))/math.pi + 0.5

        # Add keyframes
        timeline.add_keyframe(CircleCamera() @ 0.0)

        # Get FFmpeg binary
        # externals = BrokenExternals()
        # ffmpeg_binary = externals.get("ffmpeg")

        # Random video output name
        video_output = DEPTHFLOW_DIRECTORIES.TEMP/f"{uuid.uuid4()}.mp4"

        # Open FFmpeg rendering to video
        ffmpeg = shell(
            "ffmpeg",
            "-loglevel", "error",
            "-hide_banner",
            "-f", "rawvideo",
            "-pix_fmt", "rgb24",
            "-s", f"{self.depthflowgl.render_resolution[0]}x{self.depthflowgl.render_resolution[1]}",
            "-r", self.parallax_fps,
            "-i", "-",
            # Resize to the nearest 2-multiple of self.resolution and anti aliasing filter
            "-vf", f"scale={self.depthflowgl.video_resolution[0]//2*2}:{self.depthflowgl.video_resolution[1]//2*2}:flags=lanczos",
            "-profile:v", "baseline",
            "-preset", "slow",
            "-tune", "film",
            "-vcodec", "libx264",
            "-crf", "25",
            "-pix_fmt", "yuv420p",
            video_output,
            "-y",
            Popen=True,
            stdin=PIPE
        )

        # Progress bar rendering timeline and frames to FFmpeg
        time_linspace = numpy.linspace(0, self.parallax_duration, self.parallax_duration*self.parallax_fps)
        for T in tqdm(time_linspace, desc="Rendering Video", unit="frames"):
            variables = timeline.at(T)
            frame = self.depthflowgl.render(variables)
            ffmpeg.stdin.write(frame)

        # Wait video encoding to finish
        ffmpeg.stdin.close()
        ffmpeg.wait()

        # Delete temporary video after 1 minute
        def deletes_video(video_output):
            time.sleep(60)
            video_output.unlink()
        BrokenUtils.better_thread(deletes_video, video_output, start=True)

        return str(video_output)


def main():
    depthflow_gradio = DepthFlowGradio()
    depthflow_gradio.webui()

if __name__ == "__main__":
    main()
