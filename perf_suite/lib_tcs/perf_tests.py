import os
import sys
import json


# Read the test setup details specfic to MRC test cases.
def init_perf():
    # TBD : Move this to common framework lib and pass flags like unit, ui etc.
    # Depending on flags make logging specific to that test option.
    #logger = get_logger()
    # Phase 1: Test bed/environment configuration validation.
    #deploy_test_vms(logger)
    # Phase 2: We now have a test bed to execute MRC test cases.
    run_tests()

    # Phase 3: Test Suite execution report.
    #report_mgmt_update()
    
    # Phase 4: Cleanup of test setup.
    #shiva_the_destructor()

##common function to start execution
def run_tests():
        
	#Calling pytest function for executing the test
	os.system("python3 perf_suite/tests/check_page_load_time.py")


