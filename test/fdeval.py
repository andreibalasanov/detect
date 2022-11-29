#!/usr/bin/env python3

import os

import cv2
from pathlib import Path
import glob
import argparse
import requests

def list_files (src):
	res = []
	for filepath in glob.iglob(src+'/*'):
		res.append (filepath)
	return res

def annotate(src,process):
	files = list_files (src)
	print (files,src)
	for file in files:
		multipart_form_data = {
			'file': (file, open(file, 'rb')),
		}
		response = requests.post('http://localhost:8080/api/v1/annotate', files=multipart_form_data)
		if response.status_code==200:
			base = os.path.basename(file)
			with open(base, 'wb') as f:
				for chunk in response:
					f.write(chunk)
def run_test (src,command,process):
	files = list_files (src)
	passed = 0
	for file in files:
		multipart_form_data = {
    			'file': (file, open(file, 'rb')),
		}
		response = requests.post('http://localhost:8080/api/v1/detect', files=multipart_form_data)
		err = True
		if response.status_code==200:
			data = response.json()
			if command == "test-single":
				if data["persons"]==1:
					err = False
			if command == "test-none":
				if data["persons"]==0:
					err = False
			if command == "test-many":
				if data["persons"]>1:
					err = False
                        
			if command == "test-mask":
				if data["persons"]==1 and data["personStatus"]=="ePersonStatusHasFaceMaks":
					err = False
		if err==False:
			passed = passed+1
		else:
			print ("Error:",file)
			image = cv2.imread(file)
			base = os.path.basename(file)
			cv2.imwrite (base,image)
	print ("Total:",len(files),"Passed:",passed,"("+str(100*passed/len(files))+"%)")


parser = argparse.ArgumentParser(description='Face detection test tool.')
parser.add_argument('path',
			metavar='path',
			type=str,
			help='Test file locations')

parser.add_argument('--m',
			action='store',
			default='test-many',
			choices=['annotate', 'test-single','test-many','test-mask'],
			)

parser.add_argument('--process',
                        action='store',
                        default='save',
                        choices=['save', 'ignore'],
                        )


args = parser.parse_args()
command  = vars(args)["m"]
filepath  = vars(args)["path"]
process = vars(args)["process"]
print (command)
if command=="annotate":
	annotate (filepath,process)
else:
	run_test(filepath,command,process)
