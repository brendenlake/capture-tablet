import glob
import re
import os
import matplotlib.pyplot as plt
import math
from PIL import Image

#
# Display all the instances of each object type
#
# output : files in folder imgs_by_type
#

# dirs = ['balloon','bowlingpin','butterfly','horseshoe']
dirs = ['cat','butterfly']
imgs_by_type = 'objects_by_type' # directory to store aggregated images

if not os.path.exists(imgs_by_type): os.makedirs(imgs_by_type)
for d in dirs:
	mydir = d + '_shadow'
	if os.path.exists(d):
		fns = glob.glob(mydir+'/*.png')
		plt.figure(1,figsize=(30,30))
		plt.clf()
		nrow = math.ceil(math.sqrt(len(fns)))
		for s,fn in enumerate(fns):
			plt.subplot(nrow, nrow, s+1)			
			IMG = Image.open(fn).convert('LA')
			plt.imshow(IMG)
			frame = plt.gca()
			frame.axes.get_xaxis().set_visible(False)
			frame.axes.get_yaxis().set_visible(False)
			plt.title(str(s+1))			
		plt.savefig(imgs_by_type + '/' + d + '.pdf')