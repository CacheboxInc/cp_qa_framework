
from pyVmomi import vim
import urllib.request
import requests
from pyVim import connect
import subprocess
import ssl

def get_obj(content, vimtype, name = None):
   return [item for item in content.viewManager.CreateContainerView(content.rootFolder, [vimtype], recursive=True).view]

def connect_vcenter(host,user,pwd):
   # Disabling urllib3 ssl warnings
   requests.packages.urllib3.disable_warnings()

   # Disabling SSL certificate verification
   context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
   context.verify_mode = ssl.CERT_NONE

   context = None
   if hasattr(ssl, '_create_unverified_context'):
      context = ssl._create_unverified_context()

   SI = None
   #print("Connection establising")
   #SI = connect.SmartConnect(host = VCENTER_IP,user = VCENTER_USERNAME,pwd= VCENTER_PASSWORD,port=PORT,sslContext=context)
   SI = connect.SmartConnect(host=host,user=user,pwd=pwd,port=443,sslContext=context)


   content = SI.RetrieveContent()
   return content

def get_ip(host,user,pwd,vmname,cluster_name):
   content = connect_vcenter(host,user,pwd)
   cluster_name_found=False
   vm_name_found = False
   vm_ip= None
   #print("Connection established")
   for cluster_obj in get_obj(content, vim.ComputeResource):
      #print(cluster_obj.name)
      if cluster_obj.name == cluster_name:
         cluster_name_found = True
         for host in cluster_obj.host:
            #print(host.vm)
            for vm in host.vm:
                #print(vm.name)
                if vm.name == vmname:
                    vm_name_found = True
                    vm_ip = vm.summary.guest.ipAddress
   return vm_ip

def get_cluster_moid(host,user,pwd,cluster_name):

   content = connect_vcenter(host,user,pwd)
   cluster_name_found=False
   vm_name_found = False
   vm_ip= None
   #print("Connection established")
   for cluster_obj in get_obj(content, vim.ComputeResource):
      #print(cluster_obj.name)
      if cluster_obj.name == cluster_name:
         cluster_name_found = True
         #print(cluster_obj._GetMoId())
   return cluster_obj._GetMoId()


def get_all_cluster(host,user,pwd):
   content = connect_vcenter(host,user,pwd)
   cluster_list=[]
   for cluster_obj in get_obj(content, vim.ComputeResource):
      cluster_list.append(cluster_obj.name)
   
   return cluster_list



#print(get_all_cluster("10.10.8.58","administrator@vsphere.local","Root@123"))
