from flask import render_template, request, jsonify, abort
import logging
import json
import os

from app import app
from loggers import request_file_hendler
from config import base_dir

def parse_data(data):
	pass #for key in sorted(data.keys(), revers=True):

	


@app.route('/')
def index():
	#i = 1 / 0
	return render_template('index.html')


@app.route('/datareceiver', methods=['GET','POST'])
def equipments():
	if request.method == 'GET':
		return abort(404)
	else:
		i = 1 / 0
		logger = logging.getLogger('app.views')
		logger.setLevel(logging.INFO)

		logger.addHandler(request_file_hendler)

		data = request.get_json()
		parse_data(data)
		logger.info('{}\n{}'.format(request.remote_addr, 
									json.dumps(data, sort_keys=False, indent=4)))
		return jsonify({'status' : 'OK'}), 200

@app.route('/getlog', methods=['GET','POST'])
def getlog():
	if request.method == 'GET':
		return abort(404)
	else:
		filename =  request.get_json()
		with open(os.path.join(base_dir, filename)) as fd:
			full_log = fd.read()

		return render_template('log.html', text=full_log)