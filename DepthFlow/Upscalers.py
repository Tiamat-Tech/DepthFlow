from DepthFlow import *


class BrokenUpscaler:

    # #

    Simple = DotMap(
        name="simple-upscaler"
    )

    # # Nihui Upscalers

    Realsr = DotMap(
        name="realsr-ncnn-vulkan",
        scale=(4),
        noise=None,
        models=("DF2K", "DF2K_JPEG")
    )

    SRMD = DotMap(
        name="srmd-ncnn-vulkan",
        scale=(2, 3, 4),
        noise=range(-1, 11),
        models=None,
    )

    Waifu2x = DotMap(
        name="waifu2x-ncnn-vulkan",
        scale=(1, 2, 4, 8, 16, 32),
        noise=(-1, 0, 1, 2, 3),
        models=None,
    )

class BrokenImageUpscaler(ABC):
    def set_upscaler(self, upscaler: BrokenUpscaler) -> Self:
        self.upscaler = upscaler
        return self

    def upscale(self, image: Union[PilImage, PathLike, URL]) -> PilImage:
        """Upscale an image"""
        raise NotImplementedError

    def download(self) -> Self:
        """Grabs the latest """

        # Some nihui release
        if "ncnn" in self.upscaler.name:

            # Download assets information
            json = BROKEN_REQUESTS_CACHE.get(f"https://api.github.com/repos/nihui/{self.upscaler.name}/releases/latest").json()
            platform = BrokenPlatform.Name.replace("linux", "ubuntu")

            for asset in json.get("assets"):
                if platform in asset.get("name"):
                    url = asset.get("browser_download_url")
                    break

            with BrokenDownloads.download(url) as zip_file:
                # Extract to BROKEN_DIRECTORIES.EXTERNALS
                BrokenDownloads.extract_archive(zip_file, BROKEN_DIRECTORIES.EXTERNALS)
        return self


# b = BrokenDependencies()
# exit()


# upscaler = BrokenImageUpscaler()
# upscaler.set_upscaler(BrokenUpscaler.Realsr).download()
# upscaler.set_upscaler(BrokenUpscaler.SRMD).download()
# upscaler.set_upscaler(BrokenUpscaler.Waifu2x).download()
# exit()
