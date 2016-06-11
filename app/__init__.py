from flask import Flask 
import logging

from loggers import error_file_hendler

app = Flask(__name__)
app.config.from_object('config')
if not app.config['DEBUG']:
	app.logger.addHandler(error_file_hendler)

from app import views