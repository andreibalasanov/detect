#!/usr/bin/env python3
from io import BytesIO

from flask import send_file,Flask, request, jsonify
import json
from flask_swagger_ui import get_swaggerui_blueprint
import time
import flask
import os
from datetime import datetime
import threading
import numpy as np
import sys
import io 
from flask_cors import CORS
from PIL import Image
from engine.tfengine import Engine as TFEngine
from utils import imgannotate
from logic import detector_filter
import argparse

import logger
from logger import getLogger
logger = getLogger(__name__)


from io import StringIO
import cv2

from pathlib import Path
import sys
import requests

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    bundle_dir = Path(sys._MEIPASS)
else:
    bundle_dir = Path(__file__).parent

path_to_dat = Path.cwd() / bundle_dir 
print ("Path to dat is:",path_to_dat)

streaming_url = ""
app = Flask(__name__)
CORS(app)
app.config["DEBUG"] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
start = time.time()


def get_image(url):
	response = requests.get(url)
	if response.status_code == 200:
		with io.BytesIO(response.content) as f:
			with Image.open(f) as img:
				res = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
				return res
	return None

engine = TFEngine(path_to_dat)

def locationsToJson (locations):
	faces = []
	for loc in locations:
		face = {}
		pos,score,dclass = loc
		top, right, bottom, left = pos
		face["top"] = top
		face["right"] = right
		face["bottom"] = bottom
		face["left"] = left
		face["score"] = score
		faces.append (face)
	return faces

@app.route('/api/v1/detect', methods=['POST'])
def detect():
	try:    
		cvimg = get_image_from_request (request)
		locations,desc =  engine.process (cvimg)
		info = {}
		locations = detector_filter (locations)
		faces = locationsToJson (locations)
                
		info['faces']=faces
		ret = {}
		ret ["info"] = info
		ret ["persons"] = len (faces)
		if len(faces)==1:
			ret ["personStatus"] = "ePersonStatusNoArtifacts"
		else:
			ret ["personStatus"] = "ePersonStatusUknown"
		return json.dumps(ret), 200
        
	except Exception as e:
		raise e;
		return "Error", 500


@app.route('/api/v1/detect_faces', methods=['POST'])
def detect_faces():
	try:
		cvimg = get_image_from_request (request)
		locations,desc =  engine.process (cvimg)
		ret = {}
		locations = detector_filter (locations)
		faces = locationsToJson (locations)
		ret['faces']=faces
		return json.dumps(ret), 200
	except Exception as e:
		raise e;
		return "Error", 500

def serve_pil_image(pil_img):
	img_io = BytesIO()
	pil_img.save(img_io, 'JPEG', quality=70)
	img_io.seek(0)
	return send_file(img_io, mimetype='image/jpeg')

def get_image_from_request (req):
	cvimg = None
	if 'file' not in req.files:
		cvimg = get_image (streaming_url)
	else:
		file = req.files['file']
		img = Image.open(request.files['file'].stream)
		cvimg = np.array(img)
	return cvimg

@app.route('/api/v1/annotate', methods=['POST'])
def annotate():
	try:
		cvimg = get_image_from_request (request)
		locations,desc =  engine.process (cvimg)
		ret = imgannotate (detector_filter(locations),cvimg)
		return serve_pil_image (ret)
        
	except Exception as e:
		raise e
		return "Error", 500

@app.route('/ready', methods=['GET'])
def ready():
	return "",200
        
@app.route('/api/swagger.json', methods=['GET'])
def swagger():
	return flask.send_file(path_to_dat / "openapi.json")

SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI (without trailing '/')
API_URL = '/api/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(
	SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
	API_URL,
	config={
		'app_name': "Detect API"
	})
app.register_blueprint(swaggerui_blueprint)

def my_url(arg):
	from urllib.parse import urlparse
	url = urlparse(arg)
	if all((url.scheme, url.netloc)):  # possibly other sections?
		return arg  # return url in case you need the parsed object
	raise ArgumentTypeError('Invalid URL')

if __name__ == "__main__":


	parser = argparse.ArgumentParser(description='Face detection server.')

        
	parser.add_argument(
		"-p",   
		"--port",
		type=int,
		default=8080,
		help="Server port",
	)


	parser.add_argument(
		"-u",
    		"--url",
    		type=my_url,
		default="http://192.168.38.11:1000/image",
		help="Image streaming server",
	)

	
	args = parser.parse_args()
	port  = vars(args)["port"]
	streaming_url = vars(args)["url"]

	app.run(host="0.0.0.0",port=port, debug=False)
