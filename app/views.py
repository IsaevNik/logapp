from flask import render_template, request, jsonify, abort
import logging
import json
import os
import re
from datetime import datetime


from app import app
from loggers import request_file_hendler
from config import base_dir

def parse_data(data):
	pass #for key in sorted(data.keys(), revers=True):

def get_error_name(stacktrace):
	result = re.findall(r'\n(.+)Error:', stacktrace);
	return result[0] + 'Error'

def get_list_of_errors(full_log, **kvargs):
	full_log += "##"
	search_result = re.findall(r'(\d{2}\:\d{2}\:\d{2} \d{2}\/\d{2}\/\d{4}) \- (.*?)(Traceback .*?)##',full_log, re.S)

	if kvargs['errors_type'] == 'all':
		errors = [{"datetime": datetime.strptime(line[0], '%H:%M:%S %d/%m/%Y'), 
					"msg": line[1], 
					"stacktrace": line[2],
					"error_name": get_error_name(line[2])} for line in search_result] 
	else:
		errors = filter(lambda error: error["error_name"] in kvargs['errors_type'],
					[{"datetime": datetime.strptime(line[0], '%H:%M:%S %d/%m/%Y'), 
					  "msg": line[1], 
					  "stacktrace": line[2],
					  "error_name": get_error_name(line[2])} for line in search_result])

	if kvargs['date'] != "now":
		errors = filter(lambda error: error["datetime"].strftime('%d %m %Y') == kvargs['date'].strftime('%d %m %Y'), errors)

	errors.sort(key = lambda i: i["datetime"], reverse=True)
	return errors

@app.route('/')
def index():
	#i = 1 / 0
	return render_template('index.html')


@app.route('/datareceiver', methods=['GET','POST'])
def equipments():
	if request.method == 'GET':
		return abort(404)
	else:
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

		if not full_log:
			return jsonify({'log':'<pre> </pre>'}), 200

		if filename.startswith('error'):
			errors_list = get_list_of_errors(full_log, errors_type = 'all', date = 'now')
			error_name_list = list(set([error['error_name'] for error in errors_list]))

			return jsonify({'log':render_template('errorlog.html', errors=errors_list), 
							'control': render_template('error_log_controle.html', error_name_list=error_name_list)})
			
		return render_template('log.html', text=full_log)

@app.route('/errorlogfilter', methods=['GET','POST'])
def errorlogfilter():
	if request.method == 'GET':
		return abort(404)
	else:
		data = request.get_json()
		errors = data["errors"]
		date = datetime.strptime(data["date"], '%Y-%m-%d')

		with open(os.path.join(base_dir, app.config['ERROR_LOG_FILE'])) as fd:
			full_log = fd.read()
		if not full_log:
			return jsonify({'log':'<pre> </pre>'}), 200

		errors_list = get_list_of_errors(full_log, errors_type = errors, date = date)	

	return jsonify({'log':render_template('errorlog.html', errors=errors_list)})