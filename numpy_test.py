import numpy as np
from PIL import Image

img = Image.new('RGB', (4,4), (0,0,0)) # (1,2,3))
image_arr = np.array(img)

image_arr[1,1] = (3,3,3)

# [column, row, pixel]
arr = image_arr[:,:,1]


cond = np.full((4,4,3), [1, 1, 1])

rolld = np.roll(image_arr, 1, axis=1)
comp = np.maximum(rolld, image_arr)
rolld = np.roll(image_arr, -1, axis=1)
comp = np.maximum(rolld, comp)
rolld = np.roll(image_arr, 1, axis=0)
comp = np.maximum(rolld, comp)
rolld = np.roll(image_arr, -1, axis=0)
comp = np.maximum(rolld, comp)


print(image_arr)
print("extracted: ")
print(arr)
print("\ncond: \n")
print(cond)
print("\rolld: \n")
print(rolld)
print("\ncomp: \n")
print(comp)