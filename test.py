import numpy as np

A = np.random.rand(5,2)
print A

x = np.zeros((5),dtype=bool)

x[2] = True

# B = np.delete(A,np.nonzero(x),axis=0)
B = np.delete(A,x,axis=0)
print B