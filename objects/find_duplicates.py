import glob
import numpy as np
from operator import itemgetter
from scipy.spatial.distance import cdist
from scipy.ndimage import imread
from scipy import misc
import matplotlib.pyplot as plt

# Manually check to see if any silhouttes in directory are identical
mydir = 'airplane_shadow'

def ModHausdorffDistance(itemA,itemB):
	# Modified Hausdorff Distance
	#
	# Input
	#  itemA : [n x 2] coordinates of "inked" pixels
	#  itemB : [m x 2] coordinates of "inked" pixels
	#
	#  M.-P. Dubuisson, A. K. Jain (1994). A modified hausdorff distance for object matching.
	#  International Conference on Pattern Recognition, pp. 566-568.
	#
	D = cdist(itemA,itemB)
	mindist_A = D.min(axis=1)
	mindist_B = D.min(axis=0)
	mean_A = np.mean(mindist_A)
	mean_B = np.mean(mindist_B)
	return max(mean_A,mean_B)

def LoadImgAsPoints(fn,sz=50):
	# Load image file and return coordinates of 'inked' pixels in the binary image
	# 
	# Output:
	#  D : [n x 2] rows are coordinates
	I = imread(fn,flatten=True)
	
	# resize and convert to binary
	I = misc.imresize(I,(sz,sz))
	mx = np.amax(I)
	I = I < mx/2.0

	(row,col) = I.nonzero()
	D = np.array([row,col])
	D = np.transpose(D)
	D = D.astype(float)
	n = D.shape[0]
	mean = np.mean(D,axis=0)
	for i in range(n):
		D[i,:] = D[i,:] - mean
	return D

files = glob.glob(mydir+'/*.png')
images = []
D = []
for f in files:
	I = imread(f,flatten=True)
	images.append(I)
	d = LoadImgAsPoints(f)
	D.append(d)

N = len(D)
dist = np.eye(N)*100
for i in range(N):
	print "image " + str(i) + " of " + str(N)
	for j in range(i+1,N):
		dist[i,j] = ModHausdorffDistance(D[i],D[j])
dist = dist + np.transpose(dist)

thresh = np.amin(dist)*2
flag = []
for i in range(N):
	for j in range(i+1,N):
		if dist[i,j] < thresh:
			flag.append({'i':i,'j':j,'dist':dist[i,j]})

flag = sorted(flag, key=itemgetter('dist'))
print "flagged " + str(len(flag)) + " items"
for f in flag:
	i = f['i']
	j = f['j']
	dist = f['dist']

	plt.figure(1,figsize=(16,16))
	plt.subplot(121)
	plt.imshow(images[i],cmap='Greys_r')
	plt.title(files[i]+' '+str(dist))
	frame = plt.gca()
	frame.axes.get_xaxis().set_visible(False)
	frame.axes.get_yaxis().set_visible(False)
	plt.subplot(122)
	plt.imshow(images[j],cmap='Greys_r')
	plt.title(files[j])	
	frame = plt.gca()
	frame.axes.get_xaxis().set_visible(False)
	frame.axes.get_yaxis().set_visible(False)
	plt.show()