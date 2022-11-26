#!/usr/bin/env python3

import os
import tensorflow as tf
import numpy as np
from PIL import Image, ImageDraw
import cv2
from pathlib import Path
import glob
from utils import ExecTimer,ExecOp

def infer (interpreter,image_path):
	op = ExecOp ("inference")
	input_details = interpreter.get_input_details()
	output_details = interpreter.get_output_details()
	input_shape = input_details[0]['shape']
	
	height = input_details[0]['shape'][1]
	width = input_details[0]['shape'][2]
	
	image = cv2.imread(image_path)
	src_height, src_width, _ = image.shape 

	image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
	image_resized = cv2.resize(image_rgb, (width, height))
	input_data = np.expand_dims(image_resized, axis=0)
	
	floating_model = (input_details[0]['dtype'] == np.float32)
	if floating_model:
		exit()
    
	interpreter.set_tensor(input_details[0]['index'], input_data)
	
	interpreter.invoke()

	output_data = interpreter.get_tensor(output_details[0]['index'])
 
	input_details = interpreter.get_input_details()
	boxes_idx, classes_idx, num_detections_idx,score_idx = 0, 1, 3,2

	boxes = interpreter.get_tensor(output_details[boxes_idx]['index'])[0] # Bounding box coordinates of detected objects
	classes = interpreter.get_tensor(output_details[classes_idx]['index'])[0] # Class index of detected objects
	scores = interpreter.get_tensor(output_details[score_idx]['index'])[0] # Class index of detected objects
	num_detections = interpreter.get_tensor(output_details[num_detections_idx]['index'])[0] # Confidence of detected objects

	ret = []
	for i in range (int (num_detections)):
		ymin = int(max(1,(boxes[i][0] * src_height)))
		xmin = int(max(1,(boxes[i][1] * src_width)))
		ymax = int(min(src_height,(boxes[i][2] * src_height)))
		xmax = int(min(src_width,(boxes[i][3] * src_width)))
		score = scores [i]
		cl = classes[i]
		ret.append (([xmin,ymin,xmax,ymax],score,cl))
	ExecTimer.instance().reportOp (op)
	return ret

def annotate(res,image_path):
	src = Image.open(image_path)
	draw = ImageDraw.Draw(src)
	for entry in res:
		i,score,cl = entry
		#print (i,score,cl)
		if score > .7:
			draw.rectangle( (i[0], i[1], i[2], i[3]),outline=(255, 0, 0))
	base = os.path.basename(image_path)
	src.save ("res-"+base)

interpreter = tf.lite.Interpreter(model_path="model.tflite")
interpreter.allocate_tensors()





for filepath in glob.iglob('testdata/*'):
	src_img_path = filepath
	res = infer (interpreter,src_img_path)
	annotate (res,src_img_path)
	ExecTimer.instance().summary ("inference")
ExecTimer.instance().allsummary ()
print ("Completed...")


