import glob
import os
import numpy as np
from scipy import misc
from normalize import __crop
import matplotlib.pyplot as plt

outdir = 'simple_stats'
if not os.path.exists(outdir): os.makedirs(outdir)
if not os.path.exists(outdir+'/objects'): os.makedirs(outdir+'/objects')
if not os.path.exists(outdir+'/selected'): os.makedirs(outdir+'/selected')
dirs = []
dirs += ['objects/airplane_shadow','objects/butterfly_shadow','objects/car_shadow','objects/horse_shadow']
cimgs = os.listdir('selected')
cimgs = ['selected/'+c for c in cimgs]
dirs += cimgs

for d in dirs:
	images = glob.glob(d + '/*.png')

	hvec = []
	wvec = []
	for fn in images:
		img = misc.imread(fn,flatten=True)
		img = img < 250
		img = __crop(img)
		height,width = img.shape
		hvec.append(height)
		wvec.append(width)

	plt.figure(1,figsize=(8,4))
	plt.clf()
	plt.subplot(121)
	plt.title(d)
	plt.hist(wvec)
	plt.xlabel('width (pixels)')
	plt.xlim([0,250])
	plt.subplot(122)
	plt.hist(hvec)
	plt.xlabel('height (pixels)')
	plt.xlim([0,250])
	plt.savefig(outdir+'/'+d+'.pdf')