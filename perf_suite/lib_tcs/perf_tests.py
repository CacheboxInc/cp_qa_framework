import os
import sys
import json
from global_conf.config import *
from perf_suite.conf_tcs.config import *
from time import strftime, gmtime

start_time = strftime("%Y%m%d%H%M", gmtime())
cwd = os.getcwd()



def init_perf():
    run_tests()

    

##common function to start execution
def run_tests():
    report_file = cwd + REPORT_DIR + start_time +".html"    
	#Calling pytest function for executing the test
	#os.system("python3 perf_suite/tests/check_page_load_time.py")
    os.system("python3 -m pytest %s -s -v --tb=auto -l --html=%s" %(cwd+TC_DIR, report_file))
