import numpy as np
import glob
import matplotlib.pyplot as plt
from scipy import misc

# Check that the mask does indeed cover the stimulus -- by overlaying it

chars = True # characters or objects

maskdir = '.'
if chars:
	imgdir = '../imgs_handwritten'
	fn_mask = np.random.choice(glob.glob(maskdir+'/c_mask_*.png'))
else:
	imgdir = '../final_set/objects_airplane'
	fn_mask = np.random.choice(glob.glob(maskdir+'/o_mask_*.png'))

fn_img = np.random.choice(glob.glob(imgdir+'/*.png'))

plt.figure(1)
plt.subplot(1,3,1)
IMG = misc.imread(fn_img,flatten=True)

plt.imshow(IMG, cmap='Greys_r')
frame = plt.gca()
plt.title('stimulus')
frame.axes.get_xaxis().set_visible(False)
frame.axes.get_yaxis().set_visible(False)

plt.subplot(1,3,2)
IMG = misc.imread(fn_mask,flatten=True)
plt.imshow(IMG,cmap='Greys_r')
frame = plt.gca()
plt.title('mask')
frame.axes.get_xaxis().set_visible(False)
frame.axes.get_yaxis().set_visible(False)

plt.subplot(1,3,3)
IMG1 = misc.imread(fn_img,flatten=True)
IMG2 = misc.imread(fn_mask,flatten=True)
IMG = np.minimum(IMG1,IMG2) 
plt.imshow(IMG,cmap='Greys_r')
plt.title('combined')
frame = plt.gca()
frame.axes.get_xaxis().set_visible(False)
frame.axes.get_yaxis().set_visible(False)

plt.show()