import torch

from Broken import *

# -------------------------------------------------------------------------------------------------|
# Torch - The bane of my existence

warnings.filterwarnings("ignore", message="Can't initialize NVML")

# Prefer CUDA if available, override with TORCH_DEVICE env variable
TORCH_DEVICE = os.environ.get("TORCH_DEVICE", None) or ("cuda" if torch.cuda.is_available() else "cpu")
info(f"• Torch Information:")
info(f"├─ CUDA Available: [{torch.cuda.is_available()}]")
info(f"├─ Torch Device:   [{TORCH_DEVICE}]")
if TORCH_DEVICE != "cpu":
    info(f"├─ Device Name:    [{torch.cuda.get_device_name()}]")
info(f"└─ Torch Version:  [{torch.__version__}]")

# -------------------------------------------------------------------------------------------------|

# Directories
DEPTHFLOW_DIRECTORIES = BrokenDirectories(app_name="DepthFlow", app_author="BrokenSource")
SHADERS_DIRECTORY     = DEPTHFLOW_DIRECTORIES.EXECUTABLE/"Shaders"

# isort: skip
from DepthFlow.DepthFlow import *
from DepthFlow.Presets import *
from DepthFlow.Shaders import *
from DepthFlow.Timeline import *

# Test timeline
if os.environ.get("TEST_TIMELINE", None):
    import DepthFlow.Mock.Timeline
    DepthFlow.Mock.Timeline.test_timeline()
    exit()