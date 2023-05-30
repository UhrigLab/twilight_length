import cv2
import os
import csv
import time
import numpy as np
from plantcv import plantcv as pcv
from utils.nogui.undistort import undistort
from utils.nogui.correct_exposure import correct_exposure
from utils.nogui.mask_green import mask_green
from classes.Job import Job
from classes.ImageNameParser import ImageNameParser
from pathlib import Path


def listener(job: Job, queue):
    with open(job.output_csv_file, 'a', newline='') as f:
        fieldnames = ['sample', 'image_name', 'zone', 'camera', 'timestamp', 
        'date', 'time', 'plant_id', 'genotype', 'area', 'marker_area', 
        'marker_ellipse_major_axis', 'marker_ellipse_minor_axis', 'marker_ellipse_eccentricity', 
        'in_bounds', 'object_in_frame', 'estimated_object_count', 
        'perimeter', 'height', 'width', 'solidity', 
        'center_of_mass_x', 'center_of_mass_y', 'ellipse_center_x', 'ellipse_center_y', 
        'ellipse_major_axis', 'ellipse_minor_axis', 'ellipse_angle', 'ellipse_eccentricity', 
        'convex_hull_vertices', 'convex_hull_area', 'longest_path']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if os.path.getsize(job.output_csv_file) == 0:
            # write header
            writer.writeheader()

        while True:
            m = queue.get()
            if m == 'kill':
                break
            writer.writerow(m)
            f.flush()




def main(job: Job, path: Path, queue):
    pcv.params.debug = None # disable PlantCV auto plotting or auto saving intermediate results

    image_path = str(path.absolute())
    image_name : str = path.name
    image_name_no_extension = image_name.replace(".png", '')
    inp = ImageNameParser(image_name)
    timestamp = inp.get_timestamp()

    # So far, image is valid, so we will read it
    img = cv2.imread(image_path)

    print("Processing {}".format(image_path), flush=True)

    pcv.outputs.clear() # clear all outputs from previous image

    if img is None:
        return

    # Correct fisheye distortion
    if job.undistort:
        K = np.array([[job.fx, 0.0, job.cx],
                    [0.0, job.fy, job.cy],
                    [0.0, 0.0, 1.0]]) # camera intrinsic matrix

        D = np.array([job.k1, job.k2, job.k3, job.k4], dtype=np.float64) # camera distortion matrix
        img = undistort(img, K, D)

    undistorted_img = img

    # White balance
    white_spot_roi = job.white_spot_roi.get_setting(timestamp)
    if white_spot_roi is not None:
        exp_corrected_img = correct_exposure(undistorted_img, white_spot_roi)
    else:
        exp_corrected_img = undistorted_img

    # Check if too dark or too bright
    average = np.average(exp_corrected_img)
    # print("np average: {}".format(average))
    if (average < job.np_average_min):
        return

    if (average > job.np_average_max):
        return

    # Mask green
    plant_mask = mask_green(exp_corrected_img, job.upper_hsv, job.lower_hsv)

    if plant_mask is None:
        return
    
    # Fill in small noise
    filled = pcv.fill(plant_mask, job.mask_fill_threshold)


    # Size marker
    try:
        # obtain mask of size marker
        size_marker_mask = mask_green(exp_corrected_img, upper_HSV=job.size_marker_upper_hsv, lower_HSV=job.size_marker_lower_hsv)
        # Fill in small noise
        size_marker_filled_mask = pcv.fill(size_marker_mask, size=job.size_marker_fill_threshold)
        # Create roi
        roi_contour, roi_hierarchy, size_marker_roi_img = pcv.roi.custom(img=exp_corrected_img, 
        vertices=job.size_marker_rois.get_setting(timestamp)[0])
        # Report size marker area
        size_marker_img = pcv.report_size_marker_area(exp_corrected_img, roi_contour, roi_hierarchy, "detect", masked_img=size_marker_filled_mask, label="image")
    except:
        size_marker_img = exp_corrected_img


    # Define ROI's
    roi_list = []
    hierarchy_list = []
    plant_rois = job.plant_rois.get_setting(timestamp)
    for roi in plant_rois:
        roi_contour, roi_hierarchy, roi_image = pcv.roi.custom(img=exp_corrected_img, 
                                                    vertices=roi)
        roi_list.append(roi_contour)
        hierarchy_list.append(roi_hierarchy)

    # Process Objects
    rgb_image = size_marker_img # make size marker appear in the output image,
    mask = filled

    obj, obj_hierarchy = pcv.find_objects(rgb_image, mask)

    img_copy = np.copy(rgb_image)

    for i in range(0, len(roi_list)):
        roi = roi_list[i]
        hierarchy = hierarchy_list[i]
        plant_id = i
        label = f"{image_name_no_extension}_plant_{plant_id:02}"

        # get genotype
        genotype = job.get_genotype(timestamp, str(plant_id))

        # add manual observations
        pcv.outputs.add_observation(label, "genotype", "trait", "method", "scale", str, genotype, "genotype")
        pcv.outputs.add_observation(sample=label, variable="plant_id", trait="trait", method="method", scale="scale", datatype=int, value=plant_id, label="plant_id")
        pcv.outputs.add_observation(sample=label, variable="image_name", trait="trait", method="method", scale="scale", datatype=str, value=image_name, label="image_name")
        pcv.outputs.add_observation(sample=label, variable="zone", trait="trait", method="method", scale="scale", datatype=int, value=job.get_zone(), label="zone")
        pcv.outputs.add_observation(sample=label, variable="camera", trait="trait", method="method", scale="scale", datatype=int, value=job.get_camera(), label="camera")
        pcv.outputs.add_observation(sample=label, variable="date", trait="trait", method="method", scale="scale", datatype=str, value=str(timestamp.date()), label="date")
        pcv.outputs.add_observation(sample=label, variable="time", trait="trait", method="method", scale="scale", datatype=str, value=str(timestamp.time()), label="time")
        pcv.outputs.add_observation(sample=label, variable="timestamp", trait="trait", method="method", scale="scale", datatype=str, value=timestamp.strftime("%Y-%m-%d %H:%M"), label="timestamp")
        
        # Subset objects that overlap the ROI
        #   roi_type       = "partial" (default) keeps contours that overlap
        #                    or are contained in the ROI. "cutto" cuts off
        #                    contours that fall outside the ROI. "largest"
        #                    only keeps the largest object within the ROI
        plant_contours, plant_hierarchy, mask, area = pcv.roi_objects(img=rgb_image, 
                                                                    roi_contour=roi, 
                                                                    roi_hierarchy=hierarchy, 
                                                                    object_contour=obj, 
                                                                    obj_hierarchy=obj_hierarchy, 
                                                                    roi_type="partial")

        # If the plant area is zero then no plant was detected for the ROI
        # and no measurements can be done
        if area > 0:
            # Combine contours together for each plant
            plant_obj, plant_mask = pcv.object_composition(img=rgb_image, 
                                                        contours=plant_contours, 
                                                        hierarchy=plant_hierarchy)

            # leaf counting

            # auto crop
            crop_img = pcv.auto_crop(img=rgb_image, obj=plant_obj, padding_x=20, padding_y=20, color='image')
            crop_mask = pcv.auto_crop(img=plant_mask, obj=plant_obj, padding_x=20, padding_y=20, color='image')
            # pcv.plot_image(crop_img)
            # pcv.plot_image(crop_mask)


            # Use watershed segmentation 

            # Inputs:
            #   rgb_img  = RGB image data 
            #   mask     = Binary image, single channel, object in white and background black
            #   distance = Minimum distance of local maximum, lower values are more sensitive, 
            #              and segments more objects (default: 10)
            #   label    = Optional label parameter, modifies the variable name of observations recorded. (default `label="default"`)filled_img = pcv.morphology.fill_segments(mask=cropped_mask, objects=edge_objects)

            analysis_image = pcv.watershed_segmentation(rgb_img=crop_img, mask=crop_mask, distance=10, label=label)


            # Analyze the shape of each plant
            img_copy = pcv.analyze_object(img=img_copy, obj=plant_obj, 
                                        mask=plant_mask, label=label)
        

    output_image = os.path.join(job.output_image_dir, image_name_no_extension+"_processed.png")
    pcv.print_image(img_copy, output_image)

    observations = pcv.outputs.observations

    for sample in observations:
        if sample == "image":
            continue
        else:
            # sample is a label ie. z1c1--2022-06-01--12-00-01_plant_00
            row = {}
            row["sample"] = sample

            for variable in observations[sample]:
                # special cases for tuples
                if variable == "center_of_mass":
                    row["center_of_mass_x"] = observations[sample][variable]["value"][0]
                    row["center_of_mass_y"] = observations[sample][variable]["value"][1]
                elif variable == "ellipse_center":
                    row["ellipse_center_x"] = observations[sample][variable]["value"][0]
                    row["ellipse_center_y"] = observations[sample][variable]["value"][1]
                # general case
                else:
                    row[variable] = observations[sample][variable]["value"]
            try:
                row["marker_area"] = observations["image"]["marker_area"]["value"]
                row["marker_ellipse_major_axis"] = observations["image"]["marker_ellipse_major_axis"]["value"]
                row["marker_ellipse_minor_axis"] = observations["image"]["marker_ellipse_minor_axis"]["value"]
                row["marker_ellipse_eccentricity"] = observations["image"]["marker_ellipse_eccentricity"]["value"]

            except:
                row["marker_area"] = "N/A"
                row["marker_ellipse_major_axis"] = "N/A"
                row["marker_ellipse_minor_axis"] = "N/A"
                row["marker_ellipse_eccentricity"] = "N/A"

            queue.put(row)


if __name__ == "__main__":
    import multiprocessing as mp
    import sys
    from classes.Job import file_to_job
    j = file_to_job(Path(sys.argv[1]))
    job_image_paths = j.get_job_images(verbose=False, testing_mode=False)

    print(f"Processing {len(job_image_paths)} images", flush=True)

    manager = mp.Manager()

    q = manager.Queue()

    file_pool = mp.Pool(1)
    file_pool.apply_async(listener, (j, q))


    items = []
    for image_path in job_image_paths:
        items.append((j, image_path, q))
    time_start = time.time()

    with mp.Pool() as pool:
        pool.starmap(main, items)
    q.put('kill')
    file_pool.close()
    file_pool.join()

    print("Program finished!", flush=True)
    time_end = time.time()
    print("Time elapsed: ", time_end - time_start, flush=True)
