import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

def normalize(img,figure_size,ground_size):
	# 
	#   input : img as boolean numpy array, True means black pixel
	img = __crop(img)
	img = __resize(img,maxsize=figure_size)
	temp = np.array(img)
	assert max(temp.shape[0],temp.shape[1]) == figure_size
	img = __paste(img,sz=ground_size)
	assert np.all(__com(img) == np.array([img.shape[0]/2,img.shape[1]/2]))
	return img

def __crop(img):
	# Crop binary image to rectangle that contains minimal amount of white space
	#   input : img as boolean numpy array, True means black pixel
	

	on_count = np.sum(img.flatten()>=1e-4)
	off_count = np.sum(img.flatten()<1e-4)
	assert off_count > on_count

	xcord,ycord = np.nonzero(img)
	xmin = np.amin(xcord)
	ymin = np.amin(ycord)
	xmax = np.amax(xcord)
	ymax = np.amax(ycord)
	I = Image.fromarray(np.uint8(img))
	return I.crop((ymin,xmin,ymax+1,xmax+1))

def __resize(I,maxsize=100):
	# Resize an image so that the size of its longest side is 100, maintains aspect ratio
	#   I : PIL image
	ratio = maxsize / float(max(I.size[0],I.size[1]))
	size = [int(round(ratio*I.size[0])), int(round(ratio*I.size[1]))]
	return I.resize(size, Image.ANTIALIAS)

def __com(I):
	# Compute center of mass for all black pixels
	#   I : binary PIL image
	xcord,ycord = np.nonzero(I)
	return np.array([np.mean(xcord),np.mean(ycord)],dtype=int)

def __paste(I,sz=250):
	# Paste a smaller image I (rectangular) into the center of a sz x sx square image
	#   I : binary PIL image
	bg = np.zeros((sz,sz),dtype=bool)
	bg_center = np.array([sz/2,sz/2],dtype=int)
	xcord,ycord = np.nonzero(I)
	com = __com(I)
	offset = bg_center - com
	bg[xcord+offset[0],ycord+offset[1]] = True
	return bg


if __name__ == "__main__":
	
	# Parameters
	lensize = 77
	imgsize = 200

	# Check cropping functionality
	I = np.zeros((10,10)).astype(bool)
	I[1,1] = 1
	I[1,2] = 1
	I[1,3] = 1
	I[1,4] = 1
	I[2,1] = 1
	I[3,1] = 1
	I[4,1] = 1
	I[5,1] = 1
	I[6,1] = 1
	I2 = __crop(I)
	# assert np.all(I[1:7,1:5] == I2)
	print "Cropping test passed..."

	I3 = __resize(I2,maxsize=lensize)
	I4 = __paste(I3,sz=imgsize)

	I3 = np.array(I3)
	I4 = np.array(I4)

	assert max(I3.shape[0],I3.shape[1]) == lensize
	print "Resize test passed..."
	assert np.all(__com(I4) == np.array([I4.shape[0]/2,I4.shape[1]/2]))
	print "Pasting test passed..."

	plt.figure(1)
	plt.imshow(I4)
	plt.show()