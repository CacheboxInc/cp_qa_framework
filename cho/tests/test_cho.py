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

from cho.conf_tcs.config import *
from global_utils.vmware_utils.vm_utils_rest import *
from global_utils.vmware_utils.vm_details import get_ip
from global_utils.cmd_runner_para import run_cmd
from global_conf.config import logger


requests.packages.urllib3.disable_warnings()

URL        = "https://%s:443"
MIGRATE_URL = "/automigrate"
MIGRATE_BACK_URL = "/automigrateback"
URL      = URL % (APPLIANCE_IP)
headers = {'Content-type': 'application/json'}

ITERATION_COUNT=50


class Migrate_CHO_Test(unittest.TestCase):
        
    data = {}
    data["vcenter_ip"]   = "hyc-cp3.primaryio.lan"
    data["vm_names"]     = [VM_NAME]


    data_migrate_back = {}
    data_migrate_back["vcenter_ip"]   = "hyc-cp3.primaryio.lan"
    data_migrate_back["flush_flag"]   = FLUSH_FLAG
    data_migrate_back["poweron_flag"] = POWERON_FLAG
    data_migrate_back["vm_names"]     = [VM_NAME]

 
    def test_1(self):
       
        logger.info("Running the CHO test cases")
        for x in range(1,ITERATION_COUNT):
            logger.info("********************Running "+str(x)+" iteration************************")
            print("********************Running "+str(x)+" iteration************************")
            #Power on vm
            do_power_on(VM_NAME,VCENTER_IP)
			#Perform fio in a file
            vm_ip = get_ip(VCENTER_IP,VCENTER_USERNAME,VCENTER_PASSWORD,VM_NAME,VCENTER_CLUSTER)
            print("VM IP on prem: %s"%vm_ip)
            result = run_cmd(vm_ip,"root","root123",FIO_CMD)         
            logger.info("FIO OUTPUT ** /n %s"%result)
            time.sleep(30)
			#take checksum of file
            checksum = run_cmd(vm_ip,"root","root123",CKSUM_CMD)
            logger.info("On prem file checksum : %s"%checksum)
            print("On prem file checksum : %s"%checksum)
            #Power off VM  
            do_power_off(VM_NAME,VCENTER_IP)
            logger.info("Migrating VM to cloud")
            #Migrate VM to cloud
            print("Migrating VM to cloud")
            response = requests.post("%s%s" %(URL, MIGRATE_URL), json=self.data, headers=headers, verify=False)
            print("URL = %s%s" %(URL, MIGRATE_URL))
            assert(response.status_code == 200 , "Cloud migration failed")
            logger.info("Status Code : %s" %response.status_code)
            print("Status Code : %s" %response.status_code)

            if response.status_code == 200:
                time.sleep(150)
                assert(vm_present_on_vcenter(CLOUD_IP, VM_NAME), "%s not found on the cloud"%VM_NAME )

                #Power ON VM
                do_power_on(VM_NAME,CLOUD_IP)

                #Check the checksum of file
                print("Find checksum of file on cloud")
                vm_ip_cloud = get_ip(CLOUD_IP,CLOUD_USERNAME,CLOUD_PASSWORD,VM_NAME,CLOUD_CLUSTER_NAME) 	
                new_checksum = run_cmd(vm_ip_cloud,USERNAME,PASSWORD,CKSUM_CMD)
                print("Checksum on cloud = %s"%new_checksum)
                logger.info("Checksum on cloud : %s"%new_checksum)
                assert checksum == new_checksum , "Checksum is not matching"
                print("Migrating VM back to on prem")
                logger.info("Mirating back VM")
                do_power_off(VM_NAME,CLOUD_IP)
                response = requests.post("%s%s" %(URL, MIGRATE_BACK_URL), json=self.data_migrate_back, headers=headers, verify=False)
                assert(response.status_code == 200 , "Migrate back failed")
                logger.info("Status Code of migrate back: %s" %response.status_code)
                print("Status response code of migrate back: %s"%response.status_code)
                if response.status_code == 200:
                    time.sleep(180)
                    assert(vm_present_on_vcenter(CLOUD_IP, VM_NAME)==False , "VM is not migrated back to ON prem")
                else:
                    print("Migrate back Failed : ")
                    break

            else: 
                print("Migration failed")
                logger.info("Migration failed")
                break
