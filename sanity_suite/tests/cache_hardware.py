import json
import argparse
import random
import requests
from sanity_suite.conf_tcs.config import *
from sanity_suite.lib_tcs.utils import *

requests.packages.urllib3.disable_warnings()

URL         = "https://%s:443"
CACHE_HARDWARE_URL = "/cache_hardware?cluster_id=%s&benchmark=%s&cluster_name=%s&vcenter_ip=%s"

'''
Automated test for:
	1. Get cache hardware details test

Sample test run:
python3 cache_hardware_test.py --appliance-ip 192.168.3.28 --cluster-id 192168189_C01 --cluster-name C01 --vcenter-ip 192.168.1.189




parser = argparse.ArgumentParser()
parser.add_argument('--appliance-ip', required=True, help='Appliance IP')
parser.add_argument('--cluster-id', required=True, help='Cluster Id')
parser.add_argument('--cluster-name', required=True, help='Cluster name')
parser.add_argument('--vcenter-ip', required=True, help='vCenter IP')
args         = parser.parse_args()'''
URL          = URL %(APPLIANCE_IP)

CACHE_HARDWARE_URL = CACHE_HARDWARE_URL  % (CLUSTER_ID, False, CLUSTER_NAME, VCENTER_IP)


def test_run(f):
    try:
       f()
    except Exception as err:
        import traceback
        traceback.print_exc()
        print("Failed test : %s" % f.__name__)
    

class CacheHardwareTest:
    def __init__(self, url):
        self.url       = url
        self.print_msg = "*" * 15

    def get(self, url, test_name, negative=False):
        response = requests.get("%s%s" %(URL, url), verify=False)
        assert(response.status_code == 200)

        print("test", " : ", test_name)
        print("status code", " : ", response.status_code)
        print("response", " : ", response.text)
        print("%sFinished %s%s\n" % (self.print_msg, test_name, self.print_msg))

@test_run
def test_get_cache_hardware_test():
    test_obj = CacheHardwareTest(URL)
    test_obj.get(CACHE_HARDWARE_URL, "test_get_cache_hardware_test")

