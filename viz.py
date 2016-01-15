import glob
import re
import os
import matplotlib.pyplot as plt
import math
from PIL import Image

#
# Display all the instances of each character type
#
# output : files in folder imgs_by_type
#

imgs_by_type = 'stimuli_by_type' # directory to store aggregated images
imgs_printed = 'imgs_printed' # images we want participant to copy
imgs_handwritten = 'imgs_handwritten' # folder to store drawn images

if not os.path.exists(imgs_by_type): os.makedirs(imgs_by_type)

def get_nsubj():
	# return the number of subjects
	fns = glob.glob(imgs_handwritten+'/*.png')
	myid = []
	for f in fns:
	    m = re.match(imgs_handwritten+'/s(\d+).*.png', f, re.M|re.I)
	    g = m.groups()
	    myid.append(g[0])
	myid = [int(i) for i in myid]
	myid = list(set(myid))
	return max(myid)

# get all of the unique character names
fns = glob.glob(imgs_printed+'/*.png')
bases = []
for f in fns:
	m = re.match(imgs_printed+'/(.*).png', f, re.M|re.I)
	g = m.groups()
	base = g[0]
	bases.append(base)

# make the plots
nsubj = get_nsubj()
nrow = math.ceil(math.sqrt(nsubj))
for b in bases:
	plt.figure(1,figsize=(10,10))
	for s in range(1,nsubj+1):
		plt.subplot(nrow, nrow, s)
		fn = imgs_handwritten + '/s' + str(s) + '_' + b + '.png'
		IMG = Image.open(fn)
		plt.imshow(IMG)
		frame = plt.gca()
		frame.axes.get_xaxis().set_visible(False)
		frame.axes.get_yaxis().set_visible(False)
		plt.title(str(s))
	# plt.show()
	plt.savefig(imgs_by_type + '/' + b + '.pdf')

