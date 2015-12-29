import os
import sys

#
# Rename a subject's files
#
# Use case: python subject_renumber.py X Y
#
#  X is the original subject number
#  Y is the new subject number
# 

dir_imgs = 'imgs_handwritten'
dir_stks = 'strokes_handwritten'

assert len(sys.argv)== 3
x = sys.argv[1]
y = sys.argv[2]
print "*** Renaming Subject " + x + " as " + "Subject " + y + " ***"

# Rename the images
prefix = 's'+x
for f in os.listdir(dir_imgs):
	if f.startswith(prefix):
		oldname = dir_imgs+'/'+f
		newname = dir_imgs+'/'+f.replace(prefix, 's'+y)
		print oldname + " -> " + newname
		if not os.path.isfile(newname):
			os.rename(oldname,newname)			
		else:
			raise ValueError("file " + newname + " already exists.")

# # Rename the stroke data
# prefix = 's'+x
# for f in os.listdir(dir_stks):
# 	if f.startswith(prefix):
# 		oldname = dir_stks+'/'+f
# 		newname = dir_stks+'/'+f.replace(prefix, 's'+y)
# 		print oldname + " -> " + newname
# 		if not os.path.isfile(newname):
# 			os.rename(oldname,newname)			
# 		else:
# 			raise ValueError("file " + newname + " already exists.")