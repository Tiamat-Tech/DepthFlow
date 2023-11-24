👆【☰】Table of Contents

<div align="justify">

<div align="center">
  <!-- Logo -->
  <img src="https://github.com/BrokenSource/DepthFlow/assets/29046864/9ea5fbd4-4f3e-4742-9a36-d6b8b6f02b65" width="160">

  <h1>DepthFlow</h1>

  <!-- Visitor count -->
  <img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fhits.dwyl.com%2FBrokenSource%2FDepthFlow.json%3Fshow%3Dunique&label=Visitors&color=blue"/>
  <img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fhits.dwyl.com%2FBrokenSource%2FDepthFlow.json&label=Page%20Views&color=blue"/>

  Image → **2.5D Parallax** Effect Video

  <!-- Star graph -->
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


<br/>
<br/>

# 🔱 Installation

## Dependencies
- Setup our [**Framework**](https://github.com/BrokenSource/BrokenSource)

By default, Pytorch will be installed with CPU support, if you want to use your GPU:

**NVIDIA** + CUDA:
- Install<sup>1</sup> [CUDA](https://developer.nvidia.com/cuda-downloads) and [cuDNN](https://developer.nvidia.com/cudnn)
- Run the command: `broken depthflow poe cuda`

<sup><i>1: Preferably from package manager in Linux if so</i></sup>

**AMD** + ROCm:
- Run the command: `broken depthflow poe rocm`

**CPU / macOS**:
- Run the command: `broken depthflow poe cpu`

## Running the code
- Run the command: `broken depthflow` or simply `depthflow` on the Broken Shell


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
- **OS:** Windows (10+), Linux, macOS - 64 bits
- **Disk:** Roughly 30 GB free space (models and dependencies are big)
- **RAM:** Minimum 12 GB, 16 GB Recommended, should be doable in 8 GB


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
Want to use this for your company or commercially?

- Let's do something great together, contact us at [Broken Source Software](https://github.com/BrokenSource)

</div>