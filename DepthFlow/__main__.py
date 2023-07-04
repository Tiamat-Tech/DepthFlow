from DepthFlow import *


def main():
    # Initialize DepthFlow
    depthflow = DepthFlow()
    depthflow.init_opengl()

    # Input Path or URL
    # depthflow.input(image=DEPTHFLOW_DIRECTORIES.DATA/"input.png")
    depthflow.input(image="https://w.wallhaven.cc/full/x6/wallhaven-x61e1l.jpg")

    # Render to video
    depthflow.render_video(
        next=PresetDefault(loop_time=5).next,
        output="Parallax.mp4",
        duration=10,
        fps=60
    )

