from flask import render_template, request
import logging
import json

from app import app
from loggers import request_file_hendler

@app.route('/')
def index():
	#i = 1 / 0
	return render_template('index.html')


@app.route('/datareceiver', methods=['GET','POST'])
def equipments():

	logger = logging.getLogger('app.views')
	logger.setLevel(logging.INFO)

	logger.addHandler(request_file_hendler)

	data = request.get_json()
	logger.info('{}\n{}'.format(request.remote_addr, json.dumps(data, sort_keys=False, indent=4)))
	return render_template('index.html')