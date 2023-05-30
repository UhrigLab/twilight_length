import cv2
import numpy as np


def undistort(distorted_img, intrinsic_matrix, distortion_coeffs):
    K = intrinsic_matrix
    D = distortion_coeffs

    balance = 1
    dim = (distorted_img.shape[1], distorted_img.shape[0])

    new_K = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(K, D, dim, np.eye(3), balance=balance)
    map1, map2 = cv2.fisheye.initUndistortRectifyMap(K, D, np.eye(3), new_K, dim, cv2.CV_32FC1)
    # and then remap:
    undistorted = cv2.remap(distorted_img, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    return undistorted
