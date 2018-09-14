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


requests.packages.urllib3.disable_warnings()

URL        = "https://%s:443"
DEMO_URL = "/tag/assignment"

'''
Test for:
	1.  Tag Assignment

Sample test run:
python3.5 tagassignment_test.py --appliance-ip 192.168.5.140 --vcenter-ip 192.168.1.27 --tag-name Workload1


parser = argparse.ArgumentParser()
parser.add_argument('--appliance-ip', required=True, help='Appliance IP')
parser.add_argument('--vcenter-ip', required=True, help='vCenter IP')
parser.add_argument('--tag-name', required=True, help='Tag Name')
args     = parser.parse_args()'''
URL      = URL % (APPLIANCE_IP)
headers = {'Content-type': 'application/json'}

class TagAssignmentTest:
    def __init__(self):
        self.url = URL
        self.vc_ip = VCENTER_IP
        self.data = {}
        self.data["tag_name"]   = TAG_NAME
        self.data["vm_names"]   = ["Ubuntu_2"]

    #
    # Tests the return code of the POST response
    #
    def test_1(self, url, test_name, negative=False):
        print("\n\nTest Name : ", test_name)
        response = requests.post("%s%s" %(URL, url), json=self.data, headers=headers, verify=False)
        if negative is True:
            assert(response.status_code != 200)
        else:
            assert(response.status_code == 200)
        print("Status Code : ", response.status_code)
        print("%s Finished" % test_name)

if __name__ == "__main__":
    #test_obj = TagAssignmentTest(URL, args.vcenter_ip, args.tag_name)
    test_obj.test_1(DEMO_URL, "Test_post")
