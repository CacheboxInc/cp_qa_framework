

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
from sanity_suite.lib_tcs.utils import *
from global_utils.vmware_utils.vm_utils_rest import *

requests.packages.urllib3.disable_warnings()

URL= "https://%s:443"
url = "/recommendation?is_costing=True&vcenter_ip=%s"%(VCENTER_IP)

URL      = URL % (APPLIANCE_IP)
headers = {'Content-type': 'application/json'}



test_1_vm_count():
   logger.info("Running Number of VM test cases")
   expected_count = total_vm_present_on_vcenter(VCENTER_IP)
   logger.info("Total vm present on the Onprem Vcenter : %s"%expected_count)
   response = requests.get("%s%s" %(URL, url), headers=headers, verify=False)
   assert response.status_code == 200 , "Response code is not 200" 
   profile_page_response = json.loads(response.text)
   vm_list = profile_page_response["data"]["vmc"]["resource_assesment"]
   actual_count = len(vm_list)
   assert expected_count == (actual_count+1) , "Vm count on vcenter and appliance is not matching"

   
test_2_vm_count():
   logger.info("Running Number of VM test cases")
   expected_names = vm_names_onvcenter(VCENTER_IP)
   expected_names = excepted_names.remove("PrimaryIO-OnPrem-Manager-0")
   logger.info("Total vm present on the Onprem Vcenter : %s"%expected_count)
   response = requests.get("%s%s" %(URL, url), headers=headers, verify=False)
   assert response.status_code == 200 , "Response code is not 200"
   profile_page_response = json.loads(response.text)
   vm_names = profile_page_response["data"]["vmc"]["resource_assesment"][name]
   assert excpected_names == (actual_count+1) , "Vm count on vcenter and appliance is not matching"



