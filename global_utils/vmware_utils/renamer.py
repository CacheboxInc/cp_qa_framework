from pyVmomi import vim
import urllib.request
import requests
from pyVim import connect
import subprocess
import ssl
import atexit

def get_obj(content, vimtype, name = None):
   return [item for item in content.viewManager.CreateContainerView(content.rootFolder, [vimtype], recursive=True).view]

def connect_to_vc(host,user,pwd):
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

def rename_cluster(host,user,pwd,cluster_name,new_name):
   content = connect_to_vc(host,user,pwd)
   for cluster_obj in get_obj(content, vim.ComputeResource):
      #print(cluster_obj.name)
      if cluster_obj.name == cluster_name:
         cluster_obj.Rename(new_name)

def rename_vm(host,user,pwd,cluster_name,old_name, new_name):
   content = connect_to_vc(host,user,pwd)
   for cluster_obj in get_obj(content, vim.ComputeResource):
      #print(cluster_obj.name)
      if cluster_obj.name == cluster_name:
         cluster_name_found = True
         for host in cluster_obj.host:
            #print(host.vm)
            for vm in host.vm:
                #print(vm.name)
                if vm.name == old_name:
                    vm_name_found = True
                    vm.Rename(new_name)
                    print(vm_name_found)






#print(rename_vm("10.10.8.58","administrator@vsphere.local","Root@123","Cluster","VM5","VM8"))
#print(rename_cluster("10.10.8.58","administrator@vsphere.local","Root@123","Cluster","test"))
