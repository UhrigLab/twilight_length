from plantcv import plantcv as pcv


def correct_exposure(img, roi):
    """
    Roi is a list of list containing the 4 points of the roi
    Each point is represented as [x, y]
    """
    if len(roi) != 1:
        raise Exception("Only one ROI is supported")
    if len(roi[0]) != 4:
        raise Exception("ROI must have exactly four points (a rectangle)")

    # Take first and third points in ROI
    p1 = roi[0][0]
    p3 = roi[0][2]

    w = abs(p3[0] - p1[0])
    h = abs(p3[1] - p1[1])

    # Corrects image based on color standard and stores output as corrected_img
    corrected_img = pcv.white_balance(img=img, mode='hist', roi=[int(p1[0]), int(p1[1]), int(w), int(h)])
    return corrected_img
