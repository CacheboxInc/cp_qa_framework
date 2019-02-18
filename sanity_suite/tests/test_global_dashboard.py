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
from global_utils.vmware_utils.vm_utils_rest import get_vms_cluster
from global_utils.vmware_utils.vm_details import get_cluster_moid , get_all_cluster
from global_utils.vmware_utils.renamer import *

requests.packages.urllib3.disable_warnings()


cluster_moid = get_cluster_moid(VCENTER_IP,VCENTER_USERNAME,VCENTER_PASSWORD,VCENTER_CLUSTER)
cloud_cluster_moid = get_cluster_moid(CLOUD_IP,CLOUD_USERNAME,CLOUD_PASSWORD,CLOUD_CLUSTER)

URL= "https://%s"
url = "/hdm/clusters?vcenter_ip=%s"%(VCENTER_IP)
cloud_url = "/hdm/vmc_clusters?vcenter_ip=%s"%(VCENTER_IP)

URL      = URL % (APPLIANCE_IP)
headers = {'Content-type': 'application/json'}

class Global_Dashboard_Test(unittest.TestCase):

   def test_1_vm_count(self):
      logger.info("Running Number of VM test cases")
      expected_count = len(get_vms_cluster(VCENTER_IP, VCENTER_USERNAME,VCENTER_PASSWORD,cluster_moid))
      logger.info("Total vm present on the Onprem Vcenter : %s"%expected_count)
      response = requests.get("%s%s" %(URL, url), headers=headers, verify=False)
      assert response.status_code == 200 , "Response code is not 200"
      res = json.loads(response.text)
      data = res["data"]
      actual_count=0
      for i in range(0,len(res)):
         if data[i]["name"]==VCENTER_CLUSTER:
            actual_count = data[i]["vms"] 
      logger.info("Total vm present on the On dashboard page page : %s"%(actual_count))
      assert expected_count == int(actual_count) , "Vm count on vcenter and appliance is not matching"

   def test_2_cluster_names(self):
      excpected_cluster_list = get_all_cluster(VCENTER_IP, VCENTER_USERNAME,VCENTER_PASSWORD)
      logger.info("Running test for checking cluster names")
      response = requests.get("%s%s" %(URL, url), headers=headers, verify=False)
      assert response.status_code == 200 , "Response code is not 200"
      res = json.loads(response.text)
      data = res["data"]
      actual_clusters=[]
      for i in range(0,len(res)):
         actual_clusters.append(data[i]["name"])      
      actual_clusters.sort()
      excpected_cluster_list.sort()
      logger.info("Total cluster present on the Dasboard page: %s"%actual_clusters)
      logger.info("Total cluster present in the vcenter: %s"%excpected_cluster_list)
      assert  excpected_cluster_list == actual_clusters, "cluster names are not matching with vCenter and Dashboard page"

   def test_3_cluster_post_renaming(self):
      logger.info("Running test to check cluster names post renaming")
      rename_cluster_name = "dummy123"
      #renaming cluster name
      rename_cluster(VCENTER_IP, VCENTER_USERNAME,VCENTER_PASSWORD,VCENTER_CLUSTER,rename_cluster_name)
      excpected_cluster_list = get_all_cluster(VCENTER_IP, VCENTER_USERNAME,VCENTER_PASSWORD)
      
      response = requests.get("%s%s" %(URL, url), headers=headers, verify=False)
      assert response.status_code == 200 , "Response code is not 200"
      res = json.loads(response.text)
      data = res["data"]
      actual_clusters=[]
      for i in range(0,len(res)):
         actual_clusters.append(data[i]["name"])
      actual_clusters.sort()
      excpected_cluster_list.sort()
      logger.info("Total cluster present on the Dasboard page: %s"%actual_clusters)
      logger.info("Total cluster present in the vcenter: %s"%excpected_cluster_list)
      #renaming back the cluster name
      rename_cluster(VCENTER_IP, VCENTER_USERNAME,VCENTER_PASSWORD,rename_cluster_name,VCENTER_CLUSTER)
      assert  rename_cluster_name in actual_clusters, "cluster names are not matching with vCenter and Dashboard page"

   def test_4_vm_count_cloud(self):
      logger.info("Running Number of VM test cases on cloud")
      expected_count = len(get_vms_cluster(CLOUD_IP, CLOUD_USERNAME,CLOUD_PASSWORD,cloud_cluster_moid))
      logger.info("Total vm present on the Onprem Vcenter : %s"%expected_count)
      response = requests.get("%s%s" %(URL, cloud_url), headers=headers, verify=False)
      assert response.status_code == 200 , "Response code is not 200"
      res = json.loads(response.text)
      data = res["data"]
      actual_count=0
      for i in range(0,len(res)-1):
         if data[i]["name"]==CLOUD_CLUSTER:
            actual_count = data[i]["vms"]
      logger.info("Total vm present on the On dashboard dashboard page : %s"%(actual_count))
      assert expected_count == int(actual_count) , "Vm count on vcenter and appliance is not matching"

   def test_5_cluster_names_cloud(self):
      excpected_cluster_list = get_all_cluster(CLOUD_IP, CLOUD_USERNAME,CLOUD_PASSWORD)
      logger.info("Running test for checking cluster names on cloud")
      response = requests.get("%s%s" %(URL, cloud_url), headers=headers, verify=False)
      assert response.status_code == 200 , "Response code is not 200"
      res = json.loads(response.text)
      data = res["data"]
      actual_clusters=[]
      for i in range(0,len(res)-1):
         actual_clusters.append(data[i]["name"])
      actual_clusters.sort()
      excpected_cluster_list.sort()
      logger.info("Total cluster present on the Dasboard page: %s"%actual_clusters)
      logger.info("Total cluster present in the cloud: %s"%excpected_cluster_list)
      assert  excpected_cluster_list == actual_clusters, "cluster names are not matching with vCenter and Dashboard page"

   def test_6_cluster_post_renaming_cloud(self):
      logger.info("Running test to check cluster names post renaming on cloud")
      rename_cluster_name = "dummy123"
      #renaming cluster name
      rename_cluster(CLOUD_IP, CLOUD_USERNAME,CLOUD_PASSWORD,CLOUD_CLUSTER,rename_cluster_name)
      excpected_cluster_list = get_all_cluster(CLOUD_IP, CLOUD_USERNAME,CLOUD_PASSWORD)

      response = requests.get("%s%s" %(URL, cloud_url), headers=headers, verify=False)
      assert response.status_code == 200 , "Response code is not 200"
      res = json.loads(response.text)
      data = res["data"]
      actual_clusters=[]
      for i in range(0,len(res)-1):
         actual_clusters.append(data[i]["name"])
      actual_clusters.sort()
      excpected_cluster_list.sort()
      logger.info("Total cluster present on the Dasboard page: %s"%actual_clusters)
      logger.info("Total cluster present in the cloud: %s"%excpected_cluster_list)
      #renaming back the cluster name
      rename_cluster(CLOUD_IP, CLOUD_USERNAME,CLOUD_PASSWORD,rename_cluster_name,CLOUD_CLUSTER)
      assert  rename_cluster_name in actual_clusters, "cluster names are not matching with Cloud and Dashboard page"

