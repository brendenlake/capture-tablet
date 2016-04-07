import numpy as np

A = ['a','b','c','d']

np.random.shuffle(A)

B = A.pop()
print B
print A
