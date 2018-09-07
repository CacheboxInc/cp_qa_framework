import os
import sys
import json
import cp_global
#import unit_test_common_utils
#import pp
import logging
import colorlog
import time
from time import strftime, gmtime
from configparser import SafeConfigParser



cwd = os.getcwd()
config = SafeConfigParser()
config_file = os.getcwd()+"/unit_suite/conf_tcs/unit_setup.conf"
 
start_time = strftime("%Y%m%d%H%M", gmtime())

# Read the test setup details specfic test cases.


def init_unit():
    # TBD : Move this to common framework lib and pass flags like mrc, unit etc.
    # Depending on flags make logging specific to that test option.
    logger = get_logger()
    # Phase 1: MRC Test bed/environment configuration validation.
    #deploy_test_vms(logger)
    # Phase 2: We now have a test bed to execute MRC test cases.
    run_tests()

    # Phase 3: Test Suite execution report.
    #report_mgmt_update()
    
    # Phase 4: Cleanup of test setup.
    #shiva_the_destructor()

##common function to start execution.
def run_tests():
        config.read(config_file)
        tc_dir = cwd+config.get('setup', 'tc_dir')
        report_dir = config.get('setup', 'report_location')
        node = config.get('setup', 'node')
        report_file = os.getcwd()+start_time+".html"
        logger.info("Running test Unit test cases")
        logger.info("test case directory : %s",tc_dir)
	##Calling pytest function for executing the test
        os.system("python3 -m pytest %s -v --tb=line --html=%s -n %s" % (tc_dir , report_file , node))

# Currently, logging happens at the test suite level.
# TBD : TC Level logging and process level logging
def get_logger():

        global logger
        path = os.getcwd() + "/unit_suite/logs_tcs/"
        #from logging.handlers import TimedRotatingFileHandler
        #logger = TimedRotatingFileHandler(LOG_FILE, when=LOG_ROTATION_TIME)
        # __name__ is a better choice as one exactly which module called logger.
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        # Unique name for each run of mrc tests.
        nowtime = strftime("%Y-%m-%d-%H-%M", gmtime())
        path = path + "Unit-Tests" + nowtime + ".log"
        global unit_log_name
        unit_log_name = path
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

        logger.info("Setting up and Returning MRC test suite logger")
        return logger

