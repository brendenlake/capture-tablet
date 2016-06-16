#  Coordinate system
#  -----
#  (0,0) ... (sz,0)
#  ...
#  ...
#  (0,sz) ... (sz,sz)\

import render
import numpy as np
import shutil
import os

# make visual mask for characters

nmask = 5 # number of masks to create
ndots = 150 # number of dots

render.lw = 35.0
render.rd = render.lw/2.025

def start_pt():
	# sample start point
	pt = np.random.uniform(0,render.sz,size=(1,2))
	return pt
	
def make_stroke():
	# sample a stroke
	stk = start_pt()
	return stk

def make_mask():
	strokes = []
	for i in range(ndots):
		strokes.append(make_stroke())
	return strokes

if __name__ == "__main__":

	tempfile = 'render.png'
	
	for ix in range(nmask):
		new_name = 'o_mask_' + str(ix+1) + '.png'
		render.render(make_mask())
		shutil.copy(tempfile,new_name)
		os.remove(tempfile)