import logging
import config

error_file_hendler = logging.FileHandler(config.ERROR_LOG_FILE, mode = 'a')
error_file_hendler.setLevel(logging.ERROR)
format_error = logging.Formatter("##%(asctime)s - %(message)s\n", datefmt='%H:%M:%S %d/%m/%Y')
error_file_hendler.setFormatter(format_error)


request_file_hendler = logging.FileHandler(config.REQUEST_LOG_FILE, mode = 'a')
format_request = logging.Formatter("%(asctime)s - %(message)s", datefmt='%H:%M:%S %d/%m/%Y')
request_file_hendler.setFormatter(format_request)