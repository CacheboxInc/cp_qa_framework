from global_conf.config import *



##For Test set up
REPORT_DIR = "/sanity_suite/logs_tcs/"
#TC_DIR = "/sanity_suite/tests/test_add_delete_vcenter.py"
TC_DIR = "/sanity_suite/tests/"
XML_REPORT_DIR = "/sanity_suite/logs_tcs/"
# Number of worker for parallel execution
REPORT_LOCATION_SERVER = "drugesh@192.168.3.96:"
#Nodes for parallel execution
NODES = 1

APPLIANCE_IP = "192.168.0.0"
APP_USERNAME = "administrator@pio.com"
APP_PASSWORD = "admin@123"

#Setup details for checking add and install
SANITY_VCENTER_IP = "10.10.27.26"

#VCENTER_IP = "192.168.1.25"
#VCENTER_USERNAME = "administrator@vsphere.local"
#VCENTER_PASSWORD = "Root@123"
#VCENTER_CLUSTER = "Cluster"
#VC_TYPE = 0

# On-prem details

VCENTER_IP = "192.168.0.0"
#VCENTER_IP = "hyc-cp3.primaryio.lan"
VCENTER_USERNAME = "administrator@vsphere.local"
VCENTER_PASSWORD = "Naruto@123"
VCENTER_CLUSTER = "Cluster"
VCENTER_DATASTORE = "ssd"
VCENTER_NETWORK = "VM Network"
VCENTER_RESOURCEPOOL = "HYC_RP"
VC_TYPE = 8

CLUSTER_ID = None
CLUSTER_NAME = None
VM_NAME = "U3"
POWERON_FLAG = "TRUE"
FLUSH_FLAG = "TRUE"


# used to test deployement
#DATACENTER = "192.168.1.25"
#DATACENTER_USERNAME = "administrator@vsphere.local"
#DATACENTER_TYPE = "VCENTER"
#DATACENTER_DATASTORE = "QNAP_NFS"
#DATACENTER_CLUSTER_NAME = "Dev_Cluster_6.5_Esxi"
#DATACENTER_RESOURCE_POOL = "vApp_Skapoor"

##Cloud details
CLOUD_IP = "192.168.0.0"
CLOUD_USER_NAME = "administrator@vsphere.local"
CLOUD_PASSWORD  = "Naruto@123"
#CLOUD_APPLIANCE_IP = "10.10.27.164"

# URL version
VERSION = "v1.0"

HDM_LIBRARY_NAME = "HDM_CONTENT_LIBRARY"

DATACENTER = "vcenter.sddc-34-216-134-56.vmc.vmware.com"
DATACENTER_USERNAME = "cloudadmin@vmc.local"
DATACENTER_PASSWORD = "h$gzJh2*9a"
DATACENTER_TYPE = "VMC"
DATACENTER_DATASTORE = "WorkloadDatastore"
DATACENTER_CLUSTER_NAME = "Cluster-1"
DATACENTER_RESOURCE_POOL = "Compute-ResourcePool"
DATACENTER_NETWORK_NAME = "pio_network_1"

ON_PREM_OPSD_SERVICE = "VDDK"
ON_PREM_GATEWAY_SERVICE = "Prem_Msg_GW"

CLOUD_SERVICES = [("TFTP_Server", 1), ("iPXE_Server", 1), ("AS_Server", 1), \
                  ("Cloud_Msg_GW", 1), ("StorD", 1), ("TGT_Server", 1)]

# Name of VM for testing policy attach / detach tests
#VM_NAME = "unit-test"
VM_NAME_1 = "Ubuntu_Test_VM_1"
ATTACH_POLICY = "Passthrough"
CACHE_REPLICA = 0

HOST_IP_FORMAT = "0.0.0.0"
HOST_FORMAT = '{mtu=1500, SpeedMb=1000 MB, networklabel=Management Network, switchName=vSwitch0, addr=%s, ipdisplay=vmk0 (%s), is_configured=True}'
DATA_FORMAT = {'Data': '', 'name': ''}
TIME_SLEEP = 5

CLUSTER_NAMES = ["Cluster", "Cluster_1_1_1"]
EMAIL_IDS = ['drugesh.jaiswal@primaryio.com']

VMDKUUID = '6000C29e-35a7-c283-bf2e-11eba347bc8f'
DSUUID = '2f30268b-8b3fced0/test_vm'

