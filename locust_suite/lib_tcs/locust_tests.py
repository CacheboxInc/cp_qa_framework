import os
import sys
import json
import cp_global
import time
from time import strftime, gmtime
from configparser import SafeConfigParser


cwd = os.getcwd()
 
start_time = strftime("%Y%m%d%H%M", gmtime())

# Read the test setup details specfic test cases.


def init_locust():
   os.system("locust -f locust_suite/locustfile --csv=example")


