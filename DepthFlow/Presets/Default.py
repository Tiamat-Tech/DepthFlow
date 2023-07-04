from . import *

class PresetDefault:
    def __init__(self, loop_time=10):
        self.loop_time = loop_time

    def next(self, depthflow: DepthFlow, time: float, duration: float) -> None:
        # Normalized time from 0 to 1 relative to loop duration
        t = (time/self.loop_time)

        # Normalized time relative to loop duration for sin functions
        tau = 2*pi * (time/self.loop_time)

        # Around circles camera position (normalized)
        camera_position = numpy.exp(1j * tau)

        # Camera parameters
        depthflow.send_uniform("camera_position", (camera_position.real, camera_position.imag))
        depthflow.send_uniform("camera_distance", 1)
        depthflow.send_uniform("camera_rotation", (0.1*sin(tau) + 0.2*sin(2*tau) + 0.03*sin(10*tau))*0.07)

        # Zoom in and out
        zoom_intensity = 0.03
        zoom = (1.0 - zoom_intensity) + zoom_intensity*sin(tau)
        depthflow.send_uniform("camera_zoom", zoom)

        # Parallax intensity
        depthflow.send_uniform("parallax_intensity", 0.15)

        # Vignette
        depthflow.send_uniform("vignette_radius", 0.3)
        depthflow.send_uniform("vignette_intensity", 0.3)
