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

#from sanity_suite.conf_tcs.config import *
#from sanity_suite.lib_tcs.utils import *
from global_utils.vmware_utils.vm_utils_rest import *
from global_utils.vmware_utils.vm_details import get_ip

requests.packages.urllib3.disable_warnings()

URL        = "https://%s:443"
DEMO_URL = "/automigrate"

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
    def test_1(self, url=DEMO_URL, negative=False):
        logger.info("Running the Migrate test cases")
        #Power on vm
        do_power_on(VM_NAME,VCENTER_IP)
        #Perform fio in a file
        vm_ip = get_ip(VCENTER_IP,USER_NAME,PASSWORD,VM_NAME,CLUSTER_NAME)
        result = do_ios(vm_ip,username="root",pwd="root123",FIO_CONF)         

        #take checksum of file
        checksum = find_checksum(vm_ip,username="root",pwd="root123",file_name="")
        #Power off VM  
        do_power_off(VM_NAME,VCENTER_IP)

        #Migrate VM to cloud
        response = requests.post("%s%s" %(URL, url), json=self.data, headers=headers, verify=False)
        assert(response.status_code == 200)
        logger.info("Status Code : %s" %response.status_code)
        if response.status_code == 200:
            time.sleep(100)
            assert(vm_present_on_vcenter(CLOUD_IP, VM_NAME), "%s not found on the cloud"%VM_NAME )

        #Power ON VM
        do_power_on(VM_NAME,VCENTER_IP)

        #Check the checksum of file
        vm_ip_cloud = get_ip(CLOUD_VCENTER_IP,USER_NAME,PASSWORD,VM_NAME,CLOUD_CLUSTER_NAME)
        new_checksum = find_checksum(vm_ip_cloud,username="root",pwd="root123",file_name="")
        assert checksum == new_checksum , "CHecksum is not matching"

    
