from scipy import misc
from scipy.ndimage.morphology import binary_fill_holes
from scipy.stats.mstats import mode
import matplotlib.pyplot as plt
import numpy as np
import os
from skimage import morphology, measure
import cv2

# Parameters
dir_in = 'turtle' # directory with resized images (approx. 500 pixels in longest dimension)
threshold = 245
img_size = 7 # in inches
sub_scale = 0.5 # reduce size of primary object by this much

def load_images(mydir):
	list_fn = os.listdir(mydir)
	list_fn = [f for f in list_fn if f[0] != '.']
	return list_fn

# strip file type off the end of the name
def strip(s):
	indx = str.rfind(s,'.')
	return s[:indx]

# save a binary image (where 'true' is an inked pixel)
def save_bimg(fn,img):
	out = 1-img.astype(int)
	out = out * 255
	misc.imsave(fn,out)

# compute the size of the largest floating background object in an image (island of white or black pixels)
def largest_floater(img):
	labels = measure.label(img)
	component_sizes = np.bincount(labels.ravel())
	component_sizes = np.sort(component_sizes)
	if len(component_sizes)>2:
		min_object_size = component_sizes[-3]+1
	else:
		min_object_size = 8
	return min_object_size

# Main
files = load_images(dir_in)
dir_out = dir_in + '_shadow'
if not os.path.exists(dir_out):
    os.makedirs(dir_out)

# construct silhouette 
for f in files:
	
	# assert '.jpg' in f	
	base = strip(f)
	
	# read image
	im = misc.imread(dir_in + "/" + f, flatten=True)
	sz = im.shape

	# check that we don't have an odd number of pixels in either dim
	assert sz[0] % 2 == 0
	assert sz[1] % 2 == 0
	
	# make square image by padding with white space
	max_sz = max(sz)
	bg = 255 * np.ones((max_sz,max_sz))
	padx = (max_sz - sz[0])/2
	pady = (max_sz - sz[1])/2
	bg[padx:max_sz-padx,pady:max_sz-pady] = im
	im = bg
	
	# plot contour image
	fig = plt.figure(figsize=(img_size,img_size))	
	ax = fig.add_subplot(111)
	ax.set_aspect('equal')
	plt.contourf(im, levels=[0,threshold], colors='black', origin='image', antialiased=False)

	# fix axes so that the image has the proper scale
	plt.xlim([-max_sz*(1-sub_scale), max_sz*(1.0+(1-sub_scale))])
	plt.ylim([-max_sz*(1-sub_scale), max_sz*(1.0+(1-sub_scale))])
	plt.gca().xaxis.set_major_locator(plt.NullLocator())
	plt.gca().yaxis.set_major_locator(plt.NullLocator())
	plt.axis('off')
	
	# save image
	plt.savefig(dir_out + '/' + base +'.png', bbox_inches='tight', pad_inches=0)
	plt.close()

# post-processing of silhouette
files = load_images(dir_out)
for f in files:
	base = strip(f)
	
	# load binary image
	grayscale_img = misc.imread(dir_out + "/" + f, flatten=True)	
	img = grayscale_img < (255/2) # make binary image where 'true' indicates an inked pixel

	# remove stray objects in the image	
	img = morphology.remove_small_objects(img, min_size = largest_floater(img)).astype(bool)
	img = morphology.remove_small_objects(np.logical_not(img), min_size = largest_floater(img))
	img = np.logical_not(img)

	save_bimg(dir_out+'/'+base+'.png',img)