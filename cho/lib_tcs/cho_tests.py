import os
import sys
import json
import cp_global
#import sanity_test_common_utils
#import pp
import time
from time import strftime, gmtime
from configparser import SafeConfigParser
from cho.conf_tcs.config import *
from cho.conf_tcs.config import logger


cwd = os.getcwd()
 
start_time = strftime("%Y%m%d%H%M", gmtime())

# Read the test setup details specfic test cases.


def init_cho():
    run_tests()
    
##common function to start execution.
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
        os.system("python3 -m pytest %s -s -v --tb=auto -l --html=%s --junitxml=%s" % (cwd+TC_DIR , report_file , xml_report_dir  ))
        os.system("scp %s %s" %(report_file , REPORT_LOCATION_SERVER))




