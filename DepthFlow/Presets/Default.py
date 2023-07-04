from . import *

class PresetDefault:
    def __init__(self, loop_time=10):
        self.loop_time = loop_time

    def next(self, depthflow: DepthFlow, time: float, duration: float) -> None:
        parallax_intensity = 0.15

        # Around circles camera position (normalized)
        camera_position = numpy.exp(1j * (2*pi) * (time/self.loop_time))
        depthflow.send_uniform("camera_position", (camera_position.real, camera_position.imag))

        # Camera distance
        depthflow.send_uniform("camera_distance", 1)

        # Zoom in and out
        zoom_intensity = 0.05
        zoom = (1.0 - zoom_intensity) + zoom_intensity*sin((2*pi) * (time/self.loop_time))
        depthflow.send_uniform("zoom", zoom)

        # Parallax intensity
        depthflow.send_uniform("parallax_intensity", parallax_intensity)

        # Vignette
        depthflow.send_uniform("vignette_radius", 0.3)
        depthflow.send_uniform("vignette_intensity", 0.3)
