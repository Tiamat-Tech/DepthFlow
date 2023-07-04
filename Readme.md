<div align="center">
  <h1>DepthFlow</h1>

  Image → **2.5D Parallax** Effect Video

  Eventual **Text to Video** powered by Stable Diffusion
</div>



<br/>
<br/>

# Description

**Base idea:**
1. Given an image and its depth map, have a shader to generate a parallax effect
2. Estimate Depth Maps with Neural Networks for generic images
3. Varying the projections over time generates a 2.5D video

As simple as that, we achieve a similar effect as [Depthy](https://depthy.stamina.pl)

<br/>

**Upcoming:**
- **Feedback-loop** the parallax images to Stable Diffusion **img2img** after some initial **txt2img**
- **Quick Visual Effects**: Vignette, particles, rotation on the base Shader

This way we achieve a **text to video** effect where Stable Diffusion fills in the progressively unknown parts of the parallaxed image

Some possibilities include:
- Infinite side scrolling with the camera focusing on the background
- Infinite rotation around any intermediate point on the image
- Infinite rotation focusing on the closest image
- Better zoom in, zoom out effects

<br/>

**Challenges:**
- **GPU Computation time** will be a bottleneck for longer videos or many feedback loops per second
- **Depth Estimation** is a hard problem, the output should be accurate enough
- **The Shader** can't do magic, let's make it better

<sub>Eventually I'd like the Shaders pipeline and imagery to be part of ShaderFlow project. The one here might not be the most flexisble</sub>

<br/>

**Future:**
- **Keyframes:** Given many _keyframes_, interpolate prompts, depth maps, effects intensity
- Maybe some form of API and **User Interface** to make it easier to use
- **Music:** Generative music that maybe follows the video



<br/>
<br/>

# Installation

### Prebuilt Binaries
~~Grab the latest release for your platform [Here](https://github.com/BrokenSource/DepthFlow/releases/latest)~~ Prebuilt binaries are WIP

### Running from the Source Code
Follow instructions on our [Monorepo](https://github.com/BrokenSource/BrokenSource)



<br/>
<br/>

# Selecting PyTorch Acceleration Method
PyTorch has three different packages: CPU mode only, CUDA with NVIDIA GPUs and ROCm for AMD GPUs

Before running DepthFlow, select the PyTorch acceleration source package by modifying the `DepthFlow/pyproject.toml` file

Beware dragons:
- `CUDA`: Default installation, assumes you have a CUDA capable NVIDIA GPU and CUDA installed
- `ROCm`: Work in progress from AMD, might be unstable, should work in general
- `CPU`: Most compatible option, but slow for bigger inferences

You can reinstall the Python virtual environment with `broken depthflow --reinstall` to apply the changes


<br/>
<br/>

# License

## Personal use
- **User Generated Content**: CC-BY 4.0 License
- **Code**: AGPLv3-Only License

While we won't enforce punishments for failed attributions, we would appreciate if you could credit us

## Professional use
Want to use this for your company or comercially?

- Let's do something great together, contact us at [Broken Source Software](https://github.com/BrokenSource)
