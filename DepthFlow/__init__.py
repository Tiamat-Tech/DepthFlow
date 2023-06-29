from Broken import *

# Directories
DEPTHFLOW_DIRECTORIES = make_project_directories(app_name="DepthFlow", app_author="BrokenSource")
SHADERS_DIRECTORY = DEPTHFLOW_DIRECTORIES.EXECUTABLE/"Shaders"

# PIL.Image is a module, .Image is its abstract class
PilImage = PIL.Image.Image
SomeImage = Union[PathLike, str, PilImage]

# Cached requests
session = requests_cache.CachedSession(DEPTHFLOW_DIRECTORIES.CACHE/'RequestsCache')

# -------------------------------------------------------------------------------------------------|

class ImageDepthUtils:
    depth_estimator = None

    def load_image(image: SomeImage, echo=True) -> PilImage:
        """Smartly load 'SomeImage', a path, url or PIL Image"""

        # Nothing to do if already a PIL Image
        if isinstance(image, PilImage):
            return image

        # Load image if a path or url is supplied
        elif any([isinstance(image, T) for T in (PathLike, str)]):
            if (path := true_path(image)).exists():
                if echo: info(f"Loading image from path [{path}]")
                return PIL.Image.open(path).convert("RGB")
            else:
                if echo: info(f"Loading image from (maybe) url [{image}]")
                return PIL.Image.open(BytesIO(session.get(image).content))
        else:
            error(f"Unknown image parameter [{image}], must be a PIL Image, Path or URL")
            return None

    # # Depth Estimation

    def __load_depth_map_estimator():
        """Load depth estimation transformer if not initialized"""
        if ImageDepthUtils.depth_estimator is None:
            warning("Loading Depth Map Estimator Model, might take a while, downloading models and loading them (first time only)")
            ImageDepthUtils.depth_estimator = transformers.pipeline("depth-estimation", model="vinvino02/glpn-nyu")
        success("Depth Map Estimator Model loaded")

    def depth_map(image: SomeImage, cache=True) -> PilImage:
        """Monocular Depth Map Estimation"""

        # Load the image
        image = ImageDepthUtils.load_image(image)

        # Calculate hash of the image for caching
        image_hash = hashlib.md5(image.tobytes()).hexdigest()
        cache_path = DEPTHFLOW_DIRECTORIES.CACHE/f"{image_hash}.jpg"
        info(f"Image hash for Depth Map cache is [{image_hash}]")

        # If the depth map is cached, return it
        if cache and cache_path.exists():
            success(f"Depth map already cached on [{cache_path}]")
            return ImageDepthUtils.load_image(cache_path).convert("L")

        # Load base image, estimate the depth map, save to cache
        ImageDepthUtils.__load_depth_map_estimator()

        # Estimate Depth Map
        warning("Estimating Depth Map for input image (Might take a while, heavy on CPU / GPU if CUDA)")
        with halo.Halo():
            depth_map = ImageDepthUtils.depth_estimator(image)["depth"]

        # Save image to Cache
        if cache:
            success(f"Saving depth map to cache path [{cache_path}]")
            depth_map.save(cache_path)

        return depth_map

    def normalized_depth_map(image: SomeImage, cache=True) -> PilImage:
        """Normalize the depth map to (0, 1) based on the min and max values"""

        # Get array of depth map to do math
        depth_map = numpy.array(ImageDepthUtils.depth_map(image, cache=cache))

        # Calculate the normalization factor
        if (normalize := depth_map.max() - depth_map.min()) == 0:
            warning("Depth map (min(D) = max(D)), something went wrong on the depth estimation? Returning depth map as is")
            return depth_map

        # Normalize the depth map
        depth_map = (depth_map - depth_map.min()) / normalize
        return PIL.Image.fromarray((depth_map * 255).astype("uint8"))

# -------------------------------------------------------------------------------------------------|

class DepthFlow:
    def __init__(self):

        # Create OpenGL Context
        self.opengl_context = moderngl.create_standalone_context()

        # Initialize program and shaders
        self.program = self.opengl_context.program(
            vertex_shader=(SHADERS_DIRECTORY/"DepthFlow.vert").read_text(),
            fragment_shader=(SHADERS_DIRECTORY/"DepthFlow.frag").read_text(),
        )

        # We'll only have two textures so hardcode their position
        self.program["base_image"].value = 0
        self.program["depth_map"].value = 1

        # Define vertices: pairs of [vec2 render_vertex] and [vec2 coords_vertex]
        #
        # The render_vertex are on "GLUV - OpenGL UV" coordinates, the screen rectangle to render
        # - The origin is at the center of the screen, with the XY axis going from -1 to 1
        #
        # The coords_vertex are on "STUV - ShaderToy UV" coordinates, the texture coordinates
        # - The origin is at the bottom left of the screen, with the XY axis going from 0 to 1
        #
        vertices = numpy.array([
                -1.0, -1.0, 0.0, 1.0,
                -1.0,  1.0, 0.0, 0.0,
                 1.0, -1.0, 1.0, 1.0,
                 1.0,  1.0, 1.0, 0.0,
            ],
            dtype="f4",
        )

        # Upload vertices to the Vertex Buffer Object
        self.vbo = self.opengl_context.buffer(vertices)

        # Create Vertex Array Object
        self.vao = self.opengl_context.simple_vertex_array(self.program, self.vbo, "render_vertex", "coords_vertex")

        # Super Sampling Anti Aliasing
        fixme("SSAA is not implemented yet")
        self.ssaa = 1

    # # Properties

    @property
    def resolution(self) -> numpy.ndarray:
        return numpy.array(self.base_image.size)

    @property
    def resolution_ssaa(self) -> numpy.ndarray:
        return self.resolution * self.ssaa

    # # Inputs

    def send_uniform(self, name, value):
        """Send a uniform to the shader fail-safe if it isn't used"""
        if name in self.program:
            self.program[name].value = value

    def input(self, image: SomeImage, depth_map: SomeImage=None) -> bool:
        """Load an base image, calculate its depth map and upload both to the GPU"""

        # Load image and its depth map
        self.base_image = ImageDepthUtils.load_image(image)
        self.depth_map  = ImageDepthUtils.normalized_depth_map(image) if (depth_map is None) else depth_map
        self.send_uniform("resolution", self.resolution)

        def upload_texture(texture, channels, index):
            texture = self.opengl_context.texture(texture.size, channels, texture.tobytes())
            texture.filter = (moderngl.LINEAR_MIPMAP_NEAREST, moderngl.LINEAR_MIPMAP_NEAREST)
            texture.build_mipmaps()
            texture.anisotropy = 16
            texture.use(index)

        # Upload textures to the GPU
        info("Uploading textures to OpenGL - GPU")
        upload_texture(self.base_image, channels=3, index=0)
        upload_texture(self.depth_map,  channels=1, index=1)

        # Create Frame Buffer Object
        info(f"Creating Frame Buffer Object with resolution {self.resolution}")
        self.fbo = self.opengl_context.simple_framebuffer(self.resolution)
        self.fbo.use()

        return True

    # # Render function

    def render_image(self) -> bytes:
        """Clear context, render, return raw RGB SSAA resolution image"""
        self.opengl_context.clear(0, 0, 0)
        self.vao.render(moderngl.TRIANGLE_STRIP)
        return self.fbo.read(components=3, alignment=1)

    def render_video(self,
        # Something that accepts .(DepthFlow.self, time)
        next: callable,

        # Video parameters
        output="Parallax.mp4",
        duration=10,
        fps=60
    ):
        output = true_path(output)
        info(f"Rendering video to path [{output}]")

        # Spawn FFmpeg
        self.ffmpeg = shell(
            BROKEN_FFMPEG_BINARY,
            "-loglevel", "error",
            "-hide_banner",
            "-f", "rawvideo",
            "-pix_fmt", "rgb24",
            "-s", f"{self.resolution_ssaa[0]}x{self.resolution_ssaa[1]}",
            "-r", str(fps),
            "-i", "-",

            # Resize to the nearest 2-multiple of self.resolution and anti aliasing filter
            "-vf", f"scale={self.resolution[0]//2*2}:{self.resolution[1]//2*2}:flags=lanczos",

            "-profile:v", "high",
            "-preset", "slow",
            "-tune", "film",
            "-vcodec", "libx264",
            "-crf", "25",
            "-pix_fmt", "yuv420p",
            output,
            "-y",

            # Broken shell options
            Popen=True,
            stdin=PIPE
        )

        total_frames = duration * fps

        # Progress bar iterating over total frames
        with tqdm(total=total_frames, unit="frame") as progress:
            for time in numpy.linspace(0, duration, total_frames):

                # Apply dynamics to the shader
                self.send_uniform("time", time)
                next(self, time, duration)

                # Render send image to FFmpeg
                image = self.render_image()
                self.ffmpeg.stdin.write(image)
                progress.update(1)

        self.ffmpeg.stdin.close()
        self.ffmpeg.wait()

        success(f"Video rendered to [{output}]")
        return output

# -------------------------------------------------------------------------------------------------|

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

def main():
    # Initialize DepthFlow
    depthflow = DepthFlow()

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

