import logging

error_file_hendler = logging.FileHandler('errors.log', mode = 'a')
error_file_hendler.setLevel(logging.ERROR)
format_error = logging.Formatter("%(asctime)s - %(message)s \n", datefmt='%I:%M:%S %d/%m/%Y')
error_file_hendler.setFormatter(format_error)


request_file_hendler = logging.FileHandler('request.log', mode = 'a')
format_request = logging.Formatter("%(asctime)s - %(message)s", datefmt='%I:%M:%S %d/%m/%Y')
request_file_hendler.setFormatter(format_request)