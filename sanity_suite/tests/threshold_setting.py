import json
import argparse
import random
import requests
from sanity_suite.conf_tcs.config import *
from sanity_suite.lib_tcs.utils import *

requests.packages.urllib3.disable_warnings()

URL         = "https://%s:443"
SETTINGS_URL = "/settings/threshold?cluster_id=%s&cluster_name=%s&vcenter_ip=%s"

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

config = {
           "cluster_id"   : CLUSTER_ID,
           "cluster_name" : CLUSTER_NAME,
           "vcenter_ip"   : VCENTER_IP
         }

def test_run(f):
    try:
       f()
    except Exception as err:
        import traceback
        traceback.print_exc()
        print("Failed test : %s" % f.__name__)
    
class ThresholdTest:
    def __init__(self, url):
        self.url       = url
        self.print_msg = "*" * 15
    def post(self, data, url, test_name):
        response = requests.post("%s%s" %(URL, url), json=data, verify=False)
        print("test", " : ", test_name)
        print("status code", " : ", response.status_code)
        print("response", " : ", response.text)
        print("%sFinished %s%s\n" % (self.print_msg, test_name, self.print_msg))
        return response

    def get(self, url, test_name):
        response = requests.get("%s%s" %(URL, url), verify=False)
        print("test", " : ", test_name)
        print("status code", " : ", response.status_code)
        print("response", " : ", response.text)
        print("%sFinished %s%s\n" % (self.print_msg, test_name, self.print_msg))
        return response

@test_run
def test_get_health_threshold_01():
    test_obj = ThresholdTest(URL)
    test_obj.get(SETTINGS_URL, "test_get_health_threshold_01")    

@test_run
def test_set_health_threshold_iops():
    test_obj = ThresholdTest(URL)
    data     = {
                 "iops" : { 
                            "low"  : 11,
                            "high" : 50
                          }
               }
    data = {"data" : data}
    data.update(config)
    test_obj.post(data, SETTINGS_URL, "test_set_health_threshold_iops")

@test_run
def test_set_health_threshold_throughput():
    test_obj = ThresholdTest(URL)
    data     = {
                 "throughput" : { 
                                  "low"  : 13,
                                  "high" : 59
                                }
               }
    data = {"data" : data}
    data.update(config)
    test_obj.post(data, SETTINGS_URL, "test_set_health_threshold_throughput")

@test_run
def test_set_health_threshold_latency():
    test_obj = ThresholdTest(URL)
    data     = {
                 "latency" : {
                               "4k" : {
                                        "low"  : 1,
                                        "high" : 10
                                      }
                             }
               }
    data = {"data" : data}
    data.update(config)
    response = test_obj.post(data, SETTINGS_URL, "test_set_health_threshold_latency")
    assert(response.status_code == 200)

@test_run
def test_set_health_threshold_throughput_iops():
    test_obj = ThresholdTest(URL)
    data     = {
                 "throughput" : {
                                  "low"  : 1,
                                  "high" : 59
                                },
                 "iops"       : {
                                  "low"  : 11,
                                  "high" : 50
                                }
               }
    data = {"data" : data}
    data.update(config)
    response = test_obj.post(data, SETTINGS_URL, "test_set_health_threshold_throughput_iops")
    assert(response.status_code == 200)

@test_run
def test_set_health_threshold_throughput_latency():
    test_obj = ThresholdTest(URL)
    data     = {
                 "throughput" : {
                                  "low"  : 1,
                                  "high" : 9
                                },
                 "latency" :    {
                                  "4k" : {
                                           "low"  : 1,
                                           "high" : 15
                                         }
                                }
               }
    data = {"data" : data}
    data.update(config)
    response = test_obj.post(data, SETTINGS_URL, "test_set_health_threshold_throughput_latency")
    assert(response.status_code == 200)

@test_run
def test_set_health_threshold_throughput_latency_iops():
    test_obj = ThresholdTest(URL)
    data     = {
                 "throughput" : {
                                  "low"  : 1,
                                  "high" : 9
                                },
                 "latency" :    {
                                  "4k" : {
                                           "low"  : 1,
                                           "high" : 15
                                         }
                                },
                 "iops"       : {
                                  "low"  : 11,
                                  "high" : 50
                                }

               }
    data = {"data" : data}
    data.update(config)
    response = test_obj.post(data, SETTINGS_URL, "test_set_health_threshold_throughput_latency_iops")
    assert(response.status_code == 200)

@test_run
def test_get_health_threshold_02():
    test_obj = ThresholdTest(URL)
    test_obj.get(SETTINGS_URL, "test_get_health_threshold_02")
