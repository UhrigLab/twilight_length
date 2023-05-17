#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import argparse
from plantcv import plantcv as pcv
import cv2
import datetime


### Parse command-line arguments
def options():
    print('Parsing Options in workflowzone')
    parser = argparse.ArgumentParser(description="Imaging processing with opencv")
    parser.add_argument("-i", "--image", help="Input image file.", required=True)
    parser.add_argument("-r","--result", help="Result file.", required= True )
    parser.add_argument("-o", "--outdir", help="Output directory for image files.", required=True)
    parser.add_argument("-n", "--names", help="path to txt file with names of genotypes to split images into", required =False)
    parser.add_argument("-D", "--debug", help="Turn on debug, prints intermediate images.", action=None)
    args = parser.parse_args()
    return args

# Undistortion
DIM=(2592, 1944)
K=np.array([[1813.0215301956628, 0.0, 1182.3714436756943], [0.0, 1816.6475234144523, 976.6858512745583], [0.0, 0.0, 1.0]])
D=np.array([[-0.17123530115641178], [1.3367500066404934], [-5.103138626612192], [6.450284979351176]])
def undistort(img):
    h,w = img.shape[:2]
    map1, map2 = cv2.fisheye.initUndistortRectifyMap(K, D, np.eye(3), K, DIM, cv2.CV_16SC2)
    return cv2.remap(img, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)


def main():
#    class options:
#        def __init__(self):
#            self.image = "2021-06-06T104239_rgb.png"
#            self.debug = None#"plot"
#            self.writeimg= False 
#            self.result = "./multi_plant_tutorial_results"
#            self.outdir = "./images"
#            self.names = 'genotypes.txt'
            
    # Set up log files - not yet working since I want to do it in plantCV style
    
    #    if not os.path.exists(self.outdir):
    #        os.mkdir(self.outdir)
    #        print(self.outdir,'folder created')
    #    else:
    #        print(self.outdir, 'folder already exists')
    #    self.filename = self.dirName+'/'+time.strftime('%Y-%m-%d')+'-plantCV-log.csv'
    #    if not os.path.isfile(filename):
    #        print("No Log File Exists -> Making new one")
    #        header_string = 'Timestamp,'
    #        for i in range[24]
    #            header_string += str(i+1)+','
    #        header_string += '\n'
    #        with open(self.filename, 'w') as logfile:
    #            logfile.write(header_string)
    #    else:
    #        print('Log file exists, appending')
    
    # Get options
    args = options()

    # Set variables
    pcv.params.debug = args.debug        # Replace the hard-coded debug with the debug flag
    img_file = args.image     # Replace the hard-coded input image with image flag
    
    
    # Set debug to the global parameter 
    pcv.params.debug = args.debug
    
    
    # In[3]:
    
    
    # Read image
    img, path, filename = pcv.readimage(args.image)
    print(filename)
    img = undistort(img)
    timestamp = datetime.datetime.strptime(filename[6:-4],'%Y-%m-%d--%H-%M-%S')
    #timestamp = datetime.datetime.strptime(filename[0:-8],'%Y-%m-%dT%H%M%S')
    if args.debug == "plot":
        pcv.plot_image(img)
    
    
    # In[4]:
    
    
    if np.average(img) < 55:
        pcv.fatal_error("Night Image")
    else:
        pass
    
    
    # In[5]:
    
    
    # STEP 2: Normalize the white color so you can later
    # compare color between images.
    # Inputs:
    #   img = image object, RGB color space
    #   roi = region for white reference, if none uses the whole image,
    #         otherwise (x position, y position, box width, box height)
    
    # white balance image based on white toughspot
    
    img1 = pcv.white_balance(img,roi=(710, 380, 20, 20))             
    
    
    # In[6]:
    
    
    # STEP 3: Rotate the image slightly so the plants line up with 
    # the grid that we'll add in a later step
    # Inputs:
    #   img = image object, RGB color space
    #   rotation_deg = Rotation angle in degrees, can be negative, positive values 
    #                  will move counter-clockwise 
    #   crop = If True then image will be cropped to orginal image dimensions, if False
    #          the image size will be adjusted to accommodate new image dimensions 
    
    rotate_img = pcv.rotate(img1, 181, True)
    
    
    # In[7]:
    
    
    # STEP 4: Shift image. This step is important for clustering later on.
    # For this image it also allows you to push the green raspberry pi camera
    # out of the image. This step might not be necessary for all images.
    # The resulting image is the same size as the original.
    # Inputs:
    #   img    = image object
    #   number = integer, number of pixels to move image
    #   side   = direction to move from "top", "bottom", "right","left"
    
    shift1 = pcv.shift_img(rotate_img, 1, 'top')
    img1 = shift1
    
    
    # In[8]:
    
    
    # STEP 5: Convert image from RGB color space to LAB color space
    # Keep only the green-magenta channel (grayscale)
    # Inputs:
    #    img     = image object, RGB color space
    #    channel = color subchannel ('l' = lightness, 'a' = green-magenta , 'b' = blue-yellow)
    
    a = pcv.rgb2gray_lab(img1, 'a')
    
    
    # In[9]:
    
    
    # STEP 6: Set a binary threshold on the saturation channel image
    # Inputs:
    #    img         = img object, grayscale
    #    threshold   = threshold value (0-255)
    #    max_value   = value to apply above threshold (usually 255 = white)
    #    object_type = light or dark
    #       - If object is light then standard thresholding is done
    #       - If object is dark then inverse thresholding is done
    
    img_binary = pcv.threshold.binary(a, 122, 255, 'dark')
    #                                     ^
    #                                     |
    #                                 adjust this value
    
    
    # In[10]:
    
    
    # STEP 7: Fill in small objects (speckles)
    # Inputs:
    #    img  = image object, grayscale. img will be returned after filling
    #    size = minimum object area size in pixels (integer)
    
    fill_image = pcv.fill(img_binary, 80)
    #                                  ^
    #                                  |
    #                         adjust this value
    
    
    # In[11]:
    
    
    # STEP 8: Dilate so that you don't lose leaves (just in case)
    # Inputs:
    #    img    = input image
    #    ksize  = integer, kernel size
    #    i      = iterations, i.e. number of consecutive filtering passes
    
    dilated = pcv.dilate(fill_image, 2, 1)
    
    
    # In[12]:
    
    
    # STEP 9: Find objects (contours: black-white boundaries)
    # Inputs:
    #    img  = image that the objects will be overlayed
    #    mask = what is used for object detection
    
    id_objects, obj_hierarchy = pcv.find_objects(img1, dilated)
    
    
    # In[13]:
    
    
    # STEP 10: Define multiple regions of interest
    # Make a grid of ROIs
    coord=[]
    # Choose the plants you want here:
    for j in range(7):
        for i in range(4):
            if i<4:
                coord.append((990+i*238,255+j*242))
            else:
                coord.append((370+90+i*242,660+j*240))
    rois1, roi_hierarchy1 = pcv.roi.multi(img=img1, coord=coord, radius=63)
    
    
    # In[14]:
    
    
    # STEP 11 (optional): Get the size of the marker. First make a region of interest around one of 
    # the toughspots. Then use `report_size_marker_area`. 
    
    #marker_contour, marker_hierarchy = pcv.roi.rectangle(img1, 1340, 1040, 60, 60)
    
    
    # In[15]:
    
    
    # Inputs:
    #   img - RGB or grayscale image to plot the marker object on 
    #   roi_contour = A region of interest contour 
    #   roi_hierarchy = A region of interest contour heirarchy 
    #   marker = 'define' (default) or 'detect', if 'define' then you set an area, if 'detect'
    #            it means you want to detect within an area 
    #   objcolor = Object color is 'dark' (default) or 'light', is the marker darker or lighter than 
    #               the background?
    #   thresh_channel = 'h', 's', 'v' for hue, saturation, or value. Default set to None. 
    #   thresh = Binary threshold value (integer), default set to None 
    
    #   
    #analysis_images = pcv.report_size_marker_area(img1, marker_contour, marker_hierarchy, marker='detect', 
                                                  #objcolor='light', thresh_channel='v', thresh=254)
    
    
    # In[16]:
    
    
    # STEP 12: Keep objects that overlap with the ROI, now looping
    img_copy = np.copy(img1)
    import csv
    # Where to save the list of longest_path and area results
    save_path_area = 'results/results_area.csv'
    save_path_perimeter='results/results_perimeter.csv'
    save_path_estimated_object_count='results/results_estimated_object_count.csv'
    #save_path_longest = 'results/results_longest.csv'
    #save_path_green = 'results/results_green.csv'
    
    
    # Plant number counts across each row, starting at 0 in the upper left
# 0  1  2  3  
# 4  5  6  7
# 8  9  10 11
# 12 13 14 15
# 16 17 18 19
# 20 21 22 23
# 24 25 26 27
# But want to go in order
# 0 6 12 18 24 30
# 3, 9, 15, 21, 27, 33...
    roi_order = np.array([0,4,8,12,16,20,24, 2,6,10,14,18,22,26, 1,5,9,13,17,21,25, 3,7,11,15,19,23,27])

    area=[]
    perimeter=[]
    estimated_object_count=[]
    #longest_path=[]
    #green_frequencies=[]
    
    for i in range(len(roi_order)):
        
        roi = rois1[roi_order[i]]
        hierarchy = roi_hierarchy1[roi_order[i]]
        # Find objects
        filtered_contours, filtered_hierarchy, filtered_mask, filtered_area = pcv.roi_objects(
            img=img1, roi_type="partial", roi_contour=roi, roi_hierarchy=hierarchy, object_contour=id_objects, 
            obj_hierarchy=obj_hierarchy)
    
        # Combine objects together in each plant  
        pcv.params.debug = None
        plant_contour, plant_mask = pcv.object_composition(img=img1, contours=filtered_contours, hierarchy=filtered_hierarchy)        
        pcv.params.debug = False
        # Analyze the shape of each plant 
        try:
            shape_image = pcv.analyze_object(img=img_copy, obj=plant_contour, mask=plant_mask)
            analysis_image = pcv.watershed_segmentation(rgb_img=img_copy, mask=plant_mask, distance=10)
            # Save the image with shape characteristics 
            img_copy = shape_image
            # Print out a text file with shape data for each plant in the image 
            area.append(pcv.outputs.observations['area']['value'])
            perimeter.append(pcv.outputs.observations['perimeter']['value'])
            estimated_object_count.append(pcv.outputs.observations['estimated_object_count']['value'])
            #longest_path.append(pcv.outputs.observations['longest_path']['value'])
            #green_frequencies.append(sum(pcv.outputs.observations['green_frequencies']['value']))
        except TypeError:
            print('Tiny plant skipped, position {:.0f}'.format(roi_order[i]))
            img_copy=img_copy
            # Print out a text file with shape data for each plant in the image 
            area.append(0)
            perimeter.append(0)
            estimated_object_count.append(0)
            #longest_path.append(pcv.outputs.observations['longest_path']['value'])
            #green_frequencies.append(sum(pcv.outputs.observations['green_frequencies']['value']))
            
                
        #hist_image = pcv.analyze_color(rgb_img=img_copy, mask=plant_mask)
        

    
        
       
    
    
    
    with open(save_path_area, 'a', newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    #        csvwriter.writerow(['Plant number','Area (pixels)','longest_path (pixels)'])
        area.insert(0,filename)
        area.insert(1,datetime.datetime.strftime(timestamp,'%Y-%m-%d %H:%M:%S'))
    #        area.insert(2,datetime.datetime.strftime(timestamp,'%H:%M:%S'))
        csvwriter.writerow(area)
        
    with open(save_path_perimeter, 'a', newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
#        csvwriter.writerow(['Plant number','Area (pixels)','longest_path (pixels)'])
        perimeter.insert(0,filename)
        perimeter.insert(1,datetime.datetime.strftime(timestamp,'%Y-%m-%d %H:%M:%S'))
#        area.insert(2,datetime.datetime.strftime(timestamp,'%H:%M:%S'))
        csvwriter.writerow(perimeter)
    
    with open(save_path_estimated_object_count, 'a', newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
        #csvwriter.writerow(['Plant number','Area (pixels)','longest_path (pixels)'])
        estimated_object_count.insert(0,filename)
        estimated_object_count.insert(1,datetime.datetime.strftime(timestamp,'%Y-%m-%d %H:%M:%S'))
        #area.insert(2,datetime.datetime.strftime(timestamp,'%H:%M:%S'))
        csvwriter.writerow(estimated_object_count)

#    with open(save_path_longest, 'a', newline='') as csvfile:
#        csvwriter = csv.writer(csvfile, delimiter=',',
#                           quotechar='|', quoting=csv.QUOTE_MINIMAL)
    #        csvwriter.writerow(['Plant number','Area (pixels)','longest_path (pixels)'])
#        longest_path.insert(0,filename)
#        longest_path.insert(1,datetime.datetime.strftime(timestamp,'%Y-%m-%d %H:%M:%S'))
#        csvwriter.writerow(longest_path)
        
#    with open(save_path_green, 'a', newline='') as csvfile:
#       csvwriter = csv.writer(csvfile, delimiter=',',
#                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
#    #        csvwriter.writerow(['Plant number','Area (pixels)','longest_path (pixels)'])
# #       green_frequencies.insert(0,filename)
# #       green_frequencies.insert(1,datetime.datetime.strftime(timestamp,'%Y-%m-%d %H:%M:%S'))
#        csvwriter.writerow(green_frequencies)
        # Clear the measurements stored globally into the Ouptuts class
    pcv.outputs.clear()
    
    # Plot out the image with shape analysis on each plant in the image 
    if pcv.params.debug == 'plot':
        pcv.plot_image(img_copy)
    pcv.print_image(img_copy,args.outdir+'/'+filename)

if __name__ == '__main__':
    main()
