import json
import argparse
import random
import requests

from sanity_suite.conf_tcs.config import *
from sanity_suite.lib_tcs.utils import *


requests.packages.urllib3.disable_warnings()

URL         = "https://%s:443" %(APPLIANCE_IP)
SETTINGS_URL = "/planning?cluster_id=%s&cluster_name=%s&vcenter_ip=%s" %(CLUSTER_ID,CLUSTER_NAME,VCENTER_IP)

'''
Automated test for:
	1. Get APA planning test

Sample test run:
python3 apa_planning_test.py --appliance-ip 192.168.3.28 --cluster-id 192168189_C01 --cluster-name C01 --vcenter-ip 192.168.1.189




parser = argparse.ArgumentParser()
parser.add_argument('--appliance-ip', required=True, help='Appliance IP')
parser.add_argument('--cluster-id', required=True, help='Cluster Id')
parser.add_argument('--cluster-name', required=True, help='Cluster name')
parser.add_argument('--vcenter-ip', required=True, help='vCenter IP')
args         = parser.parse_args()
URL          = URL % args.appliance_ip
SETTINGS_URL = SETTINGS_URL  % (args.cluster_id, args.cluster_name, args.vcenter_ip)'''




def test_run(f):
    try:
       f()
    except Exception as err:
        import traceback
        traceback.print_exc()
        print("Failed test : %s" % f.__name__)
    

class PlanningTest:
    def __init__(self, url):
        self.url       = url
        self.print_msg = "*" * 15

    def get(self, url, test_name, negative=False):
        response = requests.get("%s%s" %(URL, url), verify=False)
        if negative is True:
            assert(response.status_code != 200)
        else:
            assert(response.status_code == 200)

        print("test", " : ", test_name)
        print("status code", " : ", response.status_code)
        print("response", " : ", response.text)
        print("%sFinished %s%s\n" % (self.print_msg, test_name, self.print_msg))

@test_run
def test_get_apa_planning():
    test_obj = PlanningTest(URL)
    test_obj.get(SETTINGS_URL, "test_get_apa_planning")

