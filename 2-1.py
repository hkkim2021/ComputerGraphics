import glfw
from OpenGL.GL import*
import numpy as np

ptype = GL_LINE_LOOP
vertexs = None

def KeyCallback(window, key, scancode, action, mods):
    global ptype
    if key == glfw.KEY_1 and action == glfw.PRESS:
        ptype = GL_POINTS
    elif key == glfw.KEY_2 and action == glfw.PRESS:
        ptype = GL_LINES
    elif key == glfw.KEY_3 and action == glfw.PRESS:
        ptype = GL_LINE_STRIP
    elif key == glfw.KEY_4 and action == glfw.PRESS:
        ptype = GL_LINE_LOOP
    elif key == glfw.KEY_5 and action == glfw.PRESS:
        ptype = GL_TRIANGLES
    elif key == glfw.KEY_6 and action == glfw.PRESS:
        ptype = GL_TRIANGLE_STRIP
    elif key == glfw.KEY_7 and action == glfw.PRESS:
        ptype = GL_TRIANGLE_FAN
    elif key == glfw.KEY_8 and action == glfw.PRESS:
        ptype = GL_QUADS
    elif key == glfw.KEY_9 and action == glfw.PRESS:
        ptype = GL_QUAD_STRIP
    elif key == glfw.KEY_0 and action == glfw.PRESS:
    	ptype = GL_POLYGON
    elif key == glfw.KEY_ESCAPE and action == glfw.PRESS:
        glfw.set_window_should_close(window = window, value = glfw.TRUE)
        
def makeVertex():
    global vertexs
    a = np.linspace(0, np.pi*2, num=13)
    vList = []
    for th in a :              
        vList.append((np.cos(th),np.sin(th)))
    
    vList.pop()
    vertexs = np.array(vList)
        
def render():
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    glBegin(ptype)
    for vertex in vertexs:
        glVertex2fv(vertex)
    glEnd()
    

def main():
    if not glfw.init():
        return
    
    window = glfw.create_window(480,480,"2021005923-2-1",None,None)
    if not window:
        glfw.terminate()
        return
    
    glfw.make_context_current(window)
    
    glfw.set_key_callback(window,KeyCallback)
    glfw.swap_interval(1)
    makeVertex()
    
    while not glfw.window_should_close(window):
        glfw.poll_events()
        render()
        glfw.swap_buffers(window)
    
    glfw.terminate()

if __name__ == "__main__":
    main()
