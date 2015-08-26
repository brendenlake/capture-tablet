import csv
import Tkinter as tk
import copy
import numpy as np

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
rd = lw/2.0 # radius of dot

def transform(strokes):
	for stk in strokes:
		stk[:,1] = -stk[:,1]
	rescale = sz
	for stk in strokes:
		stk += .5
		stk *= rescale
	return strokes

def flatten(strokes):
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
	print "average time resolution: " + str(int(np.mean(dtime))) + " ms"
	print "max time resolution: " + str(int(np.max(dtime))) + " ms"
	print "min time resolution: " + str(int(np.min(dtime))) + " ms"

	strokes = [stk[:,0:2] for stk in strokes]
	strokes = transform(strokes)
	return strokes

def render(strokes):
	# render strokes (output of load_traj.) and save as .ps file
	master = tk.Tk()
	w = tk.Canvas(master, width=sz, height=sz)
	w.pack()
	for stk in strokes:
		pos = stk[0][0:2]
		w.create_oval(pos[0]-rd, pos[1]-rd, pos[0]+rd, pos[1]+rd, fill="black")
		for idx in range(1,len(stk)):			
			new_pos = stk[idx][0:2]
			w.create_line(pos[0], pos[1], new_pos[0], new_pos[1], fill="black", width=lw)
			w.create_oval(new_pos[0]-rd, new_pos[1]-rd, new_pos[0]+rd, new_pos[1]+rd, fill="black")
			pos = copy.copy(new_pos)			

	filename = 'render'
	w.postscript(file=filename+'.ps',width=sz,height=sz)
	w.delete(tk.ALL)

if __name__ == "__main__":
	fn = 'strokes_handwritten/s1_latin_page_11.csv'
	strokes = load_traj(fn)
	render(strokes)

	## Check that the transform worked
	# ---
	# A = np.array([[-0.5,0.5],[0.5,0.5],[-0.5,-0.5],[0.5,-0.5]])
	# print A
	# B = transform([A])
	# print B