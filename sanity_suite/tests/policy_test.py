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
import traceback
from sanity_suite.conf_tcs.config import *
from sanity_suite.lib_tcs.utils import *
from sanity_suite.tests.pbm_utils import *
from sanity_suite.tests.vim_utils import *

requests.packages.urllib3.disable_warnings()

URL          = "https://%s:443"
POLICY_URL = "/policy?cluster_id=%s&cluster_name=%s&vcenter_ip=%s"
#POLICY_URL = "/policy?vcenter_ip=%s"
#POLICY_URL = "/policy"

'''
Test for:
	1. Get policy test

Sample test run:
python3.5 policy_test.py --appliance-ip 192.168.3.76 --cluster-id 192168140_Cluster --cluster-name Cluster --vcenter-ip 192.168.1.40 --vcenter-username administrator@vsphere.local --vcenter-password Naruto@123

'''

"""parser = argparse.ArgumentParser()
parser.add_argument('--appliance-ip', required=True, help='Appliance IP')
parser.add_argument('--cluster-id', required=True, help='Cluster Id')
parser.add_argument('--cluster-name', required=True, help='Cluster Name')
parser.add_argument('--vcenter-ip', required=True, help='vCenter IP')
parser.add_argument('--vcenter-username', required=True, help='vCenter Username')
parser.add_argument('--vcenter-password', required=True, help='vCenter Password')
args       = parser.parse_args()
#URL        = URL % args.appliance_ip
#POLICY_URL = POLICY_URL % (args.cluster_id, args.cluster_name, args.vcenter_ip)"""

URL        = URL % APPLIANCE_IP
POLICY_URL = POLICY_URL % (CLUSTER_ID, CLUSTER_NAME, VCENTER_IP)

#POLICY_URL = POLICY_URL % args.vcenter_ip

class PolicyTest:
    def __init__(self, url, vc_ip, vc_username, vc_password, cluster_name):
        self.url     = url

    #
    # Tests the return code of the response
    #
    def test_1(self, url, test_name, negative=False):
        print("\n\nTest Name : ", test_name)
        response = requests.get("%s%s" %(URL, url), verify=False)
        if negative is True:
            assert(response.status_code != 200)
        else:
            assert(response.status_code == 200)
        print("Status Code : ", response.status_code)
        print("%s Finished" % test_name)

    #
    # Test the response's data
    #
    def test_2(self, url, test_name, negative=False):
        print("\n\nTest Name : ", test_name)
        response = requests.get("%s%s" %(URL, url), verify=False)
        if negative is True:
            assert(response.status_code != 200)
        else:
            assert(response.status_code == 200)
        print("Status Code : ", response.status_code)
        print("Resp : ", response.json())
        print("%s Finished" % test_name)


    #
    # Tests the post call
    #
    def test_3(self, url, test_name, negative=False):
        print("\n\nTest Name : ", test_name)
        data_post = {'policy_cache_size' : 510, 'policy_rto' : 590, 'policy_rpo' : 580, 'policy_cost_threshold' : 5000}
        response = requests.post("%s%s" %(URL, url), data=data_post, verify=False)
        if negative is True:
            assert(response.status_code != 200)
        else:
            assert(response.status_code == 200)

        print("Status Code : ", response.status_code)
        print("Resp : ", response.json())
        print("%s Finished" % test_name)


    #
    # Tests the put call
    #
    def test_4(self, url, test_name, negative=False):
        print("\n\nTest Name : ", test_name)
        data_put = {'policy_cache_size' : 'None', 'policy_rto' : 'None', 'policy_rpo' : 'None', 'policy_cost_threshold' : 'None'}
        response = requests.put("%s%s" %(URL, url), data=data_put, verify=False)
        if negative is True:
            assert(response.status_code != 200)
        else:
            assert(response.status_code == 200)

        print("Status Code : ", response.status_code)
        print("Resp : ", response.json())
        print("%s Finished" % test_name)


    #
    # Tests the delete call
    #
    def test_5(self, url, test_name, negative=False):
        print("\n\nTest Name : ", test_name)
        response = requests.delete("%s%s" %(URL, url), verify=False)
        if negative is True:
            assert(response.status_code != 200)
        else:
            assert(response.status_code == 200)

        print("Status Code : ", response.status_code)
        print("Resp : ", response.json())
        print("%s Finished" % test_name)


if __name__ == "__main__":
    test_obj = PolicyTest(URL, args.vcenter_ip, args.vcenter_username, args.vcenter_password, args.cluster_name)
    test_obj.test_1(POLICY_URL, "Test_get")
    test_obj.test_2(POLICY_URL, "Test_output")
    test_obj.test_3(POLICY_URL, "Test_post")
    test_obj.test_4(POLICY_URL, "Test_put")
    test_obj.test_5(POLICY_URL, "Test_delete")
