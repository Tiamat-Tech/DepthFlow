from DepthFlow import *


def gl():

    # Initialize DepthFlow
    depthflow = DepthFlowGL()
    depthflow.init()

    # Input Path or URL
    depthflow.upload_texture(
        index=DepthFlowTextureIndex.A,
        image="https://w.wallhaven.cc/full/x6/wallhaven-x61e1l.jpg"
    )
    depthflow.upload_texture(
        index=DepthFlowTextureIndex.B,
        image="https://w.wallhaven.cc/full/85/wallhaven-85dv52.png"
    )

    # Create a timeline
    timeline = BrokenTimeline(initial_variables=DEPTHFLOW_DEFAULT_SHADER_VARIABLES)

    class CircleCamera(BrokenKeyframe):
        def __call__(self, variables, T, t, tau):
            variables.parallax_factor = 0.15
            variables.camera_position = (lambda z: (z.real, z.imag)) (numpy.exp(2*pi*T*1j * 0.25))
            variables.camera_rotation = 0.03*(0.1*sin(tau) + 0.2*sin(2*tau) + 0.03*sin(10*tau))
            variables.camera_focus = 1
            variables.camera_zoom = 1 - variables.parallax_factor
            variables.blend = 1.0 * atan(500*(tau/10 - 0.5))/pi + 0.5


    # Add keyframes
    timeline.add_keyframe(CircleCamera() @ 0.0)

    # Render
    fps = 60
    duration = 10

    # Get FFmpeg binary
    externals = BrokenExternals()
    ffmpeg_binary = externals.get("ffmpeg")

    # Open FFmpeg rendering to video
    ffmpeg = shell(
        ffmpeg_binary,
        "-loglevel", "error",
        "-hide_banner",
        "-f", "rawvideo",
        "-pix_fmt", "rgb24",
        "-s", f"{depthflow.render_resolution[0]}x{depthflow.render_resolution[1]}",
        "-r", fps,
        "-i", "-",
        # Resize to the nearest 2-multiple of self.resolution and anti aliasing filter
        "-vf", f"scale={depthflow.video_resolution[0]//2*2}:{depthflow.video_resolution[1]//2*2}:flags=lanczos",
        "-profile:v", "high",
        "-preset", "slow",
        "-tune", "film",
        "-vcodec", "libx264",
        "-crf", "25",
        "-pix_fmt", "yuv420p",
        "parallax.mp4",
        "-y",
        Popen=True,
        stdin=PIPE
    )

    # Render using tqdm
    for T in tqdm(numpy.linspace(0, duration, duration*fps), desc="Rendering Video", unit="frames"):
        variables = timeline.at(T)
        frame = depthflow.render(variables)
        ffmpeg.stdin.write(frame)



# Ideas:
# "An 80s driving pop song with heavy drums and synth pads in the backgroun"
# "a light and cheerly EDM track, chorus, with syncopated drums, aery pads, and strong emotions bpm: 130
# "A cheerful song with acoustic guitars with a lofi feel and a catchy melody, not fading away
# "upbeat tropical house with a strong beat and a catchy melody, clean and short drums, no transitions, no whitenoise
# "lofi slow bpm electro chill with organic samples and rhodes
def music(
    model: AudioCraftModel="small",
    prompt: str="A cheerful electronic dance music with a catchy melody plucky bassy house music trance"
):
    dm = DepthMusic(AudioCraftModel.Small)
    dm.main(prompt=prompt)


def gradio_demo():
    def greet(name):
        return "Hello " + name + "!"
    demo = gradio.Interface(fn=greet, inputs="text", outputs="text")
    demo.launch()


def sd_mock():
    sd = BrokenStableDiffusion()
    sd.load_model()
    sd.optimize()
    sd.prompt("Astronaut on a white rocky moon landscape").save("astronaut.png")


def main():
    typer = BrokenBase.typer_app()
    typer.command()(gl)
    typer.command()(music)
    typer.command()(gradio_demo)
    typer.command()(sd_mock)
    typer()



if __name__ == "__main__":
    main()
