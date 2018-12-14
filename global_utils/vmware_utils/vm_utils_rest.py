import requests
import json
from global_conf.config import *
sys.path.append(os.getcwd())
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
        vms=s.get('https://'+vcip+'/rest/vcenter/vm')
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


def get_vms_vcenter(vcip):
	#Get vCenter server session and can be used as needed. pass vcenter username & password
	vcsession = get_vc_session(vcip,"Administrator@vsphere.local","Naruto@123")
	print(vcsession)
	li = []
	#Get all the VMs from inventory using below method from "vcrest" module.
	vms = get_vms(vcip)
	response=json.loads(vms.text)
	#print (response["value"])
	value = response["value"]
	for i in range(0, len(value)):
		li.append(value[i]["name"])
	logger.info("VMs found the vCenter : %s" %vcip)
	logger.info(li)
	return li
	

def vm_present_on_vcenter(vcip , vm_name):
	vms = get_vms_vcenter(vcip)
	print(vms)
	if vm_name in vms:
		return True
	else:
		return False



#get_vms_vcenter(vcip)
#print(vm_present_on_vcenter("192.168.1.40" , "U3"))


