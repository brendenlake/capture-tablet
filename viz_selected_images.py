import glob
import re
import os
import matplotlib.pyplot as plt
import math
from PIL import Image

#
# Display all the instances of each object type
# in the folder of selected stimuli
#
# output : files in folder imgs_by_type
#

selected = 'selected'

# get name of folder for each character
mydirs = os.listdir(selected)
mydirs = [d for d in mydirs if '.' not in d]

imgs_by_type = 'selected_by_type' # directory to store aggregated images

if not os.path.exists(imgs_by_type): os.makedirs(imgs_by_type)
for d in mydirs:
	
	mydir = os.path.join(selected,d)
	
	if os.path.exists(mydir):
		fns = glob.glob(mydir+'/*.png')
		plt.figure(1,figsize=(10,10))
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