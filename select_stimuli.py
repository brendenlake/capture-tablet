import glob
import re
import os
import shutil
import numpy as np
from normalize import normalize
from scipy import misc
np.random.seed(seed=0)

#
# Aggregate the collected images and exclude those listed in exclude.txt
#
# output : files in folder imgs_by_type
#

figure_size = 125 # size of the largest dimension of the image (keeping aspect ratio)
background_size = 250 # total image size

imgs_by_type = 'selected' # directory to store aggregated images
exclude = 'exclude.txt' # particular images we want to exclude
imgs_printed = 'imgs_printed' # images we want participant to copy
imgs_handwritten = 'imgs_rerender' # folder to store drawn images
# imgs_handwritten = 'imgs_handwritten' # folder to store drawn images
nstim_per_category = 40 # number of examples we want for each category

if not os.path.exists(imgs_by_type): os.makedirs(imgs_by_type)

# get all excluded images
fid = open(exclude, 'rb')
d = {}
for line in fid:
	mylist = line.rstrip().split(',')
	key = mylist[0]
	vals = mylist[1:]
	vals = [int(v) for v in vals]
	d[key] = vals

def tostr(x):
	# convert number to string with leading 0
	x = str(x)
	if len(x) == 1:
		x = '0' + x
	return x

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

# aggregate the character we want
nsubj = get_nsubj()
for b in bases:

	# get images to exclude for this character
	s_exclude = []
	if b in d.keys():
		s_exclude = d[b]
	
	# exclude another random subset of images to get to the right number
	s_include = [i for i in range(1,nsubj+1) if i not in s_exclude]
	N = len(s_include)
	np.random.shuffle(s_include)
	while len(s_include) > nstim_per_category:
		s_exclude.append(s_include.pop())
	assert len(s_include) <= nstim_per_category
		
	#
	count = 1
	dstdir = os.path.join(imgs_by_type,b)
	os.makedirs(dstdir)
	for s in s_include:

		# copy file			
		srcfile = imgs_handwritten + '/s' + str(s) + '_' + b + '.png'					
		shutil.copy(srcfile, dstdir)

		# normalize stimuli
		srcfile = dstdir + '/s' + str(s) + '_' + b + '.png'
		img = misc.imread(srcfile, flatten=True)
		img = np.array(img,dtype=float)
		mx = np.amax(img.flatten())
		img = img / float(mx)
		img = 1-img
		img = normalize(img,figure_size,background_size)
		misc.imsave(srcfile,1-img)

		# rename file
		dstfile = dstdir + '/item' + tostr(count) + '_' + b + '.png'					
		os.rename(srcfile, dstfile)

		count += 1