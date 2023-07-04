from DepthFlow import *


class DepthEstimationModel(Enum):
    ZoeN  = DotMap(name="ZoeDepthN",  type="transformers", repository=("isl-org/ZoeDepth", "ZoeD_N") )
    ZoeK  = DotMap(name="ZoeDepthK",  type="transformers", repository=("isl-org/ZoeDepth", "ZoeD_K") )
    ZoeNK = DotMap(name="ZoeDepthNK", type="transformers", repository=("isl-org/ZoeDepth", "ZoeD_NK"))

    # Stable diffusion ones
    StableDiffusion   = DotMap()
    StableDiffusionXL = DotMap()


class DepthFlowMDE:
    """DepthFlow Monocular Depth Estimation"""

    def __init__(self):
        self.load_depth_model()

    def load_depth_model(self, model: DepthEstimationModel=DepthEstimationModel.ZoeN):
        """Lazy method: Set the Monocular Depth Map Estimation Model to be loaded as needed"""
        model = model.value

        # Self.mde doesn't exist, create it
        if getattr(self, "mde", None) is None:
            pass

        # Same model as before, do nothing
        elif self.mde.name == model.name:
            return

        # Model is loaded, no need to reload
        elif self.mde.model is not None:
            return

        self.mde = model

    def __load_depth_model(self):
        """Load depth estimation transformer if needed"""

        # The model has changed
        if not self.mde.model:
            warning(f"Loading new Monocular Depth Estimation Model [{self.mde.name}]")

            if self.mde.type == "transformers":
                self.mde.model = torch.hub.load(*self.mde.repository, pretrained=True)
                self.mde.model.to(TORCH_DEVICE)

        success("Depth Map Estimator Model loaded")

    def depth_map(self, image: Union[PilImage, PathLike, URL], normalized=True, cache=True) -> PilImage:
        """Monocular Depth Map Estimation"""

        # Load the image
        image = BrokenSmart.load_image(image)

        # Calculate hash of the image for caching
        image_hash = hashlib.md5(image.tobytes()).hexdigest()
        cache_path = DEPTHFLOW_DIRECTORIES.CACHE/f"{image_hash}-{self.mde.name}.jpg"
        info(f"Image hash for Depth Map cache is [{image_hash}]")

        # If the depth map is cached, return it
        if cache and cache_path.exists():
            success(f"Depth map already cached on [{cache_path}]")
            return BrokenSmart.load_image(cache_path).convert("L")

        # Load base image, estimate the depth map, save to cache
        self.__load_depth_model()

        # Estimate Depth Map
        warning("Estimating Depth Map for input image (Might take a while, heavy on CPU or GPU)")
        # with halo.Halo():
        if "Zoe" in self.mde.name:
            depth_map = self.mde.model.infer_pil(image)
        else:
            error(f"Unknown Monocular Depth Estimation Model [{self.mde}]")
            exit(1)

            # FIXME Implement the other non zoe models
            # depth_map = self.monocular_depth_estimation.model(image)["depth"]

        # Normalize the depth map to (0, 1) based on the min and max values
        if normalized:
            # Get array of depth map to do math
            depth_map = numpy.array(depth_map)

            # Calculate the normalization factor
            if (normalize := depth_map.max() - depth_map.min()) == 0:
                warning("Depth map (min(D) = max(D)), something went wrong on the depth estimation? Using as it is")
            else:
                depth_map = 255 * (depth_map - depth_map.min()) / normalize

        # Convert array to PIL Image RGB24
        depth_map = PIL.Image.fromarray(depth_map.astype("uint8"), "L")

        # Save image to Cache
        if cache:
            success(f"Saving depth map to cache path [{cache_path}]")
            depth_map.save(cache_path)

        return depth_map

# -------------------------------------------------------------------------------------------------|

class DepthFlow:
    def __init__(self):
        self.mde = DepthFlowMDE()

    # # OpenGL / Shaders

    def init_opengl(self):
        # Create OpenGL Context
        self.opengl_context = moderngl.create_standalone_context()

        # Initialize program and shaders
        self.program = self.opengl_context.program(
            vertex_shader=(SHADERS_DIRECTORY/"DepthFlow.vert").read_text(),
            fragment_shader=(SHADERS_DIRECTORY/"DepthFlow.frag").read_text(),
        )

        # We'll only have two textures so hardcode their position
        self.send_uniform("base_image", 0)
        self.send_uniform("depth_map", 1)

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
        self.ssaa = (1440/1080)

    # # Properties

    @property
    def resolution(self) -> numpy.ndarray:
        return numpy.array(self.base_image.size).astype(int)

    @property
    def resolution_ssaa(self) -> numpy.ndarray:
        return (self.resolution * self.ssaa).astype(int)

    # # Inputs

    def send_uniform(self, name, value):
        """Send a uniform to the shader fail-safe if it isn't used"""
        if name in self.program:
            self.program[name].value = value

    def input(self, image: Union[PilImage, PathLike, URL], depth_map: Union[PilImage, PathLike, URL]=None) -> Result:
        """Load an base image, calculate its depth map and upload both to the GPU"""

        # Load image and its depth map
        self.base_image = BrokenSmart.load_image(image)
        if self.base_image is None: return Error
        self.depth_map = self.mde.depth_map(image) if (depth_map is None) else depth_map
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
        self.fbo = self.opengl_context.simple_framebuffer(self.resolution_ssaa)
        self.fbo.use()

        return Ok

    # # Render function

    def render_image(self) -> bytes:
        """Clear context, render, return raw RGB SSAA resolution image"""
        self.opengl_context.clear(0)
        self.vao.render(moderngl.TRIANGLE_STRIP)
        return self.fbo.read()

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
