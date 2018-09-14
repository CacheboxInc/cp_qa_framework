import json
import argparse
import random
import requests
from sanity_suite.conf_tcs.config import *
from sanity_suite.lib_tcs.utils import *

requests.packages.urllib3.disable_warnings()

URL         = "https://%s:443"
SETTINGS_URL = "/settings/cache_threshold?cluster_id=%s&cluster_name=%s&vcenter_ip=%s"

'''
Automated test for:
	1. Get health threshold settings
	2. Set threshold for IOPS
	3. Set threshold for Throughput
	4. Set threshold for Latency
	5. Set threshold for IOPS and Throughput
	6. Set threshold for Throughput and Latency
	7. Set threshold for Throughput, Latency and IOPS

Sample test run:
python3  threshold_setting_test.py --appliance-ip 192.168.3.28 --cluster-id 192168189_C01 --cluster-name C01 --vcenter-ip 192.168.1.189




parser = argparse.ArgumentParser()
parser.add_argument('--appliance-ip', required=True, help='Appliance IP')
parser.add_argument('--cluster-id', required=True, help='Cluster Id')
parser.add_argument('--cluster-name', required=True, help='Cluster name')
parser.add_argument('--vcenter-ip', required=True, help='vCenter IP')
args         = parser.parse_args()'''
URL          = URL % (APPLIANCE_IP)
SETTINGS_URL = SETTINGS_URL  % (CLUSTER_ID, CLUSTER_NAME, VCENTER_IP)


def test_run(f):
    try:
       f()
    except Exception as err:
        import traceback
        traceback.print_exc()
        print("Failed test : %s" % f.__name__)
    

class CacheThresholdTest:
    def __init__(self, url):
        self.url       = url
        self.print_msg = "*" * 15

    def post(self, data, url, test_name):
        response = requests.post("%s%s" %(URL, url), json=data, verify=False)
        assert(response.status_code == 200)
        print("test", " : ", test_name)
        print("status code", " : ", response.status_code)
        print("response", " : ", response.text)
        print("%sFinished %s%s\n" % (self.print_msg, test_name, self.print_msg))

    def get(self, url, test_name):
        response = requests.get("%s%s" %(URL, url), verify=False)
        assert(response.status_code == 200)
        print("test", " : ", test_name)
        print("status code", " : ", response.status_code)
        print("response", " : ", response.text)
        print("%sFinished %s%s\n" % (self.print_msg, test_name, self.print_msg))

@test_run
def test_get_cache_threshold01():
    test_obj = CacheThresholdTest(URL)
    test_obj.get(SETTINGS_URL, "test_get_cache_threshold_01")    

@test_run
def test_set_cache_threshold():
    test_obj = CacheThresholdTest(URL)
    data     = {
                 "cache_size_per_node": 2,
                 "iops_limit": {
                     "read": 20,
                     "write": 50
                 },
                 "cache_thresholds": 40
               }
    data = {
              "data"          : data,
              "cluster_id"    : args.cluster_id,
              "cluster_name"  : args.cluster_name,
              "vcenter_ip"    : args.vcenter_ip
           }

    test_obj.post(data, SETTINGS_URL, "test_set_cache_threshold")

@test_run
def test_get_cache_threshold02():
    test_obj = CacheThresholdTest(URL)
    test_obj.get(SETTINGS_URL, "test_get_cache_threshold_02")

