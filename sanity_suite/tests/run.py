import getopt
import sys
import os
from driver import *

def getargs(argv):
    try:
        optlist, args = getopt.getopt(argv[1:], '')
    except getopt.GetoptError:
        sys.exit(2)
    return args  #['run.py', 'pio_install.py', 'class1.test1'], run.py would be discarded

APPLIANCE_SPECIFIC_TESTS=[
    "add_delete_vcenter.py",
    "pio_install.py",
    "pio_appliance_operations.py",
    "pio_dashboard_operations.py",
    "pio_install_negative.py",
    "pio_login.py",
    "pio_uninstall_negative.py",
    "test_xmlrpc.py",
    "test_key_manager.py"
    ]

GUI_SPECIFIC_TESTS=[
    
    ]


if __name__ == '__main__':
        
    # Handling a specific test run from the user
    # eg: pio_install.py InstallQA.test_1  # here just one test thats test_1 is executed
    if len(sys.argv) > 1:
        testname, args = getargs(sys.argv)
        if testname in APPLIANCE_SPECIFIC_TESTS:
            run_scripts([testname], [], args)
        elif testname in GUI_SPECIFIC_TESTS:
            run_scripts([], [testname], args)
    else: # Here we are executing all the tests in the script
        run_scripts(APPLIANCE_SPECIFIC_TESTS, GUI_SPECIFIC_TESTS)
