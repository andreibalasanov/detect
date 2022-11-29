import numpy as np
import cv2
from utils import ExecTimer,ExecOp
from PIL import Image

def infer (inferp,image,tf):
	src_height, src_width, _ = image.shape
	k = tf.expand_dims(tf.convert_to_tensor("test_key"), 0)
	image = np.asarray(image)
	input_tensor = tf.convert_to_tensor(image)
	encoded_image = tf.io.encode_jpeg(input_tensor)
	encoded_image = encoded_image[tf.newaxis,...]

	op = ExecOp ("inference")
	detections = inferp(image_bytes = encoded_image,key=k)
	
	num_detections = detections["num_detections"]
	ret = []
	boxes = detections["detection_boxes"][0]
	scores = detections["detection_scores"][0]
	classes = detections["detection_classes_as_text"][0]
	
	for i in range (int (num_detections)):
		ymin = int(max(1,(boxes[i][0] * src_height)))
		xmin = int(max(1,(boxes[i][1] * src_width)))
		ymax = int(min(src_height,(boxes[i][2] * src_height)))
		xmax = int(min(src_width,(boxes[i][3] * src_width)))
		score = float(scores [i])
		cl = classes[i]
		ret.append (([xmin,ymin,xmax,ymax],score,cl))
	ExecTimer.instance().reportOp (op)
	return ret

class Engine:
	def __init__(self,model="model.tflite"):
		tfimport_time = ExecOp ("tfimport")
		import tensorflow as tf
		self.tf = tf
		ExecTimer.instance().reportOp (tfimport_time)
		op = ExecOp ("modelload")
		loaded = tf.saved_model.load(model)
		self.inferp = loaded.signatures["serving_default"]
		ExecTimer.instance().reportOp (op)
	
	def process(self,image):
		res = infer (self.inferp,image,self.tf),"TF Raw"
		return res
