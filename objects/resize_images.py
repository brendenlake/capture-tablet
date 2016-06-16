import os, sys
import Image

#
# For each image in the input directory,..
#   resize and convert to JPG
#

mytype = 'butterfly'
dir_in = 'originals/' + mytype # input directory
dir_out = mytype 	 # output directory
maxsize = 500.0 	 # new size for the largest dimensino

if not os.path.exists(dir_out):
    os.makedirs(dir_out)

def load_images(mydir):
	list_fn = os.listdir(mydir)
	list_fn = [f for f in list_fn if f[0] != '.']
	return list_fn

def png_to_rgb(image, color=(255, 255, 255)):
    image.load()  # needed for split()
    background = Image.new('RGB', image.size, color)
    background.paste(image, mask=image.split()[3])  # 3 is the alpha channel
    return background

files = load_images(dir_in)
for infile in files:    
    outfile = os.path.splitext(dir_out + '/' + infile)[0] + ".jpg"
    try:
        im = Image.open(dir_in + '/' + infile)
        if im.mode == 'RGBA':
        	im = png_to_rgb(im)
        ratio = maxsize / float(max(im.size[0],im.size[1]))
        size = [int(ratio*im.size[0]), int(ratio*im.size[1])]
        if size[0] % 2 != 0:
        	size[0] += 1
        if size[1] % 2 != 0:
        	size[1] += 1
        im = im.resize(size, Image.ANTIALIAS)
        im.save(outfile, "JPEG")
    except IOError:
        print "cannot resize the file for '%s'" % infile