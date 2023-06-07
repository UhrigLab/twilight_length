import cv2
import numpy as np
from plantcv import plantcv as pcv

# define a null callback function for Trackbar
def null(x):
    pass

def hsv_tool(images, lower=[0,0,0], upper=[180,255,255], mask_fill=0, mode="path", img_scale=1.0):
    hl = lower[0]
    sl = lower[1]
    vl = lower[2]
    hh = upper[0]
    sh = upper[1]
    vh = upper[2]

    hsv_range = cv2.imread("hue_and_sat.png")
    hsv_range_w, hsv_range_h = hsv_range.shape[1], hsv_range.shape[0]
    hsv_range = cv2.resize(hsv_range, (hsv_range_w, hsv_range_h))

    hsv_visual = cv2.imread("hsv_visual.png")
    hsv_visual_w, hsv_visual_h = hsv_visual.shape[1], hsv_visual.shape[0]
    hsv_visual = cv2.resize(hsv_visual, (hsv_visual_w*2, hsv_visual_h*2))
    


    for image in images:
        if mode == "path":
            img = cv2.imread(image)
        elif mode == "array":
            img = image.copy()
        else:
            raise Exception("Mode must be 'path' or 'array'")
        
        scaled = cv2.resize(img, None, fx=img_scale, fy=img_scale)

        # convert BGR image to HSV
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # create six trackbars for H, S and V - lower and higher masking limits 
        cv2.namedWindow('HSV')
        # arguments: trackbar_name, window_name, default_value, max_value, callback_fn
        cv2.createTrackbar("HL", "HSV", hl, 180, null)
        cv2.createTrackbar("HH", "HSV", hh, 180, null)
        cv2.createTrackbar("SL", "HSV", sl, 255, null)
        cv2.createTrackbar("SH", "HSV", sh, 255, null)
        cv2.createTrackbar("VL", "HSV", vl, 255, null)
        cv2.createTrackbar("VH", "HSV", vh, 255, null)
        cv2.createTrackbar("Mask Fill", "HSV", mask_fill, 100, null)

        while True:
            # read the Trackbar positions
            hl = cv2.getTrackbarPos('HL','HSV')
            hh = cv2.getTrackbarPos('HH','HSV')
            sl = cv2.getTrackbarPos('SL','HSV')
            sh = cv2.getTrackbarPos('SH','HSV')
            vl = cv2.getTrackbarPos('VL','HSV')
            vh = cv2.getTrackbarPos('VH','HSV')
            mask_fill = cv2.getTrackbarPos('Mask Fill','HSV')
            lower = [hl, sl, vl]
            upper = [hh, sh, vh]

            # create a manually controlled mask
            # arguments: hsv_image, lower_trackbars, higher_trackbars
            mask = cv2.inRange(hsv, np.array([hl, sl, vl]), np.array([hh, sh, vh]))
            try:
                mask = pcv.fill(mask, mask_fill)
            except:
                pass
            mask = cv2.resize(mask, None, fx=img_scale, fy=img_scale)
            # derive masked image using bitwise_and method
            final = cv2.bitwise_and(scaled, scaled, mask=mask)

            # display image, mask and masked_image 
            cv2.imshow('Original', scaled)
            cv2.imshow('Mask', mask)
            cv2.imshow('Masked Image', final)
            cv2.imshow('Hue and Saturation', hsv_range)
            cv2.imshow('HSV Visual', hsv_visual)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("\n")
                print("HSV UPPER = [{}, {}, {}]".format(hh, sh, vh))
                print("HSV LOWER = [{}, {}, {}]".format(hl, sl, vl))
                print("MASK FILL = {}".format(mask_fill))
                print("\n")
                break
        cv2.destroyAllWindows()
        return lower, upper, mask_fill

