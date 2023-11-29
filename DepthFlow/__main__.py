from DepthFlow import *


class DepthFlowGradio:
    def webui(self, share: bool=False):
        self.components = DotMap()

        with gradio.Blocks(title="DepthFlow") as self.gradio_interface:
            if torch.cuda.is_available():
                gradio.Markdown(f"DepthFlow WebUI Prototype - [GPU {torch.cuda.get_device_name()}] - [Torch {torch.__version__}]")
            else:
                gradio.Markdown(f"DepthFlow WebUI Prototype - [CPU] - [Torch {torch.__version__}]")

            with gradio.Tab("DepthVideo"):
                with gradio.Row():
                    self.components.parallax_imageA = gradio.Image(label="Image A")

                with gradio.Blocks():
                    self.components.parallax_duration     = gradio.Slider(label="Duration (seconds)", minimum=1, maximum=120, value=10, step=1, interactive=True)
                    self.components.parallax_fps          = gradio.Slider(label="FPS", minimum=1, maximum=120, value=60, step=1, interactive=True)
                    self.components.parallax_factor       = gradio.Slider(label="Parallax Factor", minimum=0, maximum=1, value=0.25, step=0.01, interactive=True)
                    self.components.parallax_camera_focus = gradio.Slider(label="Camera Focus", minimum=0, maximum=1, value=1, step=0.01, interactive=True)

                self.components.parallax_generate = gradio.Button("Generate")
                self.components.parallax_video    = gradio.Video(label="Generated Video", format="mp4")

            # # Actions

            # Set of all components, identified by inputs[component]
            inputs = set(self.components.values())

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
            def __init__(self):
                self.position_noise = SombreroNoise(
                    frequency=0.15,
                    roughness=0.3,
                    octaves=6,
                    dimensions=2
                )

                self.rotation_noise = SombreroNoise(
                    frequency=0.4,
                    roughness=0.35,
                    octaves=4,
                    dimensions=1
                )

                self.zoom_noise = SombreroNoise(
                    frequency=0.2,
                    roughness=0.5,
                    octaves=3,
                    dimensions=1
                )

            def __call__(self, variables, T, t, tau):
                variables.camera_position = self.position_noise.at(T)
                variables.camera_rotation = 0.013 * self.rotation_noise.at(T)
                variables.camera_zoom = 1 - 0.25*variables.parallax_factor + 0.06*self.zoom_noise.at(T)

                # variables.parallax_factor = 0.15
                # variables.camera_focus = 1
                # variables.blend = 1.0 * atan(500*(tau/10 - 0.5))/math.pi + 0.5

        # Add keyframes
        timeline.add_keyframe(CircleCamera() @ 0.0)

        # Random video output name
        date = arrow.now().format("YYYY-MM-DD_HH-mm-ss")
        video_output = DEPTHFLOW_DIRECTORIES.DATA/f"{date}.mp4"

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

        return str(video_output)

def main():
    depthflow_gradio = DepthFlowGradio()
    depthflow_gradio.webui(share=False)

if __name__ == "__main__":
    main()
