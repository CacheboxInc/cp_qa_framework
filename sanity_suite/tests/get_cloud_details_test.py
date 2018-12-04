from sanity_suite.conf_tcs.config import *
from sanity_suite.lib_tcs.utils import *
import getopt
import requests

from pyVim import connect
from pyVmomi import vmodl
from pyVmomi import vim
from sanity_suite.tests.vim_utils import *
from sanity_suite.tests.pbm_utils import *

import warnings

"""config_file, args = get_config_file(sys.argv)
config = __import__(config_file)

for member_name in dir(config):
    if not member_name.startswith("__"):
        globals()[member_name] = getattr(config, member_name)"""

headers = {'Content-type': 'application/json'}



class GetCloudDetailsQA(QAMixin, unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(GetCloudDetailsQA, self).__init__(*args, **kwargs)
        self.pio = PIOAppliance()
        self.get_cloud_details_url = self.pio.get_url("cloud/get_cloud_details")
        self.cloud_details_data = None
        self.cloud_type = "VMC"

    def setUp(self):
        warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed.*<ssl.SSLSocket.*>")
        self.vcenter = VCenter(VCENTER_IP, VCENTER_USERNAME, VCENTER_PASSWORD)
        sys.stdout.write("\r")

    def tearDown(self):
        self.vcenter.disconnect()
        self.pio.logout()

    def collect_cloud_resources_stats(self, cloud_ip, username, password):

        total_cpu_cores = 0
        total_storage   = 0
        total_memory    = 0

        used_cpu_cores  = 0
        used_storage    = 0
        used_memory     = 0

        resource_stats = {}

        try:
            vc_obj = VCenter(cloud_ip, username, password)
        except:
            return resource_stats

        datacenters = vc_obj.get_datacenters()

        for datacenter in datacenters:
            cluster_list = vc_obj.get_clusters(datacenter)

            for cluster in cluster_list:
                hosts = []
                resource_usage = cluster.GetResourceUsage()

                total_storage += (resource_usage.storageCapacityMB << 20)
                used_storage  += (resource_usage.storageUsedMB << 20 )

                total_memory += (resource_usage.memCapacityMB << 20)
                used_memory  += (resource_usage.memUsedMB << 20)

                cluster_obj = VCenterCluster(cluster)
                host_list = cluster_obj.get_hosts()

                for host in host_list:
                    vms   = []
                    total_cpu_cores += (host.hardware.cpuInfo.numCpuCores * 32)
                    vms.extend(host.vm)
                    for vm in vms:
                        used_cpu_cores += (int(vm.config.hardware.numCoresPerSocket) *
                                                  int(vm.config.hardware.numCPU))

        total_cpu_cores = 240

        resource_stats['available']            = {}
        resource_stats['available']['compute'] = total_cpu_cores - used_cpu_cores
        resource_stats['available']['storage'] = total_storage   - used_storage
        resource_stats['available']['memory']  = total_memory    - used_memory

        resource_stats['used']            = {}
        resource_stats['used']['compute'] = used_cpu_cores
        resource_stats['used']['storage'] = used_storage
        resource_stats['used']['memory']  = used_memory

        return resource_stats

    def login(self):

        url = "https://%s/api-token-auth" % APPLIANCE_IP

        data = { 'username': 'administrator@pio.com',
                 'password': 'admin@123'
               }

        resp = requests.post(url, json=data, verify=False, headers=headers)

        return resp.json()

    def add_cloud_details(self):

        self.cloud_details_data = {
                                   'username': CLOUD_USER_NAME,
                                   'ip': CLOUD_IP,
                                   'password': CLOUD_PASSWORD,
                                   'force_add': 0,
                                   'dtype': 8,
                                   'appliance_ip': CLOUD_APPLIANCE_IP,
                                   'name' : "cloud_vcenter",
                                   'location' : "oregano",
                                   'global_username': CLOUD_USER_NAME,
                                   'global_password': CLOUD_PASSWORD
                                  }

        token = self.login()['token']

        url = "https://%s/plugin" % APPLIANCE_IP

        headers['Authorization'] = 'token {}'.format(token)

        requests.post(url, json=self.cloud_details_data, verify=False, headers=headers)

    def test_01_validate_cloud_details(self):
        self.add_cloud_details()

        resp = self.pio.get(self.get_cloud_details_url)
        resp = json.loads(resp.read().decode('utf-8'))

        status =  resp.get("status", {})
        if int(status.get("status", 1)) != 0:
            print("failed to fetch cloud details\n")
            return

        data = resp.get("data", {})
        cloud_data = data.get(self.cloud_type, {})[0]

        cloud_resource_stats = self.collect_cloud_resources_stats(CLOUD_IP, CLOUD_USER_NAME, CLOUD_PASSWORD)

        assert(cloud_data["available"]["memory"] == cloud_resource_stats["available"]["memory"])
        assert(cloud_data["available"]["vcpu"] == cloud_resource_stats["available"]["compute"])

        total_memory = cloud_resource_stats["available"]["memory"] + cloud_resource_stats["used"]["memory"]
        total_vcpu   = cloud_resource_stats["available"]["compute"] + cloud_resource_stats["used"]["compute"]

        assert(cloud_data["total"]["memory"] == total_memory)
        assert(cloud_data["total"]["vcpu"] == total_vcpu)

if __name__ == "__main__":
    unittest.main(argv=["get_cloud_details_test.py"])
