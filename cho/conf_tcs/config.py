from global_conf.config import *

##For Test set up
REPORT_DIR = "/cho/logs_tcs/"
TC_DIR = "/cho/tests/"
XML_REPORT_DIR = "/cho/logs_tcs/"

REPORT_LOCATION_SERVER = "drugesh@192.168.3.96:"
#Main SetUP
APPLIANCE_IP = "10.10.96.1"
APP_USERNAME = "administrator@pio.com"
APP_PASSWORD = "admin@123"

# On-prem details

#VCENTER_IP = "hyc-cp3.primaryio.lan"
VCENTER_IP = "10.10.8.58"
VCENTER_USERNAME = "administrator@vsphere.local"
VCENTER_PASSWORD = "Root@123"
VCENTER_CLUSTER = "Cluster"

#VM Details
VM_NAME = ["test_VM11"]
USERNAME = "root"
PASSWORD = "root123"
POWERON_FLAG = "FALSE"
FLUSH_FLAG = "TRUE"


##Cloud details
CLOUD_IP = "10.10.8.41"
CLOUD_USERNAME = "administrator@vsphere.local"
CLOUD_PASSWORD  = "Root@123"
CLOUD_CLUSTER_NAME = "Cluster_OC"
EMAIL_IDS = ['drugesh.jaiswal@primaryio.com']

#Commands
FIO_CMD =  "fio --name=/data/test --ioengine=libaio --iodepth=4 --rw=randwrite --bs=32k --direct=0 --size=500m --numjobs=1"
CKSUM_CMD = "cksum /data/test.0.0"



