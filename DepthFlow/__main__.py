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
