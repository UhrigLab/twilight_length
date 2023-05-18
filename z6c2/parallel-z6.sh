#!/bin/bash


# Here we are running a VIS top-view workflow

time \
/home/mdnafize/anaconda3/envs/envname/bin/plantcv-workflow.py \
-d . \
-p workflowzone6.py \
-t png \
-j test.json \
-i images_out/ \
-T 12 \
-f id \
-a filename \
-c \

# Translate the json database to csv. But our results are in /results/ anyway
/home/mdnafize/anaconda3/envs/envname/bin/plantcv-utils.py json2csv -j test.json -c result-table
python3 csv_datetime_sorter.py
