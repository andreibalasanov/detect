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

from flask_cors import CORS
from PIL import Image
from engine.tfengine import Engine as TFEngine
from utils import imgannotate
from logic import detector_filter
app = Flask(__name__)
CORS(app)


import logger
from logger import getLogger
logger = getLogger(__name__)

app.config["DEBUG"] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
start = time.time()

engine = TFEngine()


@app.route('/api/v1/detect', methods=['POST'])
def detect():
	try:
		if 'file' not in request.files:
			raise Exception ("No file")
		file = request.files['file']
		img = Image.open(request.files['file'].stream)
		cvimg = np.array(img) 
		locations,desc =  engine.process (cvimg)
		ret = {}
		faces = []
		locations = detector_filter (locations)
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

@app.route('/api/v1/annotate', methods=['POST'])
def annotate():
	try:
		if 'file' not in request.files:
			raise Exception ("No file")
		file = request.files['file']
		img = Image.open(request.files['file'].stream)
		cvimg = np.array(img)
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
	return flask.send_file("openapi.json")

SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI (without trailing '/')
API_URL = '/api/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(
	SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
	API_URL,
	config={
		'app_name': "Detect API"
	})
app.register_blueprint(swaggerui_blueprint)

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=8080, debug=False)