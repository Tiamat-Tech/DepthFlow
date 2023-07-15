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

def music(
    prompt: str,
    device="auto",
    model: AudioCraftModel=AudioCraftModel.Small,
    ):
    ...


def main():
    # typer = BrokenBase.typer_app()
    # typer.command()(gl)
    # typer.command()(music)
    # typer()

    def greet(name):
        return "Hello " + name + "!"
    demo = gradio.Interface(fn=greet, inputs="text", outputs="text")
    demo.launch()


if __name__ == "__main__":
    main()
