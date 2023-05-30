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

6. Look at the available job files in /jobs. Open up z1c2.json.
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

7. We've put one image in the image/z1c2 folder for this demo, but you can download the entire z1c2 image set from https://drive.google.com/drive/folders/1Ft5fDFBSBnfpqewFgEpj1uWKWl_qsgkB?usp=drive_link if you wish. Just add the other images to the same image/z1c2 folder!

8. Run the job using the command:
```
python run_job_multithreadv2.py jobs/z1c2.json
```
Once the program has completed, you should see a new z1c2_out.csv file has been created in out/csv, and an output image has been created in out/image/z1c2. Our versions of these files are in the out/correct-output-for-demo directory if you want to verify for correctness. The output image should look like this ![correct output image](/PlantCV/out/correct-output-for-demo/z1c2--2021-09-02--11-30-07_processed.png "correct output image")



9. We've followed these steps for z2c2-z6c2 to show more example outputs. However, feel free to delete the output csv files and regenerate them using the entire image sets!
