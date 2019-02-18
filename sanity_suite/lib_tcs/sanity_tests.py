import os
import sys
import json
import cp_global
#import sanity_test_common_utils
#import pp
import logging
import colorlog
import time
from time import strftime, gmtime
from configparser import SafeConfigParser
from sanity_suite.conf_tcs.config import *
from sanity_suite.conf_tcs.config import logger
from global_utils.email_util import *

cwd = os.getcwd()
config = SafeConfigParser()
config_file = os.getcwd()+"/sanity_suite/conf_tcs/sanity_setup.conf"
 
start_time = strftime("%Y%m%d%H%M", gmtime())

# Read the test setup details specfic test cases.


def init_sanity():
    # TBD : Move this to common framework lib and pass flags like mrc, sanity etc.
    
    run_tests()

def run_tests():
        #config.read(config_file)
        #tc_dir = cwd+config.get('setup', 'tc_dir')
        #report_dir = config.get('setup', 'report_location')
        xml_report_dir = cwd + XML_REPORT_DIR + start_time+".xml"

        #node = config.get('setup', 'node')
        report_file = os.getcwd() + REPORT_DIR + start_time +".html"
        logger.info("Running test sanity test cases")
        logger.info("test case directory : %s", cwd+TC_DIR)
	##Calling pytest function for executing the test
        os.system("python3 -m pytest %s -s -v --tb=auto -l --html=%s -n %s --junitxml=%s" % (cwd+TC_DIR , report_file , NODES , xml_report_dir  ))
        os.system("scp %s %s@%s:%s" %(report_file ,SERVER_USER,REPORT_LOCATION_SERVER, REPORT_LOCATION))
        time.sleep(5)
        link = "http://%s/%s/%s"%(REPORT_LOCATION_SERVER,REPORT_LOCATION,start_time +".html")
        send_mail(link,EMAIL_IDS)




"""
# Currently, logging happens at the test suite level.
# TBD : TC Level logging and process level logging
def get_logger():

        #global logger
        path = os.getcwd() + "/sanity_suite/logs_tcs/"
        #from logging.handlers import TimedRotatingFileHandler
        #logger = TimedRotatingFileHandler(LOG_FILE, when=LOG_ROTATION_TIME)
        # __name__ is a better choice as one exactly which module called logger.
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        # Unique name for each run of mrc tests.
        nowtime = strftime("%Y-%m-%d-%H-%M", gmtime())
        path = path + "sanity-Tests" + nowtime + ".log"
        global sanity_log_name
        sanity_log_name = path
        handler = logging.FileHandler(path)
        handler.setLevel(logging.INFO)

        # Create a common logging format
        # Return a logger with a default ColoredFormatter.
        # You can also call logger.exception(msg, *args), it equals to logger.error(msg, exc_info=True, *args).
        formatter = colorlog.ColoredFormatter(
                "%(log_color)s%(asctime)s-%(name)s-%(levelname)-4s%(reset)s%(white)s-%(message)s",
                datefmt=None,
                reset=True,
                log_colors={
                        'DEBUG': 'cyan',
                        'INFO': 'green',
                        'WARNING': 'yellow',
                        'ERROR': 'red',
                        'CRITICAL': 'red',
                }
        )
        handler.setFormatter(formatter)

        # Add the handlers to the logger
        logger.addHandler(handler)

        consoleHandler = logging.StreamHandler()
        consoleHandler.setFormatter(formatter)
        logger.addHandler(consoleHandler)

        logger.info("Setting up and Returning Sanity test suite logger")
        return logger
"""
