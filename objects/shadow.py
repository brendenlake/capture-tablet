from scipy import misc
from scipy.ndimage.morphology import binary_fill_holes
from scipy.stats.mstats import mode
import scipy.ndimage as ndimage
import matplotlib.pyplot as plt
import numpy as np
import os
from skimage import morphology, measure
import cv2
import sys
sys.path.append("../")
from normalize import normalize


# Parameters
if len(sys.argv) <= 1:
	dir_in = 'cat' # directory with resized images (approx. 500 pixels in longest dimension)
else:
	dir_in = sys.argv[1]
threshold = 10 # the modal value subtracted by this number is used to separate figure from ground (assuming white background)
img_size = 7 # size of contour plot in inches (shouldn't matter)
sub_scale = 0.5 # reduce size of primary object by this much
outsize = 250 # size of the output image
rename = True # rename the files?
do_normalize = True # should we normalize the images?
figure_size = 125 # size of the largest dimension of the image (keeping aspect ratio)

def load_images(mydir):
	list_fn = os.listdir(mydir)
	list_fn = [f for f in list_fn if f[0] != '.']
	return list_fn

def tostr(x):
	# convert number to string with leading 0
	x = str(x)
	if len(x) == 1:
		x = '0' + x
	return x

# strip file type off the end of the name
def strip(s):
	indx = str.rfind(s,'.')
	return s[:indx]

# save a binary image (where 'true' is an inked pixel)
def save_bimg(fn,img):
	out = 1-img
	out = out * 255
	out = misc.imresize(out,(outsize,outsize))
	misc.imsave(fn,out.astype(int))

# save a grayscale image 
def save_gscale_img(fn,grayimg,mask_erode,mask_dilate):
	mask_erode = mask_erode.astype(float)
	mask_dilate = mask_dilate.astype(float)
	grayimg = grayimg.astype(float)

	# include all pixels 'on' in eroded binary shadow
	# exclude all pixels 'off' in dilated binary shadow
	img = grayimg 
	img = np.maximum(img,mask_erode)
	img = np.minimum(img,mask_dilate)
	if do_normalize:
		img = normalize(img,figure_size,outsize)		
		out = 1-img
		out = out * 255
		out = out.astype(int)
	else:
		out = 1-img
		out = out * 255
		out = out.astype(int)
		out = misc.imresize(out,(outsize,outsize))
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
	bg_color,_ = mode(im,axis=None)
	max_sz = max(sz)
	bg = bg_color * np.ones((max_sz,max_sz))
	padx = (max_sz - sz[0])/2
	pady = (max_sz - sz[1])/2
	bg[padx:max_sz-padx,pady:max_sz-pady] = im
	im = bg
	
	# plot contour image
	fig = plt.figure(figsize=(img_size,img_size))
	ax = fig.add_subplot(111)
	ax.set_aspect('equal')	
	plt.contourf(im, levels=[0,bg_color-threshold], colors='black', origin='image', antialiased=True)

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
for idx,f in enumerate(files):
	base = strip(f)
	
	# load binary image
	grayscale_img = misc.imread(dir_out + "/" + f, flatten=True)	
	img = grayscale_img < (255/2) # make binary image where 'true' indicates an inked pixel
	
	# smoothing applied to the grayscale imgae
	grayscale_img = 1-(grayscale_img.astype(float) / 255.0)
	grayscale_img = ndimage.gaussian_filter(grayscale_img, sigma=(1, 1), order=0)

	# remove stray floaters and holes in the image
	img = np.copy(img)
	img = morphology.remove_small_objects(img, min_size = largest_floater(img)).astype(bool)
	img = morphology.remove_small_objects(np.logical_not(img), min_size = largest_floater(img))
	img = np.logical_not(img)

	# compute erosion and expansion so we can detect the border of the silhouette
	selem = morphology.disk(2)
	mask_erode = morphology.binary_erosion(img, selem)
	mask_dilate = morphology.binary_dilation(img, selem)
	
	# compute final silhouette
	fn_out = dir_out+'/'+base+'.png'
	os.remove(fn_out)
	if rename:
		fn_out = dir_out+'/item'+tostr(idx+1)+'_'+dir_in+'.png'
	save_gscale_img(fn_out,grayscale_img,mask_erode,mask_dilate)