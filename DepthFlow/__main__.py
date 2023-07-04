from DepthFlow import *

def main():
    # Initialize DepthFlow
    depthflow = DepthFlow()

    # Start OpenGL
    depthflow.init_opengl()

    # Input Path or URL
    # depthflow.input(image=DEPTHFLOW_DIRECTORIES.DATA/"input.png")
    depthflow.input(image="https://w.wallhaven.cc/full/p9/wallhaven-p9jrqj.png")

    # Render to video
    depthflow.render_video(
        next=PresetDefault(loop_time=4).next,
        output="Parallax.mp4",
        duration=10,
        fps=60
    )

