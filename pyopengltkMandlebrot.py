from OpenGL import GL
import OpenGL.GL.shaders
from pyopengltk import OpenGLFrame
import tkinter as tk
from tkinter import ttk
import numpy as np
import ctypes


#Shader compilation code from: https://github.com/jonwright/pyopengltk/blob/master/examples/shader_example.py

# Avoiding glitches in pyopengl-3.0.x and python3.4
def bytestr(s):
    return s.encode("utf-8") + b"\000"


# Avoiding glitches in pyopengl-3.0.x and python3.4
def compileShader(source, shaderType):
    """
    Compile shader source of given type
        source -- GLSL source-code for the shader
    shaderType -- GLenum GL_VERTEX_SHADER, GL_FRAGMENT_SHADER, etc,
        returns GLuint compiled shader reference
    raises RuntimeError when a compilation failure occurs
    """
    if isinstance(source, str):
        source = [source]
    elif isinstance(source, bytes):
        source = [source.decode('utf-8')]

    shader = GL.glCreateShader(shaderType)
    GL.glShaderSource(shader, source)
    GL.glCompileShader(shader)
    result = GL.glGetShaderiv(shader, GL.GL_COMPILE_STATUS)
    if not(result):
        # TODO: this will be wrong if the user has
        # disabled traditional unpacking array support.
        raise RuntimeError(
            """Shader compile failure (%s): %s""" % (
                result,
                GL.glGetShaderInfoLog(shader),
            ),
            source,
            shaderType,
        )
    return shader


vertex_shader_source = """
#version 330 core
layout (location = 0) in vec3 position;

void main()
{
    gl_Position = vec4(position, 1.0);
}
"""

mandlebrot_fragment_shader_source = """
#version 330 core
uniform vec2 resolution;
uniform vec2 L_pan;
uniform float scale;

out vec4 color;

vec2 f(vec2 c, vec2 z)
{
    return vec2(z.x*z.x - z.y*z.y, 2.0*z.x*z.y) + c;
}

vec3 HSV_to_RGB(vec3 c) {
    vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
    vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
    return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
}

void main()
{
    vec2 z = vec2(0.0, 0.0);
    vec2 coord = (((gl_FragCoord.xy - resolution.xy/2)/resolution.x) * 2.0);
    vec2 c = coord / scale + L_pan;

    int max_iter = 128;
    int i = 0;
    while (i < max_iter && length(z) < 2.0)
    {
        z = f(c, z);
        ++i;
    }

    if (i == max_iter)
    {
        color = vec4(0.0, 0.0, 0.0, 1.0);
    } else {
        float t = float(i) / float(max_iter);
        color = vec4(HSV_to_RGB(vec3(t+0.6f, 1.0, 1.0)), 1.0);
    }
}
"""


julia_fragment_shader_source = """
#version 330 core
uniform vec2 resolution;
uniform vec2 L_pan;
uniform vec2 R_pan;
uniform float scale;

out vec4 color;

vec2 f(vec2 c, vec2 z)
{
    return vec2(z.x*z.x - z.y*z.y, 2.0*z.x*z.y) + c;
}

vec3 HSV_to_RGB(vec3 c) {
    vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
    vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
    return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
}

void main()
{
    vec2 c = L_pan;
    vec2 coord = (((gl_FragCoord.xy - resolution.xy/2)/resolution.x) * 2.0);
    vec2 z = coord / scale + R_pan;

    int max_iter = 128;
    int i = 0;
    while (i < max_iter && length(z) < 2.0)
    {
        z = f(c, z);
        ++i;
    }

    if (i == max_iter)
    {
        color = vec4(0.0, 0.0, 0.0, 1.0);
    } else {
        float t = float(i) / float(max_iter);
        color = vec4(HSV_to_RGB(vec3(t+0.6f, 1.0, 1.0)), 1.0);
    }
}
"""

class ShaderFrame(OpenGLFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.julia_mode = False

        self.L_pan_x = 0.0
        self.L_pan_y = 0.0
        self.R_pan_x = 0.0
        self.R_pan_y = 0.0
        self.scale = 0.5
        self.julia_scale = 0.5

        self.L_last_x = None
        self.L_last_y = None
        self.R_last_x = None
        self.R_last_y = None

        self.bind_events()


    def initgl(self):
        GL.glClearColor(0.0, 0.0, 0.0, 1.0)
        if self.julia_mode:
            fragment_shader_source = julia_fragment_shader_source
        else:
            fragment_shader_source = mandlebrot_fragment_shader_source
        self.shader = GL.shaders.compileProgram(
                compileShader(vertex_shader_source, GL.GL_VERTEX_SHADER),
                compileShader(fragment_shader_source, GL.GL_FRAGMENT_SHADER)
            )

        self.vao = self.create_quad()
        self.u_resolution = GL.glGetUniformLocation(self.shader, bytestr('resolution'))
        self.u_L_pan = GL.glGetUniformLocation(self.shader, bytestr('L_pan'))
        if self.julia_mode:
            self.u_R_pan = GL.glGetUniformLocation(self.shader, bytestr('R_pan'))
        self.u_scale = GL.glGetUniformLocation(self.shader, bytestr('scale'))
        self.bind("<Configure>", self.resize)


    def create_quad(self):
        vertices = np.array([
            -1.0, -1.0, 0.0, #0
             1.0, -1.0, 0.0, #1
             1.0,  1.0, 0.0, #2
            -1.0,  1.0, 0.0  #3
        ], dtype=np.float32)

        indices = np.array([
            0, 1, 2, #First triangle
            2, 3, 0  #Second triangle
        ], dtype=np.uint32)

        vao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(vao)
        vbo = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL.GL_STATIC_DRAW)

        ebo = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, ebo)
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL.GL_STATIC_DRAW)

        GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, 3 * ctypes.sizeof(ctypes.c_float), ctypes.c_void_p(0))
        GL.glEnableVertexAttribArray(0)

        GL.glBindVertexArray(0)

        return vao

    def redraw(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        GL.glUseProgram(self.shader)
        GL.glUniform2f(self.u_resolution, self.width, self.height)
        GL.glUniform2f(self.u_L_pan, self.L_pan_x, self.L_pan_y)
        if self.julia_mode:
            GL.glUniform2f(self.u_R_pan, self.R_pan_x, self.R_pan_y)
            GL.glUniform1f(self.u_scale, self.julia_scale)
        else:
            GL.glUniform1f(self.u_scale, self.scale)
        GL.glBindVertexArray(self.vao)
        GL.glDrawElements(GL.GL_TRIANGLES, 6, GL.GL_UNSIGNED_INT, None)
        GL.glBindVertexArray(0)
        GL.glUseProgram(self.shader)


    def bind_events(self):
        self.bind("<Motion>", self.mouseMoved)
        self.bind("<Button-1>", self.L_mouseDown)
        self.bind("<ButtonRelease-1>", self.L_mouseUp)
        self.bind("<Button-3>", self.R_mouseDown)
        self.bind("<ButtonRelease-3>", self.R_mouseUp)
        self.bind("<MouseWheel>", self.mouseScroll) #windows
        self.bind("<Button-4>", self.mouseScroll) #linux
        self.bind("<Button-5>", self.mouseScroll) #linux
        self.bind("<Button-2>", self.toggle_julia_mode)

    def toggle_julia_mode(self, event):
        self.julia_mode = not self.julia_mode
        self.R_pan_x, self.R_pan_y = 0, 0
        self.initgl()
        self._display()

    def mouseMoved(self, event):
        moved = False

        if self.L_last_x is not None and self.L_last_y is not None:
            dx, dy = event.x - self.L_last_x, event.y - self.L_last_y
            self.L_pan_x -= (dx / self.width * 2) / self.scale
            self.L_pan_y += (dy / self.height * 2) / self.scale
            self.L_last_x, self.L_last_y = event.x, event.y
            moved = True

        if self.R_last_x is not None and self.R_last_y is not None:
            dx, dy = event.x - self.R_last_x, event.y - self.R_last_y
            self.R_pan_x -= (dx / self.width * 2) / self.julia_scale
            self.R_pan_y += (dy / self.height * 2) / self.julia_scale
            self.R_last_x, self.R_last_y = event.x, event.y
            moved = True

        if moved:
            self._display()

    def L_mouseDown(self, event):
        self.L_last_x, self.L_last_y = event.x, event.y

    def L_mouseUp(self, event):
        self.L_last_x, self.L_last_y = None, None

    def R_mouseDown(self, event):
        self.R_last_x, self.R_last_y = event.x, event.y

    def R_mouseUp(self, event):
        self.R_last_x, self.R_last_y = None, None

    def mouseScroll(self, event):
        delta = event.delta
        if self.julia_mode:
            if delta != 0:
                self.julia_scale += delta / 1200
            elif event.num == 4:
                self.julia_scale *= 1.1
            elif event.num == 5:
                self.julia_scale /= 1.1
        else:
            if delta != 0:
                self.scale += delta / 1200
            elif event.num == 4:
                self.scale *= 1.1
            elif event.num == 5:
                self.scale /= 1.1

        self._display()

    def resize(self, event):
        super().tkResize(event)
        self._display()


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.attributes("-fullscreen", True)

        self.fractalframe = ShaderFrame(self, width=1000, height=1000)
        self.fractalframe.pack(fill=tk.BOTH, expand=tk.YES)

        # self.create_menubar()

    # def create_menubar(self):
    #     self.menubar = tk.Menu(self)
    #     self.config(menu=self.menubar)
    #
    #     self.input_menu = tk.Menu(self.menubar, tearoff=0)
    #
    #     self.scale_var = tk.StringVar()
    #     self.scale_entry = ttk.Entry(self.input_menu, textvariable=self.scale_var)
    #     self.scale_entry.bind("")
    #     self.scale_entry.pack()
    #
    #     self.menubar.add_cascade(label="Input", menu=self.input_menu)



if __name__ == "__main__":
    root = App()
    root.mainloop()
