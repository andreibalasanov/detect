import numpy as np
import cv2
from utils import ExecTimer,ExecOp

def infer (interpreter,image):
	op = ExecOp ("inference")
	resize_op = ExecOp ("resize")
	input_details = interpreter.get_input_details()
	output_details = interpreter.get_output_details()
	input_shape = input_details[0]['shape']
	
	height = input_details[0]['shape'][1]
	width = input_details[0]['shape'][2]
	
	src_height, src_width, _ = image.shape 

	image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
	image_resized = cv2.resize(image_rgb, (width, height))
	input_data = np.expand_dims(image_resized, axis=0)
	ExecTimer.instance().reportOp (resize_op)

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

class Engine:
	
	def __init__(self,model="model.tflite"):
		tfimport_time = ExecOp ("tfimport")
		import tensorflow as tf
		ExecTimer.instance().reportOp (tfimport_time)

		op = ExecOp ("modelload")
		self.interpreter = tf.lite.Interpreter(model_path="model.tflite")
		self.interpreter.allocate_tensors()
		ExecTimer.instance().reportOp (op)
	def process(self,image):
		res = infer (self.interpreter,image)
		return res
