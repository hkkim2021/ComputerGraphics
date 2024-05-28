import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

gComposeM=np.identity(3)
cur_x=0
cur_r=0
def keyCallback(window, key, scancode, action, mods):
	global cur_x
	global cur_r
	global gComposeM
	
	newM=np.identity(3)
	
	if action == glfw.PRESS or action == glfw.REPEAT:
		if key == glfw.KEY_Q:
			cur_x=-0.1
			newM=np.array([[1.,0.,cur_x],
				    [0.,1.,0.],
				    [0.,0.,1.]])
			gComposeM=newM@gComposeM
		elif key == glfw.KEY_E:
			cur_x=0.1
			newM=np.array([[1.,0.,cur_x],
				    [0.,1.,0.],
				    [0.,0.,1.]])
			gComposeM=newM@gComposeM
		elif key == glfw.KEY_A:
			cur_r=10
			newM=np.array([[np.cos(np.radians(cur_r)),-np.sin(np.radians(cur_r)),0.],
				    [np.sin(np.radians(cur_r)),np.cos(np.radians(cur_r)),0.],
				    [0.,0.,1.]])
			gComposeM=gComposeM@newM
		elif key == glfw.KEY_D:
			cur_r=-10
			newM=np.array([[np.cos(np.radians(cur_r)),-np.sin(np.radians(cur_r)),0.],
				    [np.sin(np.radians(cur_r)),np.cos(np.radians(cur_r)),0.],
				    [0.,0.,1.]])
			gComposeM=gComposeM@newM
		elif key == glfw.KEY_1:
			gComposeM=np.identity(3)
		elif key == glfw.KEY_ESCAPE and action == glfw.PRESS:
			glfw.set_window_should_close(window=window, value=glfw.TRUE)
			
def render(T):
	glClear(GL_COLOR_BUFFER_BIT)
	glLoadIdentity()
	# draw cooridnate
	glBegin(GL_LINES)
	glColor3ub(255, 0, 0)
	glVertex2fv(np.array([0.,0.])) 
	glVertex2fv(np.array([1.,0.]))
	glColor3ub(0, 255, 0)
	glVertex2fv(np.array([0.,0.])) 
	glVertex2fv(np.array([0.,1.]))
	glEnd()
	# draw triangle
	glBegin(GL_TRIANGLES)
	glColor3ub(255, 255, 255)
	glVertex2fv( (T @ np.array([.0,.5,1.]))[:-1] )
	glVertex2fv( (T @ np.array([.0,.0,1.]))[:-1] )
	glVertex2fv( (T @ np.array([.5,.0,1.]))[:-1] )
	glEnd()		
	
def main():
	if not glfw.init():
		return
	window=glfw.create_window(480,480,"2021005923-3-1", None, None)
	if not window:
		glfw.terminate()
		return
	glfw.make_context_current(window)
	glfw.swap_interval(1)
	
	while not glfw.window_should_close(window):
		glfw.poll_events()
		glfw.set_key_callback(window, keyCallback)
		render(gComposeM)
		
		glfw.swap_buffers(window)
	
	glfw.terminate()
	
if __name__ == "__main__":
	main()
			   			   
			   