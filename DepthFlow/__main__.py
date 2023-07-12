from DepthFlow import *


def main():

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

    # # Render to video
    # depthflow.render_video(
    #     next=PresetDefault(loop_time=5).next,
    #     output="Parallax.mp4",
    #     duration=10,
    #     fps=60
    # )

if __name__ == "__main__":
    main()
