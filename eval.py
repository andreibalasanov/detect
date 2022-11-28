#!/usr/bin/env python3

import os
#os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

from utils import ExecTimer,ExecOp

app_time = ExecOp ("app")
import os
#from engine.tf_lite_engine import Engine as TFEngine
from engine.tfengine import Engine as TFEngine
import cv2
from pathlib import Path
import glob
from utils import imgannotate
from logic import detector_filter

if os.path.exists("testdata"):
	engine = TFEngine()
	for filepath in glob.iglob('testdata/*'):
		image = cv2.imread(filepath)
		res,name = engine.process (image)
		res = detector_filter (res)
		resimage = imgannotate(res,image)
	
		ExecTimer.instance().summary ("inference")
		base = os.path.basename(filepath)
		resimage.save ("res-"+base)
else:
	print ("Test folder is not available")

ExecTimer.instance().reportOp (app_time)
ExecTimer.instance().allsummary ()
print ("Completed...")
