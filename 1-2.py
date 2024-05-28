import numpy as np

M=np.arange(2,27)
print(M)
print("\n")

M=M.reshape(5,5)
print(M)
print("\n")

M[1:4, 1:4]=0
print(M)
print("\n")

M=M@M
print(M)
print("\n")

M=M[0, 0:5]
M=np.sqrt(M@M)
print(M)