import requests
import json
from global_conf.config import logger
#import logging as logger
import time
#sys.path.append(os.getcwd())
import random
import threading
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
 
s=requests.Session()
s.verify=False
#vcip = "10.10.8.58" 
 
# Function to get the vCenter server session
def get_vc_session(vcip,username,password):
         s.post('https://'+vcip+'/rest/com/vmware/cis/session',auth=(username,password))
         return s
 
# Function to get all the VMs from vCenter inventory
def get_vms(vcip):
        vms=s.get('https://'+vcip+'/rest/vcenter/vm/')
        return vms

def get_vms(vcip,cluster):
        vms=s.get('https://'+vcip+'/rest/vcenter/vm?filter.clusters='+cluster)
        return vms
 
#Function to power on particular VM
def poweron_vm(vmmoid,vcip):
        s.post('https://'+vcip+'/rest/vcenter/vm/'+vmmoid+'/power/start')
 
# Function to power off particular VM
def poweroff_vm(vmmoid,vcip):
        s.post('https://'+vcip+'/rest/vcenter/vm/'+vmmoid+'/power/stop')


#Function to return MRC data
def get_mrc_stats(url):
	data= requests.get(url, verify = False)
	return data

def get_vm_state(vmmoid , vcip):
	url = 'https://'+vcip+'/rest/vcenter/vm/'+vmmoid+'/power'
	data = s.get(url)
	print(url)
	return data

def do_power_off(vmname, vcip):
	get_vc_session(vcip,"Administrator@vsphere.local","Root@123")
	vms = get_vms(vcip)
	vm_response=json.loads(vms.text)
	json_data=vm_response["value"]
 
	#print( "VM names and its unique MOID")
	#print( "============================")
	for vm in json_data:
		#print(vm.get("name")+" :: "+vm.get("vm"))
		if(vm.get("name")==vmname):
			print("Checking state of "+vm.get("name"))
			if vm.get("power_state") == "POWERED_ON":
				logger.info("Power Off the VM "+vmname)
				print("Power off VM : %s"%vmname)
				poweroff_vm(vm.get("vm"),vcip)
				time.sleep(45)               
				#print(get_ip_address(vm.get("name"),vcip))

def do_power_on(vmname, vcip):
        get_vc_session(vcip,"Administrator@vsphere.local","Root@123")
        vms = get_vms(vcip)
        vm_response=json.loads(vms.text)
        json_data=vm_response["value"]

        #print( "VM names and its unique MOID")
        #print( "============================")
        for vm in json_data:
                #print(vm.get("name")+" :: "+vm.get("vm"))
                if(vm.get("name")==vmname):
                        print("Checking state of "+vm.get("name"))
                        if vm.get("power_state") == "POWERED_OFF":
                                logger.info("Power On the VM "+vmname)
                                print("Power On : %s"%vmname)
                                poweron_vm(vm.get("vm"),vcip)
                                time.sleep(60)




def get_ip_address(vmmoid , vcip):
	url = 'https://'+vcip+'/rest/vcenter/vm/'+vmmoid+'/guest/identity'
	print(url)
	data = s.get(url)
	return data


def get_vms_vcenter(vcip):
	#Get vCenter server session and can be used as needed. pass vcenter username & password
	vcsession = get_vc_session(vcip,"Administrator@vsphere.local","Root@123")
	#print(vcsession)
	li = []
	#Get all the VMs from inventory using below method from "vcrest" module.
	vms = get_vms(vcip)
	response=json.loads(vms.text)
	#print (response["value"])
	value = response["value"]
	for i in range(0, len(value)):
		li.append(value[i]["name"])
		#print("Printing the vm guest name")
		#print( value[i])
	#logger.info("VMs found the vCenter : %s" %vcip)
	#logger.info(li)
	return li
	
def get_vms_cluster(vcip,user,password,cluster):
    #Get vCenter server session and can be used as needed. pass vcenter username & password
    vcsession = get_vc_session(vcip,user,password)
    #print(vcsession)
    li = []
    #Get all the VMs from inventory using below method from "vcrest" module.
    vms = get_vms(vcip,cluster)
    response=json.loads(vms.text)
    print (response["value"])
    value = response["value"]
    for i in range(0, len(value)):
        li.append(value[i]["name"])
        print("Printing the vm guest name")
        print( value[i])
    return li


def vm_present_on_vcenter(vcip , vm_name):
	vms = get_vms_vcenter(vcip)
	#print(vms)
	if vm_name in vms:
		return True
	else:
		return False



def vm_operation_bulk(vm_name,vcip, operation):

	for vm in vm_name:
		if(operation =="power_on"):
			#t = threading.Thread(target = test_1, kwargs = {'cnt' : i})
			thread = threading.Thread(target = do_power_on, kwargs = {'vmname' : vm,'vcip':vcip})
			thread.start()
		elif(operation == "power_off"):
			thread = threading.Thread(target = do_power_off, kwargs = {'vmname' : vm,'vcip':vcip})
			thread.start()

	


#print(get_vms_cluster("10.10.8.58","administrator@vsphere.local","Root@123","domain-c7"))
#print(vm_present_on_vcenter("192.168.1.40" , "U3"))
#get_vc_session()
#vm_operation_bulk(["test_vm12","test_vm13"],"10.10.8.58", "power_off")
