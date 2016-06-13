from flask import render_template, request, jsonify, abort
import logging
import json
import os
import re
from datetime import datetime, date


from app import app
from loggers import request_file_hendler
from config import base_dir

def parse_data(data):
	pass #for key in sorted(data.keys(), revers=True):

def get_file_name(log_name):
	if log_name == 'errors':
		return app.config['ERROR_LOG_FILE']
	else:
		return app.config['REQUEST_LOG_FILE']

def get_error_name(stacktrace):
	lines = stacktrace.split('\n')
	last_line = lines[len(lines) - 2]
	result = re.search(r'^(\w+Error)', last_line);
	return result.group(0)

def get_list_of_errors(full_log, **kvargs):
	full_log += "##"
	search_result = re.findall(r'(\d{2}\:\d{2}\:\d{2} \d{2}\/\d{2}\/\d{4}) \- (.*?)(Traceback .*?)##',full_log, re.S)

	if not kvargs['errors_type']:
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

	if kvargs['date']:
		errors = filter(lambda error: error["datetime"].strftime('%d %m %Y') == kvargs['date'].strftime('%d %m %Y'), errors)

	errors.sort(key = lambda i: i["datetime"], reverse=True)
	return errors

def get_list_of_request(full_log, **kvargs):
	full_log += "##"
	search_result = re.findall(r'(\d{2}\:\d{2}\:\d{2} \d{2}\/\d{2}\/\d{4}) \- (\d+\.\d+\.\d+\.\d+)\n(.*?)\n##', full_log, re.S)
	requests = [{"datetime": datetime.strptime(line[0], '%H:%M:%S %d/%m/%Y'), 
					"ip": line[1],
					"request body": json.loads(line[2])} for line in search_result] 
	# translate readout_dt "1465193586" --> "2016-06-06"					
	for request in requests:
		for counter in request.get("request body").get("data"):
			counter["readout_dt"] = (date.fromtimestamp(int(counter["readout_dt"])))
	# ip filter
	if kvargs["ip"]:
		requests = filter(lambda request: request["ip"] == kvargs["ip"], requests)
	# request filter	
	if kvargs['request_date']:
		requests = filter(lambda request: request["datetime"].strftime('%d %m %Y') == kvargs['request_date'].strftime('%d %m %Y'), 
						  requests)
	# number of count(sn) filter
	if kvargs['sn']:
		requests = filter(lambda request: request.get("request body").get("sn") == kvargs['sn'], requests)
	# readout_dt filter
	if kvargs['start_date']:
		for request in requests:
			request.get("request body")["data"] = filter(lambda item: item["readout_dt"] >= datetime.date(kvargs['start_date']), 
														 request.get("request body")["data"])
		requests = filter(lambda request: len(request.get("request body").get("data")) >= 1, requests)

	requests.sort(key = lambda i: i["datetime"], reverse = True)	
	return requests

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/datareceiver', methods=['GET','POST'])
def equipments():
	if request.method == 'GET':
		return abort(404)
	else:
		logger = logging.getLogger('app.views')
		logger.setLevel(logging.INFO)

		logger.addHandler(request_file_hendler)
		raise FileExistsError
		data = request.get_json()
		logger.info('{}\n{}'.format(request.remote_addr, json.dumps(data, encoding = "ascii"))) 
		return jsonify({'status' : 'OK'}), 200

@app.route('/getlog', methods=['GET','POST'])
def getlog():
	if request.method == 'GET':
		return abort(404)
	else:
		filename =  get_file_name(request.get_json())
		with open(os.path.join(base_dir, filename)) as fd:
			full_log = fd.read()

		if not full_log:
			return jsonify({'log':'<pre></pre>'}), 200

		if filename == app.config['ERROR_LOG_FILE']:
			errors_list = get_list_of_errors(full_log, errors_type = '', date = '')

			error_name_list = list(set([error['error_name'] for error in errors_list]))

			return jsonify({'log':render_template('errorlog.html', errors = errors_list), 
							'control': render_template('error_log_controle.html', error_name_list = error_name_list)})
		else:
			request_list = get_list_of_request(full_log, 
				                               ip = "", 
				                               request_date = "", 
				                               sn = "", 
				                               start_date = "")
			return jsonify({'log':render_template('requestlog.html', requests = request_list), 
							'control': '<span></span>'})

@app.route('/errorlogfilter', methods=['GET','POST'])
def errorlogfilter():
	if request.method == 'GET':
		return abort(404)
	else:
		data = request.get_json()
		if data["errors"]:
			errors = data["errors"].split()
		else:
			errors = data["errors"]
		date = datetime.strptime(data["date"], '%Y-%m-%d')

		with open(os.path.join(base_dir, app.config['ERROR_LOG_FILE'])) as fd:
			full_log = fd.read()
		if not full_log:
			return jsonify({'log':'<pre></pre>'}), 200

		errors_list = get_list_of_errors(full_log, errors_type = errors, date = date)	

	return jsonify({'log':render_template('errorlog.html', errors=errors_list)})

def get_date(date):
	if date:
		return datetime.strptime(date, '%Y-%m-%d')
	return date

@app.route('/requestlogfilter', methods=['GET','POST'])
def requestlogfilter():
	if request.method == 'GET':
		return abort(404)
	else:
		data = request.get_json()
		request_date = get_date(data["request_date"])
		start_date = get_date(data["start_date"])

		with open(os.path.join(base_dir, app.config['REQUEST_LOG_FILE'])) as fd:
			full_log = fd.read()

		if not full_log:
			return jsonify({'log':'<pre></pre>'}), 200

		request_list = get_list_of_request(full_log, 
										   ip = data["ip"], 
										   request_date = request_date, 
										   sn = data["sn"], 
										   start_date = start_date) 

	return jsonify({'log':render_template('requestlog.html', requests = request_list)})