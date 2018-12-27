#
# Copyright 2018 PrimaryIO, Pvt. Ltd. All rights reserved.
# This software is property of PrimaryIO, Pvt. Ltd. and
# contains trade secrets, confidential & proprietary
# information. Use, disclosure or copying this without
# explicit written permission from PrimaryIO, Pvt. Ltd.
# is prohibited.
#
# Author: PrimaryIO, Pvt. Ltd. (sales@primaryio.com)
#
import argparse
import json
import requests
import time
import traceback

from sanity_suite.conf_tcs.config import *
from sanity_suite.lib_tcs.utils import *
from global_utils.vmware_utils.vm_utils_rest import *

requests.packages.urllib3.disable_warnings()

URL        = "https://%s:443"
DEMO_URL = "/automigrate"

'''
Test for:
	1.  Auto migrations

Sample test run:
-> Without Cluster info
 python3.5 automigrate_test.py --appliance-ip 192.168.5.140 --vcenter-ip 192.168.1.27 --vm-names Ubuntu_1 Ubuntu_2 Ubuntu_3
-> With Cluster info
 python3.5 automigrate_test.py --appliance-ip 192.168.5.140 --cluster-id 192168127_UI_Cluster --cluster-name UI_Cluster --vcenter-ip 192.168.1.27 --vm-names Ubuntu_1 Ubuntu_2 Ubuntu_3


parser = argparse.ArgumentParser()
parser.add_argument('--appliance-ip', required=True, help='Appliance IP')
parser.add_argument('--cluster-id', required=False, help='Cluster Id', default=None)
parser.add_argument('--cluster-name', required=False, help='Cluster Name', default=None)
parser.add_argument('--vcenter-ip', required=True, help='vCenter IP')
parser.add_argument('--vm-names', required=True, nargs='+', help='VM Name(s)') '''

URL      = URL % (APPLIANCE_IP)
headers = {'Content-type': 'application/json'}

class AutoMigrateTest(unittest.TestCase):
        
    url = URL
    vc_ip = VCENTER_IP
    data = {}
    data["vcenter_ip"]   = vc_ip
    data["vm_names"]     = [VM_NAME]

    data_invalid  = {}
    data_invalid["vcenter_ip"]   = vc_ip
    data_invalid["vm_names"]     = ["invalid"]
 
 
    # Tests the return code of the POST response
    #
    def test_1(self, url=DEMO_URL, test_name="Test_post", negative=False):
        logger.info("\n\nTest Name : %s" %test_name)
        #Power off vm
        do_power_off(VM_NAME,VCENTER_IP)
        response = requests.post("%s%s" %(URL, url), json=self.data, headers=headers, verify=False)
        assert(response.status_code == 200)
        
        logger.info("Status Code : %s" %response.status_code)
        if response.status_code == 200:
            time.sleep(100)
            assert(vm_present_on_vcenter(CLOUD_IP, VM_NAME), "%s not found on the cloud"%VM_NAME )

    #
    #Negative testing
    #
    def test_2(self, url=DEMO_URL, test_name="Negative testing", negative=False):
        logger.debug("\n\nTest Name : %s" % test_name)
        response = requests.post("%s%s" %(URL, url), json=self.data_invalid, headers=headers, verify=False)
        logger.info("Negative test")
        logger.info("Status Code : %s" %(response.status_code))
        logger.info("Resp : %s" %(response.json()))
        logger.info("%s Finished" % test_name)
        assert(response.status_code != 200)


if __name__ == "__main__":
    test_obj = AutoMigrateTest()
    test_obj.test_1(DEMO_URL, "Test_post")
    ##test_obj.test_2(DEMO_URL, "Test_post_response")
