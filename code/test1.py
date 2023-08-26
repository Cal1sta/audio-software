import numpy as np
import matplotlib.pyplot as plt

a = np.array([[1,2],[3,4],[5,6]])
print("a",a)

b = np.array([7,8,9])
print("b",b)

c = zip(a,b)
print("c=zip(a,b)",list(c))
