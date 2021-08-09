import argparse, json, logging, os, urllib3

urllib3.disable_warnings()

class Logger():

    logger = None

    def __init__(self, name):
        self.configure_logger(name)
        
    def configure_logger(self, name):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        log_file_handler = logging.FileHandler(filename="{name}_log".format(name=name))
        formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
        log_file_handler.setFormatter(formatter)
        self.logger.addHandler(log_file_handler)

    def info(self, message):
        print("INFO: {message}".format(message=message))
        self.logger.info(message)

    def error(self, message):
        print("ERROR: {message}".format(message=message))
        self.logger.error(message)

    def debug(self, message):
        print("DEBUG: {message}".format(message=message))
        self.logger.debug(message)