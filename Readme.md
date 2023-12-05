👆【☰】Table of Contents

<div align="justify">

<div align="center">
  <img src="./DepthFlow/Resources/DepthFlow.png" width="200">

  <h1>DepthFlow</h1>

  <img src="https://img.shields.io/github/stars/BrokenSource/DepthFlow" alt="Stars Badge"/>
  <img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fhits.dwyl.com%2FBrokenSource%2FDepthFlow.json%3Fshow%3Dunique&label=Visitors&color=blue"/>
  <img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fhits.dwyl.com%2FBrokenSource%2FDepthFlow.json&label=Page%20Views&color=blue"/>
  <img src="https://img.shields.io/github/license/BrokenSource/DepthFlow?color=blue" alt="License Badge"/>
  <a href="https://t.me/brokensource">
    <img src="https://img.shields.io/badge/Telegram-Channel-blue?logo=telegram" alt="Telegram Channel Badge"/>
  </a>

  <sub> 👆 Out of the many **Explorers**, you can be among the **Shining** stars who support us! ⭐️ </sub>

  <br>

  <ins> Image → **2.5D Parallax** Effect Video. A Professional **[**[**Depthy**](https://depthy.stamina.pl)**]** Alternative. That's **[**[**DepthFlow**](https://github.com/BrokenSource/DepthFlow)**]**.</ins>
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

# 📦 Installation

> 🔴🟡🟢
>
> **Download** and install our [**Framework**](https://github.com/BrokenSource/BrokenSource) with all the code and projects first
>
> <sub><b>Note:</b> You cannot run this project without the <i>Framework</i></sub>

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

<sub>*N1: Your GPU must support the PyTorch's CUDA installation version, pretty much all >= GTX 900. Preferable install from your package manager in Linux if so</sub>


<br/>

**AMD**<sup>R1</sup> (ROCm):
- Run the command: `broken depthflow poe rocm`

<sub>*R1: Check for compatibility with your GPU, generally speaking anything <= Polaris (<= RX 500 series) is not supported. Preferably install from your package manager in Linux if so</sub>


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