import OpenGL.GL as gl
import numpy as np

# manage shaders


### V2 SHADERS, for n_scene_v2


cmap_v2_texture_vertex_shader_source = """
#version 330 core

layout(location = 0) in vec2 position;
layout(location = 1) in vec2 tex_coord;
layout(location = 2) in vec2 prev_tex_coord;

uniform mat4 projection_matrix;
uniform int tex_unit = 0; // 0 or 1 


out vec2 frag_tex_coord_one;
out vec2 frag_tex_coord_two;


void main()
{

    // current quad
    frag_tex_coord_one = tex_coord;
    // prev quad mapped to current
    frag_tex_coord_two = prev_tex_coord;
    gl_Position =  projection_matrix * vec4(position,0.0,1.0);
}
"""
# Fragment shader source code for drawing instances
cmap_v2_texture_fragment_shader_source = """
#version 330 core

uniform sampler1D color_map;
uniform sampler2D tex1;
uniform sampler2D tex2;
uniform float fading_factor = 0;
uniform int tex_unit = 0; // 0 or 1 
uniform float tex_mix_factor = 0; // from 0 to 1 
 
in vec2 frag_tex_coord_one;
in vec2 frag_tex_coord_two;

out vec4 fragColor;
float color_multiplier = 40;

vec3 gammaCorrection(vec3 color, float gamma) {
    return pow(color, vec3(1.0 * gamma));
}

void main() {
    float base_value;
    float prev_value;
    
    if(tex_unit==0){
         // current quad using tex1
         base_value = texture(tex1, frag_tex_coord_one).r; 
         prev_value = texture(tex2, frag_tex_coord_two).r; 
    }else{
         // current quad using tex2
         base_value = texture(tex2, frag_tex_coord_one).r; 
         prev_value = texture(tex1, frag_tex_coord_two).r; 
    }

    float intensified_color_value;
    if(base_value == -1){
        fragColor = vec4(0,0,0,0);
    }
    else{
        if(prev_value == 0 || prev_value == -1){
             intensified_color_value = clamp(base_value  * color_multiplier, 0, 1);
        }
        else{
            float mixed_color = mix(base_value, prev_value, tex_mix_factor);
            intensified_color_value = clamp(mixed_color  * color_multiplier, 0, 1);
        }
        vec3 color = texture(color_map, intensified_color_value).rgb;
        fragColor = vec4(color,fading_factor);
     }
}
"""

billboards_v2_vertex_shader_source = """
#version 330 core

layout(location = 0) in vec2 quad;
layout(location = 1) in vec2 tex_coord;
uniform sampler1D color_map;
uniform sampler2D billboard;
uniform sampler2D tex1;
uniform sampler2D tex2;
uniform int tex_unit = 0; // 0 or 1 

uniform int texture_width;
uniform int texture_height;

uniform int target_width;
uniform int target_height;

uniform vec2 position_offset = vec2(0.0, 0.0); 
uniform vec2 mouse_position = vec2(0.0, 0.0); 
uniform mat4 projection_matrix;
uniform int factor =1;
uniform float node_gap = 1;

float color_multiplier = 50;

out vec2 frag_tex_coord;

out vec4 color_value;
out vec4 default_color_value;
out float empty =0;
out float hover =0;
flat out vec4 hover_point;


void main()
{

    int selected_width = min(texture_width, target_width);
    int selected_height = min(texture_height, target_height);
    float x = gl_InstanceID % selected_width;
    float y = gl_InstanceID / selected_width;
    
    float value_one = texelFetch(tex1, ivec2(x, y), 0).r;
    float value_two = texelFetch(tex2, ivec2(x, y), 0).r;
    float value = (tex_unit > 0.5) ? value_two : value_one;
    float scaled_x = x * factor;
    float scaled_y = y * factor;
    
    vec2 instance_position = vec2(scaled_x, scaled_y);
    gl_Position = projection_matrix * vec4(quad.xy + instance_position + position_offset, 0.0, 1.0);
    frag_tex_coord = tex_coord;
    
    
    float intensified_color_value = clamp(value  * color_multiplier, 0, 1);
    color_value = texture(color_map, intensified_color_value);
    default_color_value = texture(color_map, 0);
    
    vec2 quad_center_in_world_space = instance_position + position_offset + vec2(0.5,0.5);
    float mouse_distance = distance(quad_center_in_world_space, mouse_position);
    if (mouse_distance < 0.5) {  
        hover = 1;
        hover_point = projection_matrix * vec4(mouse_position, 0, 1);
    } else {
        hover = 0;
        hover_point = vec4(0);  // Default or indicative value
    }
    if(value == -1)
    {
        empty = 1;
    }

}
"""
# Fragment shader source code for drawing instances
billboards_v2_fragment_shader_source = """
#version 330 core

uniform float fading_factor = 1.0f;
uniform sampler1D color_map;
uniform sampler2D billboard;
in vec4 color_value;
in vec4 default_color_value;
out vec4 frag_color;
in vec2 frag_tex_coord;
in float empty;
in float hover;
flat in vec4 hover_point;

void main()
{  
    if(empty == 1){
        frag_color = default_color_value;
    }
    else{
        vec2 center = vec2(0.5, 0.5);  // Center in texture coordinates
        float radius = 0.5;  // Smaller radius to keep the circle away from the edge

        float distanceFromCenter = distance(frag_tex_coord, center); // Calculate the distance
        float intensity = 1.0 - (distanceFromCenter / radius);  // Adjust intensity based on smaller radius
        intensity = clamp(intensity, 0.0, 1.0);  // Ensure intensity stays within valid range
        
        
        vec4 color = color_value;
        vec4 hover_color = vec4(0.0, 0.5, 1.0, 1.0);
        if(hover == 1){
            color = hover_color;
        }
        if (intensity > 0) {
            color = vec4(color.xyz * 3 * intensity, 1.0);  
        } else {
            color = default_color_value; 
        }
        frag_color = color;
    }
}
"""

layer_effects_vertex_shader_source = """
#version 330 core

layout(location = 0) in vec2 position;
layout(location = 1) in vec2 tex_coord;

uniform mat4 projection_matrix;

out vec2 frag_tex_coord;

void main()
{
    frag_tex_coord = tex_coord;
    vec4 quad_position = projection_matrix * vec4(position,0.0,1.0);
    gl_Position = quad_position;
}
"""
# Fragment shader source code for drawing instances
layer_effects_fragment_shader_source = """
#version 330 core

uniform float radius = 10;

in vec2 frag_tex_coord;

uniform vec2 quad_size;
 
out vec4 fragColor;



void main() {
    // Calculate the position of the fragment in pixels
    vec2 uv = frag_tex_coord * quad_size;
    
    // float radius = min(10,min(quad_size.x * 0.2, quad_size.y * 0.2));
    // float radius = edge_fade; // Radius of the rounded corners

    // Calculate the distance to the nearest edge in pixels
    float dist_to_left = uv.x;
    float dist_to_right = quad_size.x - uv.x;
    float dist_to_bottom = uv.y;
    float dist_to_top = quad_size.y - uv.y;

    // Determine the minimum distance to any edge
    float dist_to_edge = min(min(dist_to_left, dist_to_right), min(dist_to_bottom, dist_to_top));

    // Calculate the alpha value based on the distance to the edges
    float alpha_edge = smoothstep(0.0, radius, dist_to_edge);

    // Calculate the distance to the nearest corner
    vec2 corner_dist = min(min(uv, quad_size - uv), vec2(radius));
    float dist_to_corner = length(corner_dist - vec2(radius));

    // Calculate the alpha value based on the distance to the corners
    float alpha_corner = smoothstep(0.0, radius, dist_to_corner);

    // Combine the edge fade and rounded corner effects
    float alpha = min(alpha_edge, alpha_corner);
    alpha = clamp(0,0.7,1-alpha_corner);
    // Set the fragColor with the calculated alpha value
    fragColor = vec4(1.0, 0.0, 0.0, alpha);
}
"""


class NShader:
    def __init__(self):
        self.shader_program = None
        self.shader_version = None
        self.current_cmap_name = None
        self.colorMapTextureID = None
        self.billboardID = None

    def use(self):
        gl.glUseProgram(self.shader_program)

        # assign shader tex1 and tex2 to openGl texture. gl.GL_TEXTURE1 and gl.GL_TEXTURE2
        text_uniform = gl.glGetUniformLocation(self.shader_program, "color_map")
        gl.glUniform1i(text_uniform, 0)
        text_uniform = gl.glGetUniformLocation(self.shader_program, "billboard")
        gl.glUniform1i(text_uniform, 1)
        text_uniform1 = gl.glGetUniformLocation(self.shader_program, "tex1")
        gl.glUniform1i(text_uniform1, 2)
        text_uniform2 = gl.glGetUniformLocation(self.shader_program, "tex2")
        gl.glUniform1i(text_uniform2, 3)

    def update_color_map(self, cmap_name, color_values):
        if self.current_cmap_name == cmap_name:
            return
        # Generate and bind the texture
        if self.colorMapTextureID is None:
            self.colorMapTextureID = gl.glGenTextures(1)
        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(gl.GL_TEXTURE_1D, self.colorMapTextureID)

        # color_values = np.clip(color_values * 50, 0, 255)
        # Upload the 1D color map data
        gl.glTexImage1D(gl.GL_TEXTURE_1D, 0, gl.GL_RGB, 255, 0, gl.GL_RGB, gl.GL_UNSIGNED_BYTE, color_values)

        # Set texture parameters
        gl.glTexParameteri(gl.GL_TEXTURE_1D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_1D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_1D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
        self.current_cmap_name = cmap_name

    def update_cell_billboard(self):
        if self.billboardID is not None:
            return
            # Generate and bind the texture
        if self.billboardID is None:
            self.billboardID = gl.glGenTextures(1)
        gl.glActiveTexture(gl.GL_TEXTURE1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.billboardID)

        # color_values = np.clip(color_values * 50, 0, 255)
        # Upload the 1D color map data
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_R32F, 48, 48, 0, gl.GL_RED, gl.GL_FLOAT,
                        np.ones((48, 48), dtype=np.float32))

        # Set texture parameters
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)

    def update_projection(self, projection_matrix):
        projection_matrix_uniform = gl.glGetUniformLocation(self.shader_program, "projection_matrix")
        gl.glUniformMatrix4fv(projection_matrix_uniform, 1, gl.GL_FALSE, projection_matrix)

    def update_quad_matrix(self, quad_matrix):
        quad_matrix_uniform = gl.glGetUniformLocation(self.shader_program, "quad_matrix")
        gl.glUniformMatrix4fv(quad_matrix_uniform, 1, gl.GL_FALSE, quad_matrix)

    def update_fading_factor(self, factor):
        fading_factor = gl.glGetUniformLocation(self.shader_program, "fading_factor")
        gl.glUniform1f(fading_factor, factor)

    def select_texture(self, index):
        tex_unit = gl.glGetUniformLocation(self.shader_program, "tex_unit")
        gl.glUniform1i(tex_unit, index)

    def mix_textures(self, factor):
        tex_mix_factor = gl.glGetUniformLocation(self.shader_program, "tex_mix_factor")
        gl.glUniform1f(tex_mix_factor, factor)

    def update_texture_width(self, width):
        texture_width = gl.glGetUniformLocation(self.shader_program, "texture_width")
        gl.glUniform1i(texture_width, width)

    def update_texture_height(self, height):
        texture_height = gl.glGetUniformLocation(self.shader_program, "texture_height")
        gl.glUniform1i(texture_height, height)

    def update_target_width(self, width):
        target_width = gl.glGetUniformLocation(self.shader_program, "target_width")
        gl.glUniform1i(target_width, width)

    def update_target_height(self, height):
        target_height = gl.glGetUniformLocation(self.shader_program, "target_height")
        gl.glUniform1i(target_height, height)

    def update_details_factor(self, details_factor):
        factor = gl.glGetUniformLocation(self.shader_program, "factor")
        gl.glUniform1i(factor, details_factor)

    def update_position_offset(self, x1, y1):
        position_offset = gl.glGetUniformLocation(self.shader_program, "position_offset")
        gl.glUniform2f(position_offset, x1, y1)

    def update_details_factor_one(self, details_factor):
        factor = gl.glGetUniformLocation(self.shader_program, "factor_one")
        gl.glUniform1i(factor, details_factor)

    def update_details_factor_two(self, details_factor):
        factor = gl.glGetUniformLocation(self.shader_program, "factor_two")
        gl.glUniform1i(factor, details_factor)

    def update_size_one(self, x1, y1):
        size_one = gl.glGetUniformLocation(self.shader_program, "size_one")
        gl.glUniform2f(size_one, x1, y1)

    def update_size_two(self, x1, y1):
        size_two = gl.glGetUniformLocation(self.shader_program, "size_two")
        gl.glUniform2f(size_two, x1, y1)

    def update_position_offset_one(self, x1, y1):
        position_offset = gl.glGetUniformLocation(self.shader_program, "position_offset_one")
        gl.glUniform2f(position_offset, x1, y1)

    def update_position_offset_two(self, x1, y1):
        position_offset = gl.glGetUniformLocation(self.shader_program, "position_offset_two")
        gl.glUniform2f(position_offset, x1, y1)

    def update_mouse_position(self, x1, y1):
        mouse_position = gl.glGetUniformLocation(self.shader_program, "mouse_position")
        gl.glUniform2f(mouse_position, x1, y1)

    def update_quad_size(self, w, h):
        update_quad_size = gl.glGetUniformLocation(self.shader_program, "quad_size")
        gl.glUniform2f(update_quad_size, w, h)

    def update_node_gap(self, gap):
        node_gap = gl.glGetUniformLocation(self.shader_program, "node_gap")
        gl.glUniform1f(node_gap, gap)

    def update_radius(self, radius):
        node_gap = gl.glGetUniformLocation(self.shader_program, "radius")
        gl.glUniform1f(node_gap, radius)

    def compile_color_map_v2_texture_program(self):
        self.compile(cmap_v2_texture_vertex_shader_source, cmap_v2_texture_fragment_shader_source)

    def compile_billboards_v2_program(self):
        self.compile(billboards_v2_vertex_shader_source, billboards_v2_fragment_shader_source)

    def compile_effects_program(self):
        self.compile(layer_effects_vertex_shader_source, layer_effects_fragment_shader_source)

    def compile(self, vertex_shader_source, fragment_shader_source):
        self.shader_version = gl.glGetString(gl.GL_SHADING_LANGUAGE_VERSION)
        # print("Supported shader version:", self.shader_version.decode())

        # Create and compile the vertex shader
        vertex_shader = gl.glCreateShader(gl.GL_VERTEX_SHADER)
        gl.glShaderSource(vertex_shader, vertex_shader_source)
        gl.glCompileShader(vertex_shader)

        # Check the compilation status
        status = gl.glGetShaderiv(vertex_shader, gl.GL_COMPILE_STATUS)
        if status != gl.GL_TRUE:
            # Compilation failed, retrieve the error message
            error_message = gl.glGetShaderInfoLog(vertex_shader)
            print("Vertex Shader compilation failed:\n", error_message)

        # Create and compile the fragment shader
        fragment_shader = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)
        gl.glShaderSource(fragment_shader, fragment_shader_source)
        gl.glCompileShader(fragment_shader)

        # Check the compilation status
        status = gl.glGetShaderiv(fragment_shader, gl.GL_COMPILE_STATUS)
        if status != gl.GL_TRUE:
            # Compilation failed, retrieve the error message
            error_message = gl.glGetShaderInfoLog(fragment_shader)
            print("Fragment Shader compilation failed:\n", error_message)

        # Create the shader program and attach the shaders
        self.shader_program = gl.glCreateProgram()
        gl.glAttachShader(self.shader_program, vertex_shader)
        # gl.glAttachShader(self.shader_program, geometry_shader)
        gl.glAttachShader(self.shader_program, fragment_shader)
        gl.glLinkProgram(self.shader_program)

        # Check the linking status
        status = gl.glGetProgramiv(self.shader_program, gl.GL_LINK_STATUS)
        if gl.GL_TRUE != status:
            # Linking failed, retrieve the error message
            error_message = gl.glGetProgramInfoLog(self.shader_program)
            print("Shader program linking failed:\n", error_message)
