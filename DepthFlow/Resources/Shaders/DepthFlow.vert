// There's nothing happening out of the ordinary, I mean
#version 330

// Input rectangle render and stuv coordinates
in vec2 render_vertex;
in vec2 coords_vertex;

// Output stuv coordinates
out vec2 vertex_stuv;

// Basically do nothing, render a place on the screen
void main() {
    gl_Position = vec4(render_vertex, 0.0, 1.0);
    vertex_stuv = coords_vertex;
}
