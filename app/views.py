from flask import render_template, request, jsonify, abort
import logging
import json
import os
import re
from datetime import datetime, date

from app import app
from loggers import request_file_hendler
from config import base_dir


def get_file_name(log_name):
	"""Return name of the file from app config error.log/request.log"""
	if log_name == 'errors':
		return app.config['ERROR_LOG_FILE']
	else:
		return app.config['REQUEST_LOG_FILE']

def get_error_name(stacktrace):
	"""Parse the stacktrace of error and return name of Error"""
	lines = stacktrace.split('\n')
	last_line = lines[len(lines) - 2]
	result = re.search(r'^(\w+Error)', last_line);
	return result.group(0)

def get_list_of_errors(full_log, **kvargs):
	"""Return list of errors from error.log.

	Keyword arguments:
	full_log -- string line containing full error.log
	**kvargs {
		errors_type -- list of errors which user enter in front (default "" i.e. All)
		date -- datetime(%Y-%m-%d) date which user enter in front 
				(in start date="" i.e. All date, if user didn't enter date,
				 date=today datetime(%Y-%m-%d))
	}

	"""
	full_log += "##"
	search_result = re.findall(
		r'(\d{2}\:\d{2}\:\d{2} \d{2}\/\d{2}\/\d{4}) \- (.*?)(Traceback .*?)##',
		full_log, re.S)
	# For all type of errors create a list of dictionaries 
	# with information about error.
	if not kvargs['errors_type']:
		errors = [{"datetime": datetime.strptime(line[0], '%H:%M:%S %d/%m/%Y'), 
					"msg": line[1], 
					"stacktrace": line[2],
					"error_name": get_error_name(line[2])} for line in search_result] 
	# Add a filter if error_name  != errors_type, this error not add to result.
	else:
		errors = filter(lambda error: error["error_name"] in kvargs['errors_type'],
					    [{"datetime": datetime.strptime(line[0], '%H:%M:%S %d/%m/%Y'), 
					      "msg": line[1], 
					      "stacktrace": line[2],
					      "error_name": get_error_name(line[2])} for line in search_result])
	# Add a filter if error datetime != kvargs['date'], this error not add to result.
	if kvargs['date']:
		errors = filter(lambda error: 
			error["datetime"].strftime('%d %m %Y') == kvargs['date'].strftime('%d %m %Y'),
			errors)

	# Sorting result list by date (early -> late).
	errors.sort(key = lambda i: i["datetime"], reverse=True)
	return errors

def get_list_of_request(full_log, **kvargs):
	"""Return list of request from request.log.

	Keyword arguments:
	full_log -- string line containing full error.log
	**kvargs {
		ip -- string ip adress which interested by user (default "" i.e. All)
		request_date -- datetime(%Y-%m-%d) date which user enter 
						in front (default "" i.e. All)
		sn -- string number of counter which interested 
			  by user (default "" i.e. All)
		start_date -- datetime(%Y-%m-%d) date which user 
					  enter in front (default "" i.e. All)
	}
	If any of kvargs == "" filter of this mark will not work.

	"""
	full_log += "##"
	search_result = re.findall(
		r'(\d{2}\:\d{2}\:\d{2} \d{2}\/\d{2}\/\d{4}) \- (\d+\.\d+\.\d+\.\d+)\n(.*?)\n##', 
		full_log, re.S)
	# Create a list of dictionaries with information 
	# about request(date, ip, counter info).
	requests = [{"datetime": datetime.strptime(line[0], '%H:%M:%S %d/%m/%Y'), 
					"ip": line[1],
					"request_body": json.loads(line[2])} for line in search_result] 

	# Translate readout_dt "1465193586" --> "2016-06-06" in all measurments.					
	for request in requests:
		for counter in request.get("request_body").get("data"):
			counter["readout_dt"] = (date.fromtimestamp(int(counter["readout_dt"])))

	# Add a filter if request ip != kvargs["ip"], this request not add to result.
	if kvargs["ip"]:
		requests = filter(lambda request: request["ip"] == kvargs["ip"], requests)

	# Add a filter if request["datetime"] != kvargs['request_date'], this error not add to result.	
	if kvargs['request_date']:
		requests = filter(lambda request: 
			request["datetime"].strftime('%d %m %Y') == kvargs['request_date'].strftime('%d %m %Y'), 
			requests)

	# Add a filter if sn of counter != kvargs["sn"], this request not add to result.
	if kvargs['sn']:
		requests = filter(lambda request: 
			request.get("request_body").get("sn") == kvargs['sn'], requests)

	# Add a filter if measurment date "readout_dt" < kvargs['start_date'], 
	# this measurment not add to result.
	if kvargs['start_date']:
		for request in requests:
			request.get("request_body")["data"] = filter(
				lambda item: item["readout_dt"] >= datetime.date(kvargs['start_date']), 
				request.get("request_body")["data"])

		requests = filter(lambda request: 
			len(request.get("request_body").get("data")) >= 1, requests)

	# Sorting result list by date (early -> late).
	requests.sort(key = lambda i: i["datetime"], reverse = True)	
	return requests

@app.route('/')
def index():
	"""Render index page"""
	return render_template('index.html')

@app.route('/datareceiver', methods=['GET','POST'])
def datareceiver():
	"""Get data in JSON format from client and add information
	about requset in request.log. Return status: OK if success.

	"""
	if request.method == 'GET':
		return abort(404)
	logger = logging.getLogger('app.views')
	logger.setLevel(logging.INFO)

	logger.addHandler(request_file_hendler)
	data = request.get_json()
	logger.info('{}\n{}'.format(request.remote_addr, 
								json.dumps(data, encoding="ascii"))) 
	return jsonify({'status' : 'OK'}), 200

@app.route('/getlog', methods=['GET','POST'])
def getlog():
	"""Return to client render_template of error_log or request_log
	1. Get from client what type of log he want's to see (errors or requests).
	2. Get list of dictionaries from get_list_of_errors or get_list_of_requset
	with emty named arguments.
	3. Return to a client html page with content of  errors or requests log.

	"""
	if request.method == 'GET':
		return abort(404)
	
	filename =  get_file_name(request.get_json())
	with open(os.path.join(base_dir, filename)) as fd:
		full_log = fd.read()

	if not full_log:
		return jsonify({'log':'<pre></pre>', 'control': ''}), 200

	if filename == app.config['ERROR_LOG_FILE']:
		# Get list of errors.
		errors_list = get_list_of_errors(full_log, 
										 errors_type='', 
										 date='')

		# Get list of type of errors in errors.log.
		error_name_list = list(set([error['error_name'] for error in errors_list]))

		return jsonify({'log':render_template('errorlog.html', errors=errors_list), 
						'control': render_template('error_log_controle.html', 
												   error_name_list=error_name_list)})
	else:
		# Get list of requests.
		request_list = get_list_of_request(full_log, 
			                               ip="", 
			                               request_date="", 
			                               sn="", 
			                               start_date="")
		return jsonify({'log':render_template('requestlog.html', 
											   requests=request_list), 
						'control': ''})

@app.route('/errorlogfilter', methods=['GET','POST'])
def errorlogfilter():
	"""Return to client render_template of error_log with user filters:
	Method get JSON: {
		"errors" : string errors separeted by ' ' or empty string (i.e. all type)
		"date" : string (yyyy-mm-dd) choice by user(for filter)
	}

	"""
	if request.method == 'GET':
		return abort(404)
	else:
		data = request.get_json()
		if data["errors"]:
			errors = data["errors"].split()
		else:
			errors = data["errors"]

		date = get_date(data["date"])

		with open(os.path.join(base_dir, app.config['ERROR_LOG_FILE'])) as fd:
			full_log = fd.read()
		# If log is empty return empty response.
		if not full_log:
			return jsonify({'log':'<pre></pre>'}), 200
		# Get filtered errosr_list.
		errors_list = get_list_of_errors(full_log, errors_type=errors, date=date)
		error_name_list = list(set([error['error_name'] for error in errors_list]))	

	return jsonify({'log':render_template('errorlog.html', errors=errors_list), 
					'control': render_template('error_log_controle.html', 
											   error_name_list=error_name_list)})

def get_date(date):
	"""Translation string date -> datetime date or return empty string"""
	if date:
		return datetime.strptime(date, '%Y-%m-%d')
	return date

@app.route('/requestlogfilter', methods=['GET','POST'])
def requestlogfilter():
	"""Return to client render_template of request_log with user filters:
	Method get JSON: {
		"ip" : string ip choice by user(for filter)
			   or empty string (i.e. all ips)
		"request_date" : string (yyyy-mm-dd) request date choice 
						 by user(for filter) or empty string 
						 (i.e. all date)
		"sn" : string counter number choice by user(for filter)
			   or empty string (i.e. all sns)
		"start_date" : string (yyyy-mm-dd) request date choice 
					   by user(for filter) later that date 
					   measurment add in result or empty string 
					   (i.e. all date)
	}

	"""
	if request.method == 'GET':
		return abort(404)
	
	data = request.get_json()
	request_date = get_date(data["request_date"])
	start_date = get_date(data["start_date"])

	with open(os.path.join(base_dir, 
						   app.config['REQUEST_LOG_FILE'])) as fd:
		full_log = fd.read()
	# If log is empty return empty response.
	if not full_log:
		return jsonify({'log':'<pre></pre>'}), 200
	# Get filtered request_list.
	request_list = get_list_of_request(full_log, 
									   ip=data["ip"], 
									   request_date=request_date, 
									   sn=data["sn"], 
									   start_date=start_date) 

	return jsonify({'log':render_template('requestlog.html', 
										  requests=request_list)})