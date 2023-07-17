👆【☰】Table of Contents

<div align="justify">

<div align="center">
  <img src="https://github.com/BrokenSource/DepthFlow/assets/29046864/9ea5fbd4-4f3e-4742-9a36-d6b8b6f02b65" width="160">

  <h1>DepthFlow</h1>

  Image → **2.5D Parallax** Effect Video

  Eventual **Text to Video** powered by **Stable Diffusion**

  <img src="https://api.star-history.com/svg?repos=BrokenSource/DepthFlow&type=Timeline" width=500/>
</div>


<br/>
<br/>

# 🔥 Description

**💡 Base idea:**
1. Given an image and its depth map, have a shader to generate a parallax effect
2. Estimate Depth Maps with Neural Networks for generic images
3. Varying the projections over time generates a 2.5D video

As simple as that, we achieve a similar effect as [**Depthy**](https://depthy.stamina.pl)

- 🤗 All of that with an WebUI powered by [**Gradio**](https://www.gradio.app/)

**Currently,** we have:
- 🎥 Interface for Image to Parallax Video
- 🎵 Interface for AI Stereo Music using [**AudioCraft**](https://github.com/facebookresearch/audiocraft)

<br/>

**📈 Upcoming:**
- **Feedback-loop** the parallax images to Stable Diffusion **img2img** after some initial **txt2img**
- **Quick Visual Effects**: Vignette, particles, rotation on the base Shader

This way we achieve a **text to video** effect where Stable Diffusion fills in the progressively unknown parts of the parallaxed image

Some possibilities include:
- Infinite side scrolling with the camera focusing on the background
- Infinite rotation around any intermediate point on the image
- Infinite rotation focusing on the closest image
- Better zoom in, zoom out effects

<br/>

**🏆 Challenges:**
- **GPU Computation time** will be a bottleneck for longer videos or many feedback loops per second
  - _Possible solution_: Use fewer steps on img2img since it is already close to the target
  - _Implementation_: Stop when `MSE(A, B)` is low enough
- **Depth Estimation** is a hard problem, the output should be accurate enough
- **The Shader** can't do magic, let's make it better

<sub>Eventually I'd like the Shaders pipeline and imagery to be part of ShaderFlow project. The one here might not be the most flexible</sub>

<br/>

**👑 Future:**
- **Keyframes:** Given a list of _keyframes_, interpolate prompts, depth maps, effects intensity
- Maybe some form of API and **User Interface** to make it easier to use
- **Music:** Generative music that maybe follows the video



<br/>
<br/>

# Installation

## 🔮 Prebuilt Binaries
We only release prebuilt binaries with PyTorch CUDA backend exclusive to NVIDIA GPUs, don't worry, if you are on macOS or have an AMD GPU please run directly from the source code, it works just as well

**Instructions**:

- Install [CUDA](https://developer.nvidia.com/cuda-downloads) and [cuDNN](https://developer.nvidia.com/cudnn) (Preferably from package manager in Linux)

- Grab the latest [DepthFlow Release](https://github.com/BrokenSource/DepthFlow/releases/latest) for your platform, run it



### 📦 Package Manageer
We are actively looking for package managers to bundle our projects, if you are interested in helping please contact us, you'll be credited here and do a great convenience service to the whole community

<br/>

## Running from the Source Code
Follow instructions on our [Monorepo](https://github.com/BrokenSource/BrokenSource) for downloading our Framework, and chose PyTorch acceleration method below:


### 🔦 Selecting PyTorch Acceleration Method
PyTorch has three different packages: CPU mode only, CUDA with NVIDIA GPUs and ROCm for AMD GPUs

Before running DepthFlow, select the PyTorch acceleration source package by modifying the `DepthFlow/pyproject.toml` file

Beware dragons:
- `CUDA`: Default installation, assumes you have a CUDA capable NVIDIA GPU and CUDA installed
- `ROCm`: Work in progress from AMD, might be unstable, should work in general
- `CPU`: Most compatible option, but slow for bigger inferences

You can reinstall the Python virtual environment with `broken depthflow --reinstall` to apply the changes


<br/>
<br/>

# 🚧 Hardware Requirements
<div align="center">
  Dear user with weak specs, you can only do so much on a limited hardware
</div>

<br/>
The faster the hardware (CPU, GPU, RAM), the faster the code will run. Apart from memory restrictions your hardware should support some minimum technologies:

- **CPU:** Any should do, affects video encoding time
- **GPU:** Supports OpenGL 3.3 or higher<sup>1</sup>, affects rendering time (sent to the CPU)
  - Parallax mode: Very few VRAM for both NVIDIA and AMD
  - Stable Diffusion:
    - *Extra Large*: Minimum 8 GB VRAM for NVIDIA<sup>2</sup>, 16 GB for AMD<sup>3</sup>
    - *Previous*: Minimum 6 GB VRAM for NVIDIA<sup>2</sup>, 8 GB for AMD<sup>3</sup>
  - AudioCraft:
    - Runnable on 4 GB for NVIDIA small model context length 5, (hangs on AMD?)
    - Likely minimum 8 GB for NVIDIA medium size, ideally 12 GB or 16 GB
- **OS:** Windows (10+), Linux, macOS - 64 bits
- **Disk:** Roughly 30 GB free space (models and dependencies are big)
- **RAM:** Minimum 12 GB, 16 GB Recommended, should be doable in 8 GB

The main bottleneck 99% the time is the GPU for generative images and the parallax shader projections


<sub>*1: Some NVIDIA datacenter GPUs does not implement common graphics APIs, for example A100, H100</sub>

<sub>*3: Your GPU must support the PyTorch's CUDA installation version, pretty much all >= GTX 900 </sub>

<sub>*2: Check for compatibility with your GPU, generally speaking anything <= Polaris (<= RX 500 series) is not supported</sub>



<br/>
<br/>

# ⚖️ License

## 👤 Personal use
- **User Generated Content**: CC-BY 4.0 License
- **Code**: AGPLv3-Only License

While we won't enforce punishments for failed attributions, we would appreciate if you could credit us

## 🎩 Professional use
Want to use this for your company or comercially?

- Let's do something great together, contact us at [Broken Source Software](https://github.com/BrokenSource)

</div>