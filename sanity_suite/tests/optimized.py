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
import atexit
import json
import argparse
import random
import requests
import ssl
import traceback
from sanity_suite.conf_tcs.config import *
from sanity_suite.lib_tcs.utils import *

from pyVim import connect
from pyVmomi import vmodl
from pyVmomi import vim

from unit_suite.tests.pbm_utils import *
from unit_suite.tests.vim_utils import *

requests.packages.urllib3.disable_warnings()

URL          = "https://%s:443"
OPTIMIZED_URL = "/optimization?cluster_id=%s&cluster_name=%s&vcenter_ip=%s"

'''
Test for:
        1. Get optimized test

Sample test run:
python3.5 optimized_test.py --appliance-ip 192.168.3.76 --cluster-id 192168140_Cluster --cluster-name Cluster --vcenter-ip 192.168.1.40 --vcenter-username administrator@vsphere.local --vcenter-password Naruto@123



parser = argparse.ArgumentParser()
parser.add_argument('--appliance-ip', required=True, help='Appliance IP')
parser.add_argument('--cluster-id', required=True, help='Cluster Id')
parser.add_argument('--cluster-name', required=True, help='Cluster Name')
parser.add_argument('--vcenter-ip', required=True, help='vCenter IP')
parser.add_argument('--vcenter-username', required=True, help='vCenter Username')
parser.add_argument('--vcenter-password', required=True, help='vCenter Password')

args          = parser.parse_args()'''
URL           = URL % (APPLIANCE_IP)
OPTIMIZED_URL = OPTIMIZED_URL % (CLUSTER_ID, CLUSTER_NAME, VCENTER_IP)

class OptimizedTest(unittest.TestCase):
    url       = URL
    vcenter = VCenter(VCENTER_IP, VCENTER_USERNAME, VCENTER_PASSWORD)
    cluster = vcenter.get_obj([vim.ClusterComputeResource], CLUSTER_NAME)
    pbm     = PBMUtils(vcenter)

    #
    # Get the vsphere vm list from vCenter within cluster
    #
    def vms_obj_list_by_cluster(self):
        vm_obj_list = []
        try:
            hosts = self.cluster.host
            for host in hosts:
                vms = host.vm
                for vm in vms:
                    vm_obj_list.append(vm)

        except:
            traceback.print_exc()

        return vm_obj_list


    #
    # Get the vsphere vm list from vCenter within cluster
    #
    def vmdks_obj_list_by_cluster(self):
        vmdk_obj_dict = {}
        try:
            hosts = self.cluster.host
            for host in hosts:
                vms = host.vm
                for vm in vms:
                    vmdk_list = []
                    vmdk_obj_dict[vm.name] = {}
                    vm_obj = GuestVM(vm)
                    vmdks = vm_obj.get_vmdks()
                    for vmdk in vmdks:
                        vmdk_list.append(vmdk)
                    vmdk_obj_dict[vm.name] = vmdk_list

        except:
            traceback.print_exc()

        return vmdk_obj_dict


    #
    # Get the list of VM names from vm_obj_list
    #
    def get_vm_name_list(self, vm_obj_list):
        vm_name_list = []
        try:
            for vm in vm_obj_list:
                vm_name_list.append(vm.name)
        except:
            traceback.print_exc()

        return vm_name_list


    #
    # Get the list of uuids from vm_obj_list
    #
    def get_vm_uuid_list(self, vm_obj_list):
        vm_uuid_list = []
        try:
            for vm in vm_obj_list:
                vm_uuid_list.append(vm.summary.config.uuid.replace("-", ""))
        except:
            traceback.print_exc()

        return vm_uuid_list


    #
    # Get the vsphere vmdk list from vCenter within VM
    #
    def get_vmdks_size_by_vm(self, vm_obj_list):
        vmdk_size_dict = {}
        try:
            for vm in vm_obj_list:
                vmdk_size_dict[vm.name] = {}
                vmdk_size = 0
                for device in vm.config.hardware.device:
                    if type(device).__name__ == 'vim.vm.device.VirtualDisk':
                        vmdk_size += int(device.deviceInfo.summary.strip("KB").strip().replace(",", "")) << 10
                vmdk_size_dict[vm.name] = vmdk_size
        except:
            traceback.print_exc()

        return vmdk_size_dict


    #
    # Get the list of uuids from vmdk_obj_list
    #
    def get_vmdk_name(self, vm_obj_list):
        vmdk_name_dict = {}
        try:
            for vm in vm_obj_list:
                vmdk_name_dict[vm.name] = {}
                for device in vm.config.hardware.device:
                    if type(device).__name__ == 'vim.vm.device.VirtualDisk':
                        vmdk_name_dict[vm.name][device.backing.uuid.replace("-", "").lower()] = \
                            device.deviceInfo.label
        except:
            traceback.print_exc()

        return vmdk_name_dict

    #
    # Get the list of uuids from vmdk_obj_list
    #
    def get_vmdk_uuid(self, vm_obj_list):
        vmdk_uuid_dict = {}
        try:
            for vm in vm_obj_list:
                vmdk_uuid_dict[vm.name] = {}
                vmdk_uuid_tmp = []
                for device in vm.config.hardware.device:
                    if type(device).__name__ == 'vim.vm.device.VirtualDisk':
                        vmdk_uuid_tmp.append(device.backing.uuid.replace("-", "").lower())
                vmdk_uuid_dict[vm.name] = vmdk_uuid_tmp
        except:
            traceback.print_exc()

        return vmdk_uuid_dict


    #
    # Tests the return code of the response
    #
    def test_1_return_code(self, url=OPTIMIZED_URL, test_name="test1", negative=False):
        print("\n\nTest Name : ", test_name)
        response = requests.get("%s%s" %(URL, url), verify=False)
        if negative is True:
            assert(response.status_code != 200)
        else:
            assert(response.status_code == 200)

        print("Status Code : ", response.status_code)
        print("%s Finished" % test_name)


    #
    # Compares the VM names from the response
    #
    def test_2_vm_name(self, url=OPTIMIZED_URL, test_name="test2"):
        print("\n\nTest Name : ", test_name)
        response = requests.get("%s%s" %(URL, url), verify=False)
        vmware_vm_obj_list  = self.vms_obj_list_by_cluster()
        vmware_vmdk_obj_dict = self.vmdks_obj_list_by_cluster()

        spbm_disks    = {}

        optimized_vms = []
        for vm in vmware_vm_obj_list:
            policies            = self.pbm.get_vm_vmdk_storage_policies(vm)
            spbm_disks[vm.name] = dict(policies)

            vmdk_obj = vmware_vmdk_obj_dict[vm.name]

            for vmdk in vmdk_obj:
                if vmdk.key in list(spbm_disks[vm.name].keys()):
                    p_id   = spbm_disks[vm.name].get(vmdk.key)
                    policy = self.pbm.get_policy_value(p_id)
                    if policy.lower() == "passthrough":
                        continue
                    if vm.name not in optimized_vms:
                        optimized_vms.append(vm.name)

        resp = response.json()
        pio_vm_name_list = []
        for vm in resp['data']['vm_list']:
            pio_vm_name_list.append(resp['data']['vm_list'][vm]['name'])

        for vm_name in optimized_vms:
            if vm_name in pio_vm_name_list:
                continue
            else:
                print("%s Failed" % test_name)
                break

        print("%s Finished" % test_name)


    #
    # Compares the VM names from the response from uuid
    #
    def test_3_vm_name_from_uuid(self, url=OPTIMIZED_URL, test_name="test3"):
        print("\n\nTest Name : ", test_name)
        response = requests.get("%s%s" %(URL, url), verify=False)
        vmware_vm_obj_list  = self.vms_obj_list_by_cluster()
        vmware_vmdk_obj_dict = self.vmdks_obj_list_by_cluster()

        spbm_disks    = {}

        optimized_vms = []
        for vm in vmware_vm_obj_list:
            policies            = self.pbm.get_vm_vmdk_storage_policies(vm)
            spbm_disks[vm.name] = dict(policies)

            vmdk_obj = vmware_vmdk_obj_dict[vm.name]

            for vmdk in vmdk_obj:
                if vmdk.key in list(spbm_disks[vm.name].keys()):
                    p_id   = spbm_disks[vm.name].get(vmdk.key)
                    policy = self.pbm.get_policy_value(p_id)
                    if policy.lower() == "passthrough":
                        continue
                    if vm.name not in optimized_vms:
                        optimized_vms.append(vm.name)

        resp = response.json()
        pio_vm_name_list = []
        for vm in resp['data']['vm_list']:
            vm_split = vm.split("_")[2:]
            vm_name  = "_".join(vm_split)

            pio_vm_name_list.append(vm_name)

        for vm_name in optimized_vms:
            if vm_name in pio_vm_name_list:
                continue
            else:
                print("%s Failed" % test_name)
                break

        print("%s Finished" % test_name)


    #
    # Compares the VM uuid from the response
    #
    def test_4_vm_uuid(self, url=OPTIMIZED_URL, test_name="test4"):
        print("\n\nTest Name : ", test_name)
        response = requests.get("%s%s" %(URL, url), verify=False)
        vmware_vm_obj_list  = self.vms_obj_list_by_cluster()
        vmware_vmdk_obj_dict = self.vmdks_obj_list_by_cluster()
        vmware_vm_uuid_list = self.get_vm_uuid_list(vmware_vm_obj_list)

        spbm_disks    = {}

        optimized_vm_uuids = []
        for vm in vmware_vm_obj_list:
            policies            = self.pbm.get_vm_vmdk_storage_policies(vm)
            spbm_disks[vm.name] = dict(policies)

            vmdk_obj = vmware_vmdk_obj_dict[vm.name]

            for vmdk in vmdk_obj:
                if vmdk.key in list(spbm_disks[vm.name].keys()):
                    p_id   = spbm_disks[vm.name].get(vmdk.key)
                    policy = self.pbm.get_policy_value(p_id)
                    if policy.lower() == "passthrough":
                        continue
                    if vm.config.uuid.replace("-", "") not in optimized_vm_uuids:
                        optimized_vm_uuids.append(vm.config.uuid.replace("-", ""))

        resp = response.json()
        pio_vm_uuid_list = []
        for vm in resp['data']['vm_list']:
            pio_vm_uuid_list.append("".join(vm.split("_")[1:2]))

        for vm_uuid in optimized_vm_uuids:
            if vm_uuid in pio_vm_uuid_list:
                continue
            else:
                print("%s Failed" % test_name)
                break

        print("%s Finished" % test_name)


    #
    # Compares the VMDK uuid from the response
    #
    def test_5_vmdk_uuid(self, url=OPTIMIZED_URL, test_name="test5"):
        print("\n\nTest Name : ", test_name)
        failed = False
        response = requests.get("%s%s" %(URL, url), verify=False)
        vmware_vm_obj_list  = self.vms_obj_list_by_cluster()
        vmware_vmdk_obj_dict = self.vmdks_obj_list_by_cluster()
        vmware_vm_uuid_list = self.get_vm_uuid_list(vmware_vm_obj_list)

        spbm_disks    = {}

        optimized_vmdk_uuids = []
        for vm in vmware_vm_obj_list:
            policies            = self.pbm.get_vm_vmdk_storage_policies(vm)
            spbm_disks[vm.name] = dict(policies)

            vmdk_obj = vmware_vmdk_obj_dict[vm.name]

            for vmdk in vmdk_obj:
                if vmdk.key in list(spbm_disks[vm.name].keys()):
                    p_id   = spbm_disks[vm.name].get(vmdk.key)
                    policy = self.pbm.get_policy_value(p_id)
                    if policy.lower() == "passthrough":
                        continue
                    optimized_vmdk_uuids.append(vmdk.backing.uuid.replace("-", "").lower())

        resp = response.json()
        for vm in resp['data']['vm_list']:
            for vmdk in resp['data']['vm_list'][vm]["health_details"]:
                if "".join(vmdk['id'].split("_")[1:2]) in optimized_vmdk_uuids:
                    continue
                else:
                    failed = True
                    print("%s Failed" % test_name)
                    break
            if failed:
                break

        print("%s Finished" % test_name)


    #
    # Compares the VMDK name/label from the response
    #
    def test_6_vmdk_name(self, url=OPTIMIZED_URL, test_name="test6"):
        print("\n\nTest Name : ", test_name)
        failed = False
        response = requests.get("%s%s" %(URL, url), verify=False)
        vmware_vm_obj_list  = self.vms_obj_list_by_cluster()
        vmware_vmdk_obj_dict = self.vmdks_obj_list_by_cluster()
        vmware_vm_uuid_list = self.get_vm_uuid_list(vmware_vm_obj_list)

        spbm_disks    = {}

        optimized_vmdks_names = {}
        for vm in vmware_vm_obj_list:
            policies            = self.pbm.get_vm_vmdk_storage_policies(vm)
            spbm_disks[vm.name] = dict(policies)

            vmdk_obj = vmware_vmdk_obj_dict[vm.name]

            for vmdk in vmdk_obj:
                if vmdk.key in list(spbm_disks[vm.name].keys()):
                    p_id   = spbm_disks[vm.name].get(vmdk.key)
                    policy = self.pbm.get_policy_value(p_id)
                    if policy.lower() == "passthrough":
                        continue
                    if vm.name in list(optimized_vmdks_names.keys()):
                        optimized_vmdks_names[vm.name][vmdk.deviceInfo.label] = policy
                    else:
                        optimized_vmdks_names[vm.name] = {}
                        optimized_vmdks_names[vm.name][vmdk.deviceInfo.label] = policy

        resp = response.json()
        for vm in resp['data']['vm_list']:
            for vmdk in resp['data']['vm_list'][vm]['health_details']:
                if vmdk['name'] in list(optimized_vmdks_names[resp['data']['vm_list'][vm]['name']].keys()):
                    continue
                else:
                    failed = True
                    print("%s Failed" % test_name)
                    break
            if failed:
                break

        print("%s Finished" % test_name)


    #
    # Compares the VMDK name/label from the response's policy_details
    #
    def test_7_vmdk_name_policy_details(self, url=OPTIMIZED_URL, test_name="test7"):
        print("\n\nTest Name : ", test_name)
        failed = False
        response = requests.get("%s%s" %(URL, url), verify=False)
        vmware_vm_obj_list  = self.vms_obj_list_by_cluster()
        vmware_vmdk_obj_dict = self.vmdks_obj_list_by_cluster()
        vmware_vm_uuid_list = self.get_vm_uuid_list(vmware_vm_obj_list)

        spbm_disks    = {}

        optimized_vmdks_names = {}
        for vm in vmware_vm_obj_list:
            policies            = self.pbm.get_vm_vmdk_storage_policies(vm)
            spbm_disks[vm.name] = dict(policies)

            vmdk_obj = vmware_vmdk_obj_dict[vm.name]

            for vmdk in vmdk_obj:
                if vmdk.key in list(spbm_disks[vm.name].keys()):
                    p_id   = spbm_disks[vm.name].get(vmdk.key)
                    policy = self.pbm.get_policy_value(p_id)
                    if policy.lower() == "passthrough":
                        continue
                    if vm.name in list(optimized_vmdks_names.keys()):
                        optimized_vmdks_names[vm.name][vmdk.deviceInfo.label] = policy
                    else:
                        optimized_vmdks_names[vm.name] = {}
                        optimized_vmdks_names[vm.name][vmdk.deviceInfo.label] = policy

        resp = response.json()

        for vm in resp['data']['vm_list']:
            for vmdk_policy in resp['data']['vm_list'][vm]['policy_details']:
                if vmdk_policy['name'] in list(optimized_vmdks_names[resp['data']['vm_list'][vm]['name']].keys()):
                    continue
                else:
                    failed = True
                    print("%s Failed" % test_name)
                    break
            if failed:
                break

        print("%s Finished" % test_name)


    #
    # Compares the VMDK policy from the response
    #
    def test_8_vmdk_policy(self, url=OPTIMIZED_URL, test_name="test8"):
        print("\n\nTest Name : ", test_name)
        failed = False
        response = requests.get("%s%s" %(URL, url), verify=False)
        vmware_vm_obj_list  = self.vms_obj_list_by_cluster()
        vmware_vmdk_obj_dict = self.vmdks_obj_list_by_cluster()
        vmware_vm_uuid_list = self.get_vm_uuid_list(vmware_vm_obj_list)

        spbm_disks    = {}

        optimized_vmdks_names = {}
        for vm in vmware_vm_obj_list:
            policies            = self.pbm.get_vm_vmdk_storage_policies(vm)
            spbm_disks[vm.name] = dict(policies)

            vmdk_obj = vmware_vmdk_obj_dict[vm.name]

            for vmdk in vmdk_obj:
                if vmdk.key in list(spbm_disks[vm.name].keys()):
                    p_id   = spbm_disks[vm.name].get(vmdk.key)
                    policy = self.pbm.get_policy_value(p_id)
                    if policy.lower() == "passthrough":
                        continue
                    if vm.name in list(optimized_vmdks_names.keys()):
                        optimized_vmdks_names[vm.name][vmdk.deviceInfo.label] = policy
                    else:
                        optimized_vmdks_names[vm.name] = {}
                        optimized_vmdks_names[vm.name][vmdk.deviceInfo.label] = policy
                        
        resp = response.json()

        for vm in resp['data']['vm_list']:
            return_code
            for vmdk in resp['data']['vm_list'][vm]['health_details']:
                if vmdk['policy'] == optimized_vmdks_names[resp['data']['vm_list'][vm]['name']][vmdk['name']].lower():
                    continue
                else:
                    failed = True
                    print("%s Failed" % test_name)
                    break
            if failed:
                break

        print("%s Finished" % test_name)


    #
    # Compares the VMDK policy from the response's policy_details
    #
    def test_9_vmdk_policy_details(self, url=OPTIMIZED_URL, test_name="test9"):
        print("\n\nTest Name : ", test_name)
        failed = False
        response = requests.get("%s%s" %(URL, url), verify=False)
        vmware_vm_obj_list  = self.vms_obj_list_by_cluster()
        vmware_vmdk_obj_dict = self.vmdks_obj_list_by_cluster()
        vmware_vm_uuid_list = self.get_vm_uuid_list(vmware_vm_obj_list)

        spbm_disks    = {}

        optimized_vmdks_names = {}
        for vm in vmware_vm_obj_list:
            policies            = self.pbm.get_vm_vmdk_storage_policies(vm)
            spbm_disks[vm.name] = dict(policies)

            vmdk_obj = vmware_vmdk_obj_dict[vm.name]

            for vmdk in vmdk_obj:
                if vmdk.key in list(spbm_disks[vm.name].keys()):
                    p_id   = spbm_disks[vm.name].get(vmdk.key)
                    policy = self.pbm.get_policy_value(p_id)
                    if policy.lower() == "passthrough":
                        continue
                    if vm.name in list(optimized_vmdks_names.keys()):
                        optimized_vmdks_names[vm.name][vmdk.deviceInfo.label] = policy
                    else:
                        optimized_vmdks_names[vm.name] = {}
                        optimized_vmdks_names[vm.name][vmdk.deviceInfo.label] = policy

        resp = response.json()

        for vm in resp['data']['vm_list']:
            for vmdk_policy in resp['data']['vm_list'][vm]['policy_details']:
                if vmdk_policy['policy'] in optimized_vmdks_names[resp['data']['vm_list'][vm]['name']][vmdk_policy['name']].lower():
                    continue
                else:
                    failed = True
                    print("%s Failed" % test_name)
                    break
            if failed:
                break

        print("%s Finished" % test_name)


if __name__ == "__main__":
    test_obj = OptimizedTest(URL, VCENTER_IP, VCENTER_USERNAME, VCENTER_PASSWORD, CLUSTER_NAME)
    test_obj.test_1(OPTIMIZED_URL, "Test_return_code")
    test_obj.test_2(OPTIMIZED_URL, "Test_vm_name")
    test_obj.test_3(OPTIMIZED_URL, "Test_vm_name_from_uuid")
    test_obj.test_4(OPTIMIZED_URL, "Test_vm_uuid")
    test_obj.test_5(OPTIMIZED_URL, "Test_vmdk_uuid")
    test_obj.test_6(OPTIMIZED_URL, "Test_vmdk_name")
    test_obj.test_7(OPTIMIZED_URL, "Test_vmdk_name_policy_details")
    test_obj.test_8(OPTIMIZED_URL, "Test_vmdk_policy")
    test_obj.test_9(OPTIMIZED_URL, "Test_vmdk_policy_details")
