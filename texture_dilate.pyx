import numpy as np

def process(arr, size, inflate_iterations):
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