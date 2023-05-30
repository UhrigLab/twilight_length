from plantcv import plantcv as pcv


def check_rois(img, rois):
    """
    Inputs: 
    * img - numpy array of image
    * rois - list of rois to check

    Outputs: 
    * image with rois drawn on it

    Discussion:
    * Useful to plot the output and view if all the rois are good
    """
    old_debug = pcv.params.debug
    pcv.params.debug = None
    img_out = img.copy()
    for roi in rois:
        roi_contour, roi_hierarchy, img_out = pcv.roi.custom(img=img_out, 
                                                    vertices=roi)
    pcv.params.debug = old_debug
    return img_out   
