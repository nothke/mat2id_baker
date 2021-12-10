import pyximport; pyximport.install()
import texture_dilate as td
import numpy as np
from PIL import Image, ImageDraw
import time


def process_classic(arr, size, inflate_iterations):
    # arr is RGBA image array
    # size is dimension of the image

    for _ in range(inflate_iterations):
        src = arr.copy()

        for y in range(size):
            for x in range(size):
                bail = False

                # skip if pixel is opaque
                if arr[x, y, 3] > 5:
                    continue

                startx = x-1 if x > 0 else 0
                endx = x+2 if x < size-1 else size-1

                starty = y-1 if y > 0 else 0
                endy = y+2 if y < size-1 else size-1

                for yi in range(starty, endy):
                    for xi in range(startx, endx):
                        # skip if center pixel
                        if xi == x and yi == y:
                            continue

                        # when an opaque pixel is encountered, color this pixel the same
                        if src[xi, yi, 3] > 5:
                            arr[x, y] = src[xi, yi]
                            bail = True
                            continue

                    if bail:
                        continue

                if bail:
                    continue

    return arr


size = 256
img = Image.new('RGBA', (size, size), color=(0, 0, 0, 0))
draw = ImageDraw.Draw(img)

draw.line((6, 3, 6, 9), fill="red")
draw.line((3, 6, 9, 6), fill="red")

arr = np.array(img)

t = time.time()
arr = process_classic(arr, size, 1)
print("Dilation with numpy took %8.4f seconds" % (time.time() - t))

t = time.time()
arr = td.process(arr, size, 3)
print("Dilation with cython took %8.4f seconds" % (time.time() - t))

img = Image.fromarray(arr)
img.save("test.png")
# img.show()
