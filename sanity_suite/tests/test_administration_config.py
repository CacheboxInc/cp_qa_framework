
#Copyright 2018 PrimaryIO, Pvt. Ltd. All rights reserved.
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
from global_conf.config import logger
from sanity_suite.lib_tcs.utils import *
from global_utils.vmware_utils.vm_utils_rest import *
from global_utils.vmware_utils.vm_details import get_cluster_moid

requests.packages.urllib3.disable_warnings()

cluster_moid = get_cluster_moid(VCENTER_IP,VCENTER_USERNAME,VCENTER_PASSWORD,VCENTER_CLUSTER)

URL= "https://%s"
url = "/hdm/clusters?vcenter_ip=%s"%(cluster_moid , VCENTER_IP)


URL      = URL % (APPLIANCE_IP)
headers = {'Content-type': 'application/json'}


class Administration_Conf_Test(unittest.TestCase):

   def test_1_cluster(self):
      logger.info("Running Number of VM test cases")
      expected_count = len(get_vms_cluster(VCENTER_IP, VCENTER_USERNAME,VCENTER_PASSWORD,cluster_moid))
      logger.info("Total vm present on the Onprem Vcenter : %s"%expected_count)
      response = requests.get("%s%s" %(URL, url), headers=headers, verify=False)
      print("%s%s" %(URL, url))
      assert response.status_code == 200 , "Response code is not 200"
      profile_page_response = json.loads(response.text)
      vm_list = profile_page_response["data"]["vmc"]["resource_assesment"]
      actual_count = len(vm_list)
      logger.info("Total vm present on the On cloud burst page : %s"%actual_count)
      assert expected_count == (actual_count+1) , "Vm count on vcenter and appliance is not matching"



