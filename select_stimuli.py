import glob
import re
import os
import shutil

#
# Aggregate the collected images and exclude those listed in exclude.txt
#
# output : files in folder imgs_by_type
#

imgs_by_type = 'selected' # directory to store aggregated images
exclude = 'exclude.txt' # particular images we want to exclude
imgs_printed = 'imgs_printed' # images we want participant to copy
imgs_handwritten = 'imgs_handwritten' # folder to store drawn images

if not os.path.exists(imgs_by_type): os.makedirs(imgs_by_type)

# get all excluded images
fid = open(exclude, 'rb')
d = {}
for line in fid:
	mylist = line.rstrip().split(',')
	key = mylist[0]
	d[key] = mylist[1:]

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
		
	count = 1
	dstdir = os.path.join(imgs_by_type,b)
	os.makedirs(dstdir)
	for s in range(1,nsubj+1):
		if str(s) in s_exclude: # pass if we don't want this image
			continue			
		srcfile = imgs_handwritten + '/s' + str(s) + '_' + b + '.png'			
		shutil.copy(srcfile, dstdir)
		# count += 1

# # make the plots
# nsubj = get_nsubj()
# nrow = math.ceil(math.sqrt(nsubj))
# plt.figure(1,figsize=(10,10))
# for b in bases:

# 	# get images to exclude for this character
# 	s_exclude = []
# 	if b in d.keys():
# 		s_exclude = d[b]
		
# 	plt.clf()
# 	count = 1
# 	for s in range(1,nsubj+1):
# 		if str(s) in s_exclude: # pass if we don't want this image
# 			continue
# 		plt.subplot(nrow, nrow, count)
# 		fn = imgs_handwritten + '/s' + str(s) + '_' + b + '.png'
# 		IMG = Image.open(fn)
# 		plt.imshow(IMG)
# 		frame = plt.gca()
# 		frame.axes.get_xaxis().set_visible(False)
# 		frame.axes.get_yaxis().set_visible(False)
# 		plt.title(str(s))
# 		count += 1
		
# 	plt.savefig(imgs_by_type + '/' + b + '.pdf')