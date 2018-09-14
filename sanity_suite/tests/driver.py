from utils import *
import time

def run_scripts(appliance_test, guiselenium_test, args='none'):
    start_time = time.clock()
    # Generating the logfolder name
    logfolder = datetime.datetime.today().strftime('%Y%m%d_%H%M%S')
    logfolder = os.path.join(os.getcwd(), logfolder)
    testlist = appliance_test
    # Starting off the tests
    for test in testlist:
            os.system("python %s %s %s" % (test, args, logfolder))
    total_script_duration = str((time.clock() - start_time)/3600)
    if not os.path.isfile(os.path.join(os.getcwd(),"summary.obj")):
        summary_dict = {}
        with open('summary.obj', 'wb') as obj:
            pickle.dump(summary_dict, obj, protocol=pickle.HIGHEST_PROTOCOL)
    generate_report()

