import numpy as np
import cv2


def mask_green(image, upper_HSV : list, lower_HSV : list):
    # Returns a binary image with green pixels as white, and the rest black.
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    upper = np.array(upper_HSV)
    lower = np.array(lower_HSV)
    
    mask = cv2.inRange(hsv, lower, upper)
    return mask
