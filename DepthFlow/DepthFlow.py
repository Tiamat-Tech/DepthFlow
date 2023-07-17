from DepthFlow import *

# -------------------------------------------------------------------------------------------------|

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

class DepthFlowTextureIndex(Enum):
    A = (0, 1)
    B = (2, 3)

# Default shader pipelines
DEPTHFLOW_DEFAULT_SHADER_VARIABLES = DotMap(
    # Camera
    camera_position = (0.0, 0.0),
    camera_rotation = 0.0,
    camera_focus    = 1.0,
    camera_zoom     = 1.0,

    # Parallax
    parallax_factor = 0.0,

    # Vignette
    vignette_radius = 0.0,
    vignette_smooth = 0.0,

    # Textures
    blend           = 0.0,
)

class DepthFlowGL:
    def __init__(self):
        self.mde = DepthFlowMDE()
        self.textures = DotMap()

    # # OpenGL / Shaders

    def init(self):
        """Initialize OpenGL and Shaders"""

        # Create OpenGL Context
        info("Creating OpenGL Context")
        self.opengl_context = moderngl.create_standalone_context()

        # Initialize program and shaders
        info("Initializing OpenGL Program and Shaders")
        self.program = self.opengl_context.program(
            vertex_shader=(SHADERS_DIRECTORY/"DepthFlow.vert").read_text(),
            fragment_shader=(SHADERS_DIRECTORY/"DepthFlow.frag").read_text(),
        )

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

        # Create VBO and VAO objects
        info("Creating OpenGL VBO and VAO objects")
        self.vbo = self.opengl_context.buffer(vertices)
        self.vao = self.opengl_context.simple_vertex_array(self.program, self.vbo, "render_vertex", "coords_vertex")
        self.fbo = None

        # Super Sampling Anti Aliasing
        self.ssaa = (1440/1080)

    # # Properties

    @property
    def video_resolution(self) -> numpy.ndarray:
        return numpy.array(self.textures[0].size)

    @property
    def render_resolution(self) -> numpy.ndarray:
        return (self.video_resolution * self.ssaa).astype(int)

    # # Uniforms

    def set_uniform(self, name, value) -> None:
        """Send a uniform to the shader fail-safe if it isn't used"""
        if name in self.program:
            self.program[name].value = value

    def get_uniform(self, name) -> Option[Any, None]:
        """Get a uniform from the shader fail-safe if it isn't used"""
        return self.program[name].get(value, None)

    # # Textures

    def _upload_texture(self, name: str, texture: PilImage, index: int, channels: int=3) -> None:
        """Internal: Upload a texture to the GPU and send it to the shader at a variable name"""
        info(f"• Uploading Texture to OpenGL")
        info(f"└─ Info: [{name} ({texture.size[0]}x{texture.size[1]}x{channels}) @ Index {index}]")

        # Do the ModernGL magic
        texture = self.opengl_context.texture(texture.size, channels, texture.tobytes())
        texture.filter = (moderngl.LINEAR_MIPMAP_NEAREST, moderngl.LINEAR_MIPMAP_NEAREST)
        texture.build_mipmaps()
        texture.anisotropy = 16
        texture.use(index)
        self.set_uniform(name, index)
        self.textures[index] = texture

    def upload_texture(self,
        index: DepthFlowTextureIndex,
        image: Union[PilImage, PathLike, URL],
        depth: Union[PilImage, PathLike, URL]=None
    ) -> None:

        # Load image and its depth map
        image = BrokenSmart.load_image(image).convert("RGB")
        depth = depth or self.mde.depth_map(image)

        # Upload textures to the GPU
        self._upload_texture(f"image_{index.name}", image, index=index.value[0], channels=3)
        self._upload_texture(f"depth_{index.name}", depth, index=index.value[1], channels=1)
        self._create_update_fbo()

    def _create_update_fbo(self) -> None:
        """Create and/or update FBO as needed for current input image resolution"""
        if self.fbo is None:
            pass
        elif (self.fbo.size != self.render_resolution).any():
            self.fbo.release()
        else:
            return
        info(f"• Creating new main Frame Buffer Object")
        info(f"└─  Resolution: [{self.render_resolution[0]}x{self.render_resolution[1]}]")
        self.fbo = self.opengl_context.simple_framebuffer(self.render_resolution)
        self.fbo.use()

    # # Render function

    def render(self, variables: DotMap={}, read=True) -> bytes:
        """Clear context, render, return raw RGB SSAA resolution image if read=True"""
        self._create_update_fbo()

        # Send variables to the shader
        for name, value in variables.items():
            self.set_uniform(name, value)

        # Clear screen, render, read pixels
        self.opengl_context.clear(0)
        self.vao.render(moderngl.TRIANGLE_STRIP)
        return self.fbo.read() if read else None
