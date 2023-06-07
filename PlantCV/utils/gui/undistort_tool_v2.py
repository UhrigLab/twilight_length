import cv2
import numpy as np

fx_cx_fy_cy_MAX = 2000
fx_cx_fy_cy_MIN = 900

k1_k2_k3_k4_MAX = 10
k1_k2_k3_k4_MIN = -10


def null(x):
    pass

def undistort_tool(image_path: str, scale: float, fx: float, cx: float, fy: float, cy: float, k1: float, k2: float, k3: float, k4: float):

    distorted_img = cv2.imread(image_path)
    resized_original = cv2.resize(distorted_img, (0, 0), fx=scale, fy=scale)
    cv2.imshow('Original Image', resized_original)
    cv2.namedWindow('Undistortion Parameters')


    cv2.createTrackbar('fx', 'Undistortion Parameters', fx, fx_cx_fy_cy_MAX, null)
    cv2.createTrackbar('cx', 'Undistortion Parameters', cx, fx_cx_fy_cy_MAX, null)
    cv2.createTrackbar('fy', 'Undistortion Parameters', fy, fx_cx_fy_cy_MAX, null)
    cv2.createTrackbar('cy', 'Undistortion Parameters', cy, fx_cx_fy_cy_MAX, null)

    cv2.createTrackbar('k1', 'Undistortion Parameters', k1, k1_k2_k3_k4_MAX, null)
    cv2.createTrackbar('k2', 'Undistortion Parameters', k2, k1_k2_k3_k4_MAX, null)
    cv2.createTrackbar('k3', 'Undistortion Parameters', k3, k1_k2_k3_k4_MAX, null)
    cv2.createTrackbar('k4', 'Undistortion Parameters', k4, k1_k2_k3_k4_MAX, null)

    cv2.setTrackbarMin('fx', 'Undistortion Parameters', fx_cx_fy_cy_MIN)
    cv2.setTrackbarMin('cx', 'Undistortion Parameters', fx_cx_fy_cy_MIN)
    cv2.setTrackbarMin('fy', 'Undistortion Parameters', fx_cx_fy_cy_MIN)
    cv2.setTrackbarMin('cy', 'Undistortion Parameters', fx_cx_fy_cy_MIN)

    cv2.setTrackbarMin('k1', 'Undistortion Parameters', k1_k2_k3_k4_MIN)
    cv2.setTrackbarMin('k2', 'Undistortion Parameters', k1_k2_k3_k4_MIN)
    cv2.setTrackbarMin('k3', 'Undistortion Parameters', k1_k2_k3_k4_MIN)
    cv2.setTrackbarMin('k4', 'Undistortion Parameters', k1_k2_k3_k4_MIN)


    while True:

        fx = cv2.getTrackbarPos('fx', 'Undistortion Parameters')
        cx = cv2.getTrackbarPos('cx', 'Undistortion Parameters')
        fy = cv2.getTrackbarPos('fy', 'Undistortion Parameters')
        cy = cv2.getTrackbarPos('cy', 'Undistortion Parameters')
        k1 = cv2.getTrackbarPos('k1', 'Undistortion Parameters')
        k2 = cv2.getTrackbarPos('k2', 'Undistortion Parameters')
        k3 = cv2.getTrackbarPos('k3', 'Undistortion Parameters')
        k4 = cv2.getTrackbarPos('k4', 'Undistortion Parameters')

        K = np.array([[fx, 0.0, cx],
                    [0.0, fy, cy],
                    [0.0, 0.0, 1.0]]) # camera intrinsic matrix
        

        D = np.array([k1, k2, k3, k4], dtype=np.float64) # camera distortion matrix

        balance = 1
        dim = (distorted_img.shape[1], distorted_img.shape[0])

        new_K = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(K, D, dim, np.eye(3), balance=balance)
        map1, map2 = cv2.fisheye.initUndistortRectifyMap(K, D, np.eye(3), new_K, dim, cv2.CV_32FC1)
        # and then remap:
        undistorted = cv2.remap(distorted_img, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)

        resized = cv2.resize(undistorted, (0, 0), fx=scale, fy=scale)
        cv2.imshow('Undistorted Image', resized)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    cv2.destroyAllWindows()
