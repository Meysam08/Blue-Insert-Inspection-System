import cv2
import numpy as np

img = cv2.imread("phase 1/sample.jpg")
img = cv2.resize(img, (600, 900))

hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

def on_mouse(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        pixel = hsv[y, x]
        print(f"HSV at ({x},{y}) = {pixel}")

cv2.imshow("Click on BLUE area", img)
cv2.setMouseCallback("Click on BLUE area", on_mouse)

cv2.waitKey(0)
cv2.destroyAllWindows()


