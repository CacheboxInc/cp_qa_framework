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

URL          = "https://%s:443"
POLICY_URL = "/policy?cluster_id=%s&cluster_name=%s&vcenter_ip=%s"
#POLICY_URL = "/policy?vcenter_ip=%s"
#POLICY_URL = "/policy"

POLICY_URL = POLICY_URL % (CLUSTER_ID, CLUSTER_NAME, VCENTER_IP)

#POLICY_URL = POLICY_URL % args.vcenter_ip

class PolicyTest(unittest.TestCase):
    #
    # Tests the return code of the response
    #
    def test_1(self):
        logger.info("Running the test case 1")
        response = requests.get("%s%s" %(URL, POLICY_URL), verify=False)
        logger.info("Status Code : ", response.status_code)
        logger.info("Resp : ", response.json())
        assert response.status_code == 200, "Wrong Policy URL"

    #
    # Tests the post call
    #
    """def test_2(self):
        logger.info("Running the policy tests")
        data_post = {'policy_cache_size' : 510, 'policy_rto' : 590, 'policy_rpo' : 580, 'policy_cost_threshold' : 5000}
        response = requests.post("%s%s" %(URL, POLICY_URL), data=data_post, verify=False)
        logger.info("Status Code : ", response.status_code)
        logger.info("Resp : ", response.json())
        assert (response.status_code == 200 , "Policy post URL is not working")


    def test_3(self):
        logger.info("Runnng the post URL with all values as None")
        data_put = {'policy_cache_size' : 'None', 'policy_rto' : 'None', 'policy_rpo' : 'None', 'policy_cost_threshold' : 'None'}
        response = requests.put("%s%s" %(URL, POLICY_URL), data=data_put, verify=False)
        logger.info("Status Code : ", response.status_code)
        logger.info("Resp : ", response.json())
        assert(response.status_code == 200)



    #
    # Tests the delete call
    #
    def test_4(self):
        logger.info("Running the delete call URL")
        response = requests.delete("%s%s" %(URL, POLICY_URL), verify=False)
        logger.info("Status Code : ", response.status_code)
        logger.info("Resp : ", response.json())
        assert(response.status_code == 200)"""
