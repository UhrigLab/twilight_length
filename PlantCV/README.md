# Steps to recreate our results
1. Initialize a python virtual environment (tested using python version 3.8.16)

```python -m venv venv```

2. Activate the environment (note that the command and path may differ depending on your platform, below is for macos and linux)

```source venv/bin/activate```

3. Clone the repository

```git clone https://github.com/UhrigLab/twilight_length.git```

4. Navigate to the repository

```cd twilight_length```

5. Install the requirements

```pip install -r requirements.txt```

4. Look at the available job files in /jobs. Open up z1c2.json.
- Note that the paths in this file are configured for macos and linux systems, if on windows, adjust the following:
```    
"input_image_dir": "images/z1c2",
"output_image_dir": "out/image/z1c2",
"output_csv_file": "out/csv/z1c2_out.csv",
```
to
```    
"input_image_dir": "images\\z1c2",
"output_image_dir": "out\\image\\z1c2",
"output_csv_file": "out\\csv\\z1c2_out.csv",
```

5. We've put one image in the image/z1c2 folder for this demo, but you can download the entire z1c2 image set from https://drive.google.com/drive/folders/1Ft5fDFBSBnfpqewFgEpj1uWKWl_qsgkB?usp=drive_link if you wish. Just add the other images to the same image/z1c2 folder!

6. Run the job using the command:
```
python run_job_multithreadv2.py jobs/z1c2.json
```
Once the program has completed, you should see a new z1c2_out.csv file has been created in out/csv, and an output image has been created in out/image/z1c2. Our versions of these files are in the out/correct-output-for-demo directory if you want to verify for correctness. The output image should look like this ![correct output image](/PlantCV/out/correct-output-for-demo/z1c2--2021-09-02--11-30-07_processed.png "correct output image")



7. We've followed these steps for z2c2-z6c2 to show more example outputs. However, feel free to delete the output csv files and regenerate them using the entire image sets!

---
# Creating your own job files

We've provided the scripts and several utilities that we used to create our json job files. Our workflow is tailored to our camera configuration and so these scripts will not be 'plug-and-play' with your own image pipeline. These scripts may serve as inspiration for your own pipeline, and we describe how they are used below. Note that they have been tested and used on Windows only.

## Prerequisites

For this demo, we can re-create the z1c2.json job file. To begin, ensure you have downloaded the entire z1c2 image set from https://drive.google.com/drive/folders/1Ft5fDFBSBnfpqewFgEpj1uWKWl_qsgkB?usp=drive_link and placed them in images/z1c2. The images follow a specific naming scheme as follows:

z1c2--2021-09-02--11-30-07.png in plain english: Zone 1, Camera 2, taken on September 2nd, 2021 at 11:30:07 am.

In addition to the previous requirements.txt file, we will need to install 'ipykernel' to use the configure_job.ipynb file. Do so using ```pip install ipykernel```.

## Defining the job

Open up the configure_job.ipynb jupyter notebook and run the first two cells. This will import the necessary modules as well as create a job object 'j'.

The third cell contains important information related to the time frame for this job. First, we set the j.zonecamera setting to 'z1c2', and the j.description setting can be used to quickly look back at this job file and understand it's purpose. The start and end timestamps define the beginning and end of the experiment. Suppose an experiment went on for 3 days, but you only wanted to process images taken between 9am and 9pm. You can set the j.light_on_time and j.light_off_time to control this. Finally, we define important paths to our input images, and where we would like to save our outputs.

Running this third cell should output "Found 13 images in job". If not, check that you've downloaded all the z1c2 images and placed them in the images/z1c2 folder.

## Undistortion

The next cell (4) is used to correct for the fisheye effect caused by our camera system, run this cell to ensure that images are corrected using the parameters obtained by calibrating the camera.

## Camera angles

Sometimes, the camera or plants are bumped or shifted over the course of the experiment. This requires us to define separate plant regions of interest for each new camera angle. Since the plant locations are constant in this example, we can simply enter in the path to any of the z1c2 images, and run the cell (5).

## Genotype map

In this experiment, we have 28 plants with one of two genotypes. Run this cell (6) to define a mapping to record the genotype of each plant with each observation. We number plants from left to right, top to bottom. This order will be the same order we draw the plant regions of interest in.

## White spot ROI

Since the images in this example are all taken when the lights are brightest, there is no need to balance out the exposure. We will skip this cell, but it can be used to draw a small square over a white spot in the image that will be used to balance exposure. See the ROI drawing section below on how we use these scripts to draw ROI's.

## Creating undistorted images

Before we draw plant ROI's, we need to prepare the images. Running cell 11 will find all the images applicable to your job, undistort them, and correct their exposure (if applicable). It will then output a histogram from which you can check for outliers. Images that are too dark or too bright will be difficult to analyze. Run cell 12 to set a range from which images will be processed from. Judging by the histogram, all 13 images are good to go! ![histogram](/PlantCV/images/demo/histogram.png "histogram")

## Thresholding

In order to separate plants from the soil, we use an HSV thresholding technique to mask the plants. Run cell 13 to initialize a threshold that we will adjust next. Running cell 14 will open several windows that will be used to tweak the threshold. You can adjust the values using the slider, and see the output in the other windows. If you press 'q', the UI will close, and you will be prompted to quit, or to view another image using the same threshold. Once you've quit, you can run cell 16 to set the threshold. This process can be repeated to prepare a threshold for a size marker, should it be desired. ![thresholding](/PlantCV/images/demo/threshold.png "thresholding")

## Drawing plant ROI's

The last main step is to draw the plant ROI's. It's important that the ROI's are drawn in the same order that the genotype map was set. In this demo, we will set from from left to right, top to bottom. Run cell 22 to be shown the image. 

Controls for ROI drawing:
- Use the mouse wheel to zoom in and out
- When zoomed in, use the right mouse button to pan
- Use the left mouse button to place a point, placing subsequent points will join a line to the previous point
- After placing points around the first plant, complete the ROI by pressing the middle mouse button (click mouse wheel)

![roi-drawing](/PlantCV/images/demo/roi-drawing.png "roi-drawing")

Once all ROI's have been drawn, click the x button on the window to quit, if you had previously defined multiple camera angles, you will be prompted with the next camera angle. Set the plant ROI's using cells 23, 24, and 25. Finally use cell 26 to inspect the ROI's.

![roi-inspecting](/PlantCV/images/demo/roi-inspect-cell26.png "roi-inspecting")

## Wrapping up

Cell 28 can be used to check that everything has been set. If you've followed this demo, you should see:

```
z1c2
missing white_spot_roi
missing size_marker_rois
missing size_marker_upper_hsv
missing size_marker_lower_hsv
missing size_marker_fill_threshold
```

Last but not least, save the job file by running cell 29. You're now ready to run the job using the process described in the previous section. Feel free to use and adapt these scripts and utilities for your own imaging pipelines. As each pipeline is coupled to the camera configuration, we cannot provide any further technical support on the usage of these scripts. For more information on PlantCV, visit the documentation at https://plantcv.readthedocs.io/en/stable/.

