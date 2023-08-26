import torch

from Broken import *

# -------------------------------------------------------------------------------------------------|
# Torch - The bane of my existence
# IDEA: Torch initialization or information should be part of something else of Broken
warnings.filterwarnings("ignore", message="Can't initialize NVML")

# Prefer CUDA if available, override with TORCH_DEVICE env variable
TORCH_DEVICE = os.environ.get("TORCH_DEVICE", None) or ("cuda" if torch.cuda.is_available() else "cpu")
log.info(f"• Torch Information:")
log.info(f"├─ CUDA Available: [{torch.cuda.is_available()}]")
log.info(f"├─ Torch Device:   [{TORCH_DEVICE}]")
if TORCH_DEVICE != "cpu":
    log.info(f"├─ Device Name:    [{torch.cuda.get_device_name()}]")
log.info(f"└─ Torch Version:  [{torch.__version__}]")

# -------------------------------------------------------------------------------------------------|

# Directories
DEPTHFLOW_DIRECTORIES = BrokenDirectories(app_name="DepthFlow", app_author="BrokenSource")
DEPTHFLOW_DIRECTORIES.SHADERS = DEPTHFLOW_DIRECTORIES.RESOURCES/"Shaders"

# isort: off
from DepthFlow.DepthFlow import *
from DepthFlow.BrokenTimeline import *

# Mock
from .DepthAudio import *

