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
DEMO_URL = "/automigrateback"


#args     = parser.parse_args()
URL      = URL % (APPLIANCE_IP)
headers = {'Content-type': 'application/json'}

class AutoMigrateBackTest(unittest.TestCase):

    url = URL
    vc_ip = VCENTER_IP
    data = {}
    data["vcenter_ip"]   = vc_ip
    data["cluster_id"]   = CLUSTER_ID
    data["cluster_name"] = CLUSTER_NAME
    data["flush_flag"]   = FLUSH_FLAG
    data["poweron_flag"] = POWERON_FLAG
    data["vm_names"]     = VM_NAME

    data_invalid  = {}
    data_invalid["vcenter_ip"]   = vc_ip
    data_invalid["cluster_id"]   = CLUSTER_ID
    data_invalid["cluster_name"] = CLUSTER_NAME
    data_invalid["vm_names"]     = "invalid"
 
 
    # Tests the return code of the POST response
    #
    def test_1(self, url=DEMO_URL, test_name="Test_post", negative=False):
        logger.debug("\n\nTest Name : ", test_name)
        response = requests.post("%s%s" %(URL, url), json=self.data, headers=headers, verify=False)
        assert(response.status_code == 200)
        logger.debug("Status Code : ", response.status_code)
        logger.debug("%s Finished" % test_name)

    #
    # 
    #
    def test_2(self, url=DEMO_URL, test_name="Test_post_response", negative=False):
        logger.debug("\n\nTest Name : ", test_name)
        response = requests.post("%s%s" %(URL, url), json=self.data_invalid, headers=headers, verify=False)
 
        assert(response.status_code != 200)

        logger.debug("Status Code : ", response.status_code)
        logger.debug("Resp : ", response.json())
        logger.debug("%s Finished" % test_name)

if __name__ == "__main__":
    test_obj = AutoMigrateBackTest()
    test_obj.test_1(DEMO_URL, "Test_post")
    test_obj.test_2(DEMO_URL, "Test_post_response")
