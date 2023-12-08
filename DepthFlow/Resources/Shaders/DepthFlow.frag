
// ------------------------------------------------------------------------------------------------|

// Get the clamped depth of a image (no overshooting) based on iFocus
// - Zero depth means the object does not move
float get_depth(vec2 stuv, sampler2D depth) {
    return iFocus - draw_image(depth, stuv).r;
}

// Depth-Layer displacement for a pixel, composed of the camera displacement times max
// camera displacement (iParallaxFactor) times the depth of the pixel (zero should not move)
vec2 displacement(vec2 stuv, sampler2D depth) {
    return iPosition * get_depth(stuv, depth) * iParallaxFactor;
}

// ------------------------------------------------------------------------------------------------|

// Apply the DepthFlow parallax effect into some image and its depth map
//
// - The idea of how this shader works is that we search, on the opposite direction a pixel is
//   supposed to "walk", if some other pixel should be in front of *us* or not.
//
// - B's texture is A's on the future, so the parallax direction must be the inverse (send -1)
//
vec4 image_parallax(vec2 stuv, sampler2D image, sampler2D depth) {

    // vec2 resolution = textureSize(image, 0);
    // vec2 scale = vec2(resolution.y / resolution.x, 1.0);
    // vec2 gluv = stuv2gluv(stuv);
    // gluv *= scale;
    // stuv = gluv2stuv(gluv);

    // The direction the pixel walk is the camera displacement itself
    vec2 direction = iPosition * iParallaxFactor;

    // Initialize the parallax space with the original stuv
    vec2 parallax_uv = stuv + displacement(stuv, depth);

    // FIXME: Do you know how to code shaders better than me?
    // Fixme: Could you implement the step() pixel size anti-aliasing and better efficiency?
    for (float i=0; i<length(direction); i=i+0.001) {
        vec2 walk_stuv          = stuv + direction*i;
        vec2 other_displacement = displacement(walk_stuv, depth);

        if (i < length(other_displacement)) {
            parallax_uv = walk_stuv;
        }
    }

    // Sample the texture on the parallax space
    return draw_image(image, parallax_uv);
}

// ------------------------------------------------------------------------------------------------|

void main() {
    vec2 uv = zoom(stuv, 0.95 + 0.05*iZoom, vec2(0.5));
    fragColor = image_parallax(uv, image, depth);
}
