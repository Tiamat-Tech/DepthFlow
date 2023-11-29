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

> Download and install our [**Framework**](https://github.com/BrokenSource/BrokenSource) with all the code and projects first


## Running the code

- Run the command: `broken depthflow` or simply `depthflow` on the Broken Shell

A **Gradio** interface should open, the first execution will download some models, be patient


## Using your GPU

> By default, Pytorch will be installed with CPU support.

If you want to **Speed Up** the **Depth Estimation** process, you can install it with GPU support:

<br/>

**NVIDIA**<sup>N1</sup> (CUDA):
- Install [CUDA](https://developer.nvidia.com/cuda-downloads) and [cuDNN](https://developer.nvidia.com/cudnn)
- Run the command: `broken depthflow poe cuda`

<sub>*N1: Preferably from package manager in Linux if so</sub>

<sub>*N1: Your GPU must support the PyTorch's CUDA installation version, pretty much all >= GTX 900</sub>


<br/>

**AMD**<sup>R1</sup> (ROCm):
- Run the command: `broken depthflow poe rocm`

<sub>*R1: Preferably from package manager in Linux if so</sub>

<sub>*R1: Check for compatibility with your GPU, generally speaking anything <= Polaris (<= RX 500 series) is not supported</sub>


<br/>

**CPU / macOS** (Default):

- Run the command: `broken depthflow poe cpu`


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