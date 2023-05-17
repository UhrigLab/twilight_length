#!//home/anaconda3/envs/plantcv/bin/python
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 10 09:18:40 2019
This is to take all csv files in a directory and sort the rows by date_time
@author: evan
"""
import csv
import os
import datetime

for filename in os.listdir('./results'):
    if filename[-3:]=='csv':
        with open('./results/'+filename) as file:
            data = csv.reader(file)
            data = sorted(data, key = lambda row: datetime.datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S'))
        with open('./results/'+filename,'w') as file:
            writer = csv.writer(file, delimiter=',')
            writer.writerows(data)
