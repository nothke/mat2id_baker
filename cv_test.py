import cv2
import numpy as np

img = np.zeros((256, 256, 3, 0), np.uint8)

cv2.line(img, (0, 0), (256, 256), (255, 0, 0, 255), 1)
kernel = np.ones((5,5),np.uint8)
#img = cv2.dilate(img, kernel, iterations=1)

r, g, b, a = cv2.split(img)
img = cv2.merge((r, g, b))

cv2.imshow("Image", img)
cv2.waitKey(0)
cv2.destroyAllWindows()