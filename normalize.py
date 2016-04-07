import numpy as np
from scipy import misc
import matplotlib.pyplot as plt
# from PIL import Image

def normalize(img,figure_size,ground_size):
	#   input : img as a float boolean numpy array (bounded between 0 and 1, where 1 is "black")
	assert_valid_format(img)
	img = __crop(img)
	assert_valid_format(img,check_polarity=False)
	img = __resize(img,maxsize=figure_size)
	assert_valid_format(img,check_polarity=False)
	assert max(img.shape[0],img.shape[1]) == figure_size
	img = __paste(img,sz=ground_size)
	assert np.all(__com(img) == np.array([img.shape[0]/2,img.shape[1]/2]))
	return img

def assert_valid_format(img,check_polarity=True):
	# check the format of the image...
	mx = np.amax(img)
	mn = np.amin(img)
	assert float(mx) <= 1.0
	assert float(mn) >= 0.0
	assert np.issubdtype(img.dtype, np.float) | np.issubdtype(img.dtype, np.bool_)
	if check_polarity:
		on_count = np.sum(img.flatten()>=1e-4)
		off_count = np.sum(img.flatten()<1e-4)
		assert off_count > on_count

def __crop(img):
	# Crop image to rectangle that contains minimal amount of white space
	xcord,ycord = np.nonzero(img)
	xmin = np.amin(xcord)
	ymin = np.amin(ycord)
	xmax = np.amax(xcord)
	ymax = np.amax(ycord)
	return img[xmin:xmax+1,ymin:ymax+1]
	# convert to PIL format
	# I = Image.fromarray( np.uint8(255.0*(1-img)) )
	# return I.crop((ymin,xmin,ymax+1,xmax+1))

def __resize(img,maxsize=100):
	# Resize an image so that the size of its longest side is 100, maintains aspect ratio
	#   img : numpy image
	ratio = maxsize / float(max(img.shape[0],img.shape[1]))
	size = [int(round(ratio*img.shape[0])), int(round(ratio*img.shape[1]))]	
	if np.issubdtype(img.dtype, np.float):
		out = misc.imresize(img,size,mode='F')
	elif np.issubdtype(img.dtype, np.bool_):		
		out = misc.imresize(img.astype(float),size,mode='F')
		out = out.astype(bool)
	else:
		assert False
	return out
	# return I.resize(size, Image.ANTIALIAS)

def __com(img):
	# Compute center of mass for all black pixels
	#   img : numpy image
	img = img / float(np.sum(img.flatten()))	
	
	# sz = img.shape
	# m = np.array([0.0,0.0])
	# for x in range(sz[0]):
	# 	for y in range(sz[1]):
	# 		m = m + np.array([x,y]) * img[x,y]
	# m = np.round(m).astype(int)

	xcord,ycord = np.nonzero(img)
	weight = img[xcord,ycord].astype(float)
	m1 = np.array([np.dot(xcord,weight),np.dot(ycord,weight)])
	m1 = np.round(m1).astype(int)
	return m1

	# xcord,ycord = np.nonzero(I)
	# return np.array([np.mean(xcord),np.mean(ycord)],dtype=int)

def __paste(img,sz=250):
	# Paste a smaller image img (rectangular) into the center of a sz x sx square image
	#   img : numpy image
	bg = np.zeros((sz,sz),dtype=img.dtype)
	bg_center = np.array([sz/2,sz/2],dtype=int)
	xcord,ycord = np.nonzero(img)
	com = __com(img)
	offset = bg_center - com
	img = np.asarray(img)
	bg[xcord+offset[0],ycord+offset[1]] = img[xcord,ycord]
	return bg

if __name__ == "__main__":
	
	# Parameters
	lensize = 75
	imgsize = 215

	# Check cropping functionality
	I = np.zeros((10,10)).astype(bool)
	I[1,1] = 0.5
	I[1,2] = 1
	I[1,3] = 1
	I[1,4] = 1
	I[2,1] = 1
	I[3,1] = 1
	I[4,1] = 1
	I[5,1] = 1
	I[6,1] = 0.5
	
	I2 = __crop(I)
	assert np.all(I[1:7,1:5] == I2)
	
	print "Cropping test passed..."

	I3 = __resize(I2,maxsize=lensize)
	I4 = __paste(I3,sz=imgsize)
	I3 = np.array(I3)
	I4 = np.array(I4)

	# assert I4.dtype == I.dtype
	assert max(I3.shape[0],I3.shape[1]) == lensize
	print "Resize test passed..."
	assert np.all(__com(I4) == np.array([I4.shape[0]/2,I4.shape[1]/2]))
	print "Pasting test passed..."

	I4 = normalize(I,lensize,imgsize)
	plt.figure(1)
	plt.imshow(1-I4,cmap='Greys_r')
	plt.show()