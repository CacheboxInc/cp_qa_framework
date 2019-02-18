

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
from global_utils.vmware_utils.renamer import *

requests.packages.urllib3.disable_warnings()

cluster_moid = get_cluster_moid(VCENTER_IP,VCENTER_USERNAME,VCENTER_PASSWORD,VCENTER_CLUSTER)

URL= "https://%s"
url = "//recommendation?cluster_moid=%s&cloud=vmc&is_profiling=True&vcenter_ip=%s"%(cluster_moid , VCENTER_IP)

URL      = URL % (APPLIANCE_IP)
headers = {'Content-type': 'application/json'}

class Monitor_Profiler_Test(unittest.TestCase):

   def test_1_vm_count(self):
      logger.info("Running Number of VM test cases")
      vm_names = get_vms_cluster(VCENTER_IP, VCENTER_USERNAME,VCENTER_PASSWORD,cluster_moid)
      if "PrimaryIO-OnPrem-Manager-0" in vm_names:
         vm_names.remove("PrimaryIO-OnPrem-Manager-0")
      expected_count = len(vm_names)
      logger.info("Total vm present on the Onprem Vcenter : %s"%expected_count)
      response = requests.get("%s%s" %(URL, url), headers=headers, verify=False)
      assert response.status_code == 200 , "Response code is not 200" 
      profile_page_response = json.loads(response.text)
      vm_list = profile_page_response["data"]["vm_list"]
      actual_count = len(vm_list)
      logger.info("Total vm present on the On cloud burst page : %s"%actual_count)
      assert expected_count == (actual_count) , "Vm count on vcenter and appliance is not matching"

   def test_2_primaryio_component(self):
      logger.info("Runningtest cases for checking primaryIO compenents are not listed in VM lists")
      response = requests.get("%s%s" %(URL, url), headers=headers, verify=False)
      assert response.status_code == 200 , "Response code is not 200"
      profile_page_response = json.loads(response.text)
      total_resources = profile_page_response["data"]["vm_list"]
      vm_names=[]
      for key in total_resources.keys():
         vm_names.append(total_resources[key]["name"])
      vm_names.sort()
      logger.info("Total vm present on the profiling page : %s"%vm_names)
      assert "PrimaryIO-OnPrem-Manager-0" not in vm_names , "PrimaryIO-OnPrem-Manager-0 is listed on profiling page"


   
   def test_3_vm_count(self):
      logger.info("Running Number of VM test cases")
      expected_names = get_vms_cluster(VCENTER_IP, VCENTER_USERNAME,VCENTER_PASSWORD,cluster_moid)
      if "PrimaryIO-OnPrem-Manager-0" in expected_names:
         expected_names.remove("PrimaryIO-OnPrem-Manager-0")
      expected_names.sort()
      logger.info("Total vm present on the Onprem Vcenter : %s"%expected_names)
      print("Total vm present on the Onprem Vcenter : %s"%expected_names)
      response = requests.get("%s%s" %(URL, url), headers=headers, verify=False)
      assert response.status_code == 200 , "Response code is not 200"
      profile_page_response = json.loads(response.text)
      total_resources = profile_page_response["data"]["vm_list"]
      vm_names=[]
      for key in total_resources.keys():
         vm_names.append(total_resources[key]["name"])
      vm_names.sort()
      logger.info("Total vm present on the profiling page : %s"%vm_names)
      assert expected_names==vm_names , "Vm names on vcenter and appliance is not matching"


   def test_4_rename_cluster(self):
      logger.info("Running test cases: verify correct names are getting displayed on renaming of cluster")
      expected_names = get_vms_cluster(VCENTER_IP, VCENTER_USERNAME,VCENTER_PASSWORD,cluster_moid)
      if "PrimaryIO-OnPrem-Manager-0" in expected_names:
           expected_names.remove("PrimaryIO-OnPrem-Manager-0")
      expected_names.sort()
      logger.info("Total vm present on the Onprem Vcenter : %s"%expected_names)
      print("Total vm present on the Onprem Vcenter : %s"%expected_names)
      rename_cluster_name = "test"
      #renaming cluster name
      rename_cluster(VCENTER_IP, VCENTER_USERNAME,VCENTER_PASSWORD,VCENTER_CLUSTER,rename_cluster_name)
      time.sleep(2)
      response = requests.get("%s%s" %(URL, url), headers=headers, verify=False)
      assert response.status_code == 200 , "Response code is not 200"
      profile_page_response = json.loads(response.text)
      total_resources = profile_page_response["data"]["vm_list"]
      vm_names=[]
      for key in total_resources.keys():
         vm_names.append(total_resources[key]["name"])
      vm_names.sort()
      logger.info("Total vm present on the profiling page i post renaming: %s"%vm_names)
      rename_cluster(VCENTER_IP, VCENTER_USERNAME,VCENTER_PASSWORD,rename_cluster_name,VCENTER_CLUSTER)
      assert expected_names==vm_names , "VM nams are matching post renaming"

   def test_5_rename_vm(self):
      logger.info("Verify correct VM names are getting reflected on renamin a VM")
      expected_names = get_vms_cluster(VCENTER_IP, VCENTER_USERNAME,VCENTER_PASSWORD,cluster_moid)
      if "PrimaryIO-OnPrem-Manager-0" in expected_names:
           expected_names.remove("PrimaryIO-OnPrem-Manager-0")
      expected_names.sort()
      old_name  = expected_names[1]
      new_name = old_name+"dummy"
      rename_vm(VCENTER_IP, VCENTER_USERNAME,VCENTER_PASSWORD,VCENTER_CLUSTER,old_name,new_name)
      logger.info("Total vm present on the Onprem Vcenter : %s"%expected_names)
      print("Total vm present on the Onprem Vcenter : %s"%expected_names)
      #renaming cluster name
      time.sleep(2)
      response = requests.get("%s%s" %(URL, url), headers=headers, verify=False)
      assert response.status_code == 200 , "Response code is not 200"
      profile_page_response = json.loads(response.text)
      total_resources = profile_page_response["data"]["vm_list"]
      vm_names=[]
      for key in total_resources.keys():
         vm_names.append(total_resources[key]["name"])
      vm_names.sort()
      logger.info("Total vm present on the profiling page i post renaming: %s"%vm_names)
      rename_vm(VCENTER_IP, VCENTER_USERNAME,VCENTER_PASSWORD,VCENTER_CLUSTER,new_name,old_name)

      assert new_name in vm_names, "Rename VM is not listed in the appliance VM list"
