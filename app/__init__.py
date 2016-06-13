from flask import Flask 

from loggers import error_file_hendler

app = Flask(__name__)
app.config.from_object('config')

if not app.config['DEBUG']:
	app.logger.addHandler(error_file_hendler)
	print("Debug mode : {}".format(app.config['DEBUG']))

from app import views
