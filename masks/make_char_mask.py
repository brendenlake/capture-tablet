#  Coordinate system
#  -----
#  (0,0) ... (sz,0)
#  ...
#  ...
#  (0,sz) ... (sz,sz)\

from render import sz,render
import numpy as np
import shutil
import os

# make visual mask for characters

nmask = 5 # number of masks to create
nstroke = 45 # number of strokes
nstep = 100 # number of steps for each
init_stepsize = 2 # initial step size
sigma = 2 # parameter that controls wiggliness

def start_pt():
	# sample start point
	pt = np.random.uniform(0,sz,size=(2))
	dx = np.random.normal(0,init_stepsize,size=(2))
	return pt,dx

def next_pt(pt,dx):
	dx = dx + np.random.normal(0,sigma,size=(2)) # add jitter to derivative
	pt = pt + dx
	return pt,dx

def clip(stroke):
	# clip points in stroke [n x 2] that go out of bounds
	x = stroke[:,0]
	y = stroke[:,1]
	out = np.logical_or(x < 0,x > sz)
	out = np.logical_or(out,y < 0)
	out = np.logical_or(out,y > sz)
	stroke = np.delete(stroke,np.nonzero(out),axis=0)
	return stroke
	
def make_stroke():
	# sample a stroke
	stk = []
	pt,dx = start_pt()
	stk.append(pt)
	for i in range(nstep-1):
		pt,dx = next_pt(pt,dx)
		stk.append(pt)
	stk = np.array(stk)
	stk = clip(stk)
	return stk

def make_mask():
	strokes = []
	for i in range(nstroke):
		strokes.append(make_stroke())
	return strokes

if __name__ == "__main__":

	tempfile = 'render.png'
	
	for ix in range(nmask):
		new_name = 'c_mask_' + str(ix+1) + '.png'
		render(make_mask())
		shutil.copy(tempfile,new_name)
		os.remove(tempfile)