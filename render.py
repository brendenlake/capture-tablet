import csv
import Tkinter as tk
import copy
import numpy as np
import os
import glob
import shutil
from numpy.matlib import repmat

#
# Return pen sequence from csv file as image.
#

# Initial coordinate system when read from file
#  (-0.5,0.5) ... (0.5,0.5)
#  ...
#  ...
#  (-0.5,-0.5) ... (0.5,-0.5)

# New coordinate system for rendering
#  (0,0) ... (sz,0)
#  ...
#  ...
#  (0,sz) ... (sz,sz)\
#
# Thus, transform is first flip y-axis (multiply by -1).
# Then add 0.5 to all coordinates
# Then multiply by sz
#
sz = 250 # size of canvas
lw = 8.0 # line width
rd = lw/2.025
# rd = lw/2.0 # radius of dot

do_normalize = True # do we want to normalize images?
figure_size = 125 # size of the largest dimension of the image (keeping aspect ratio)

def __resize(strokes,maxsize):
	# normalize character so that longest side is maxsize long
	v = flatten(strokes)
	if v.shape[0]==1: # if we only have length one
		return strokes
	vx = v[:,0]
	vy = v[:,1]	
	rx = np.amax(vx)-np.amin(vx)
	ry = np.amax(vy)-np.amin(vy)
	ratio = maxsize / float(max(rx,ry))
	new_strokes = np.copy(strokes)
	new_strokes = [s*ratio for s in new_strokes]
	assert np.isclose(np.amax(np.amax(v*ratio,axis=0)-np.amin(v*ratio,axis=0)),maxsize)
	return new_strokes

def __center(strokes):
	# center image so that center of mass (in trajectory space) is at center of the image
	v = flatten(strokes)
	m = np.mean(v,axis=0)
	bg_center = np.array([sz/2,sz/2],dtype=float)
	offset = bg_center - m
	new_strokes = []
	for s in strokes:
		N = s.shape[0]
		new_strokes.append(s + repmat(offset,N,1))
	assert np.all(np.isclose(np.mean(flatten(new_strokes),axis=0),bg_center))
	return new_strokes

def transform(strokes):
	for stk in strokes:
		stk[:,1] = -stk[:,1]
	rescale = sz
	for stk in strokes:
		stk += .5
		stk *= rescale
	return strokes

def flatten(strokes):
	if strokes==[]:
		return np.array([])
	overall = strokes[0]
	for stk in strokes[1:]:
		overall = np.append(overall,stk,axis=0)
	return overall

def load_traj(fn):
	# Load pen sequence from csv file
	# return as list of trajectories
	strokes = []
	with open(fn,'rb') as f:
		reader = csv.reader(f)
		for line in reader:
			stk = [item[1:-1].split(', ') for item in line]			
			assert len(stk[0])==3 # make sure format is [x,y,t]
			strokes.append(np.array(stk,dtype='float'))

	# check the time resolution
	dtime = []
	for stk in strokes:
		time = stk[0][2]
		for idx in range(1,len(stk)):	
			new_time = stk[idx][2]
			dtime.append(new_time-time)
			time = new_time
	dtime = np.array(dtime)
	
	# print "average time resolution: " + str(int(np.mean(dtime))) + " ms"
	# print "max time resolution: " + str(int(np.max(dtime))) + " ms"
	# print "min time resolution: " + str(int(np.min(dtime))) + " ms"

	strokes = [stk[:,0:2] for stk in strokes]
	strokes = transform(strokes)
	if do_normalize and len(strokes)>0:
		strokes = __resize(strokes,figure_size)
		strokes = __center(strokes)
	return strokes

def render(strokes):
	# render strokes (output of load_traj.) and save as .ps file
	master = tk.Tk()
	w = tk.Canvas(master, width=sz, height=sz)
	w.pack()
	for stk in strokes:
		pos = stk[0][0:2]
		w.create_oval(pos[0]-rd, pos[1]-rd, pos[0]+rd, pos[1]+rd, fill="black", width=0)
		for idx in range(1,len(stk)):			
			new_pos = stk[idx][0:2]
			w.create_line(pos[0], pos[1], new_pos[0], new_pos[1], fill="black", width=lw)
			w.create_oval(new_pos[0]-rd, new_pos[1]-rd, new_pos[0]+rd, new_pos[1]+rd, fill="black", width=0)
			pos = copy.copy(new_pos)			

	filename = 'render'
	w.postscript(file=filename+'.ps',width=sz,height=sz)
	w.delete(tk.ALL)
	os.system('convert -flatten ' + filename+'.ps ' + filename+'.png')
	os.remove(filename+'.ps')
	return filename+'.png'

if __name__ == "__main__":
	# fn = 'strokes_handwritten/s1_aaa_practice_01.csv'
	# strokes = load_traj(fn)
	# render(strokes)

	# re-render all of the iamges
	indir = 'strokes_handwritten'
	outdir = 'imgs_rerender'
	if not os.path.exists(outdir): os.makedirs(outdir)
	files = glob.glob(indir+'/*.csv')
	for idx,f in enumerate(files):
		new_name = outdir + '/' + f[len(indir)+1:]
		new_name = new_name.replace('.csv','.png')
		if not os.path.isfile(new_name):
			print "rendering " + str(idx) + " of " + str(len(files))
			tempfile = render(load_traj(f))			
			shutil.copy(tempfile,new_name)
			os.remove(tempfile)

	## Check that the transform worked
	# ---
	# A = np.array([[-0.5,0.5],[0.5,0.5],[-0.5,-0.5],[0.5,-0.5]])
	# print A
	# B = transform([A])
	# print B