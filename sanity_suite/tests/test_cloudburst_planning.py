

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

requests.packages.urllib3.disable_warnings()

URL= "https://%s"
url = "/recommendation?is_profiling=False&vcenter_ip=%s"%(VCENTER_IP)

URL      = URL % (APPLIANCE_IP)
headers = {'Content-type': 'application/json'}

class planning_Test(unittest.TestCase):

   def test_1_vm_count(self):
      logger.info("Running Number of VM test cases")
      expected_count = len(get_vms_vcenter(VCENTER_IP))
      logger.info("Total vm present on the Onprem Vcenter : %s"%expected_count)
      response = requests.get("%s%s" %(URL, url), headers=headers, verify=False)
      assert response.status_code == 200 , "Response code is not 200" 
      profile_page_response = json.loads(response.text)
      vm_list = profile_page_response["data"]["vmc"]["resource_assesment"]
      actual_count = len(vm_list)
      logger.info("Total vm present on the On cloud burst page : %s"%actual_count)
      assert expected_count == (actual_count+1) , "Vm count on vcenter and appliance is not matching"

   def test_2_primaryio_component(self):
      logger.info("Runningtest cases for checking primaryIO compenents are not listed in VM lists")
      response = requests.get("%s%s" %(URL, url), headers=headers, verify=False)
      assert response.status_code == 200 , "Response code is not 200"
      profile_page_response = json.loads(response.text)
      total_resources = profile_page_response["data"]["vmc"]["resource_assesment"]
      vm_names=[]
      for resource in total_resources:
         vm_names.append(resource["name"])
      vm_names.sort()
      logger.info("Total vm present on the profiling page : %s"%vm_names)
      assert "PrimaryIO-OnPrem-Manager-0" not in vm_names , "PrimaryIO-OnPrem-Manager-0 is listed on profiling page"


   
   def test_3_vm_count(self):
      logger.info("Running Number of VM test cases")
      expected_names = get_vms_vcenter(VCENTER_IP)
      expected_names.remove("PrimaryIO-OnPrem-Manager-0")
      expected_names.sort()
      logger.info("Total vm present on the Onprem Vcenter : %s"%expected_names)
      print("Total vm present on the Onprem Vcenter : %s"%expected_names)
      response = requests.get("%s%s" %(URL, url), headers=headers, verify=False)
      assert response.status_code == 200 , "Response code is not 200"
      profile_page_response = json.loads(response.text)
      total_resources = profile_page_response["data"]["vmc"]["resource_assesment"]
      vm_names=[]
      for resource in total_resources:
         vm_names.append(resource["name"])
      vm_names.sort()
      logger.info("Total vm present on the profiling page : %s"%vm_names)
      assert expected_names==vm_names , "Vm count on vcenter and appliance is not matching"



