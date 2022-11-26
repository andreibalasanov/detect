#!/usr/bin/env python3

from utils import ExecTimer,ExecOp
app_time = ExecOp ("app")
import os
from tfengine import Engine
import cv2
from pathlib import Path
import glob
from utils import annotate

engine = Engine()
for filepath in glob.iglob('testdata/*'):
	image = cv2.imread(filepath)
	res = engine.process (image)
	resimage = annotate (res,image)
	
	ExecTimer.instance().summary ("inference")
	base = os.path.basename(filepath)
	resimage.save ("res-"+base)

ExecTimer.instance().reportOp (app_time)
ExecTimer.instance().allsummary ()
print ("Completed...")


