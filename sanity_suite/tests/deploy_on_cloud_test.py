from sanity_suite.conf_tcs.config import *
from sanity_suite.lib_tcs.utils import *
import getopt

from pyVim import connect
from pyVmomi import vmodl
from pyVmomi import vim
from unit_suite.tests.vim_utils import *
from unit_suite.tests.pbm_utils import *


import warnings

"""config_file, args = get_config_file(sys.argv)
config = __import__(config_file)

for member_name in dir(config):
    if not member_name.startswith("__"):
        globals()[member_name] = getattr(config, member_name)"""

class DeployCloudQA(QAMixin, unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(DeployCloudQA, self).__init__(*args, **kwargs)
        self.pio = PIOAppliance()
        self.vcenter_url = self.pio.get_url("/plugin")
        self.deploy_on_cloud = self.pio.get_url("/deployment/oncloud")
        self.deploy_on_prem = self.pio.get_url("/deployment/onprem")
        self.deploy_update = self.pio.get_url("PIOA_Primary/v1.0/deployment/update")

    def setUp(self):
        warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed.*<ssl.SSLSocket.*>")
        self.vcenter = VCenter(VCENTER_IP, VCENTER_USERNAME, VCENTER_PASSWORD)
        sys.stdout.write("\r")

    def tearDown(self):
        self.vcenter.disconnect()
        self.pio.logout()

    def test_01_add_vmc(self):
        '''
            Test which would test add vCenter PIO operation
        '''
        data = {
                'ip': DATACENTER,
                'username': DATACENTER_USERNAME,
                'password': DATACENTER_PASSWORD,
                'force_add': 0,
                'dtype': 8
               }

        res = self.pio.post(self.vcenter_url, data)
        ret = json.loads(res.read().decode('utf-8'))

        logger.debug(self.vcenter_url)
        logger.debug(ret)

        rc = res.getcode()
        do_pass(self, 'test_01_add_vcenter', rc == 201 or rc == 503 or rc == 409)

        return

    def test_02_get_cluster_resource(self):
        try:
            data = {"cloud_ip" : DATACENTER}

            res = self.pio.get(self.deploy_on_cloud, data)
            data = res.read().decode('utf-8')

            logger.debug(self.deploy_on_prem)
            logger.debug(data)

            self.assertEqual(res.getcode(), 200)

            data = json.loads(data)

        except Exception as err:
            logger.exception(err)
            do_pass(self, 'test_02_get_cluster_resource', 0)

        do_pass(self, 'test_02_get_cluster_resource', 1)


    def test_03_deploy_gateway(self):
        #
        # test the setdata. Return code should be 0
        #
        try:
            rs = self.vcenter.get_obj([vim.ResourcePool], VCENTER_RESOURCEPOOL)
            ds = self.vcenter.get_obj([vim.Datastore], VCENTER_DATASTORE)
            ns = self.vcenter.get_obj([vim.Network], VCENTER_NETWORK)

            cluster = self.vcenter.get_obj([vim.ClusterComputeResource], VCENTER_CLUSTER)

            values = {
                "vcenter_ip": VCENTER_IP,
                "service_type": "gateway",
                "scale": "1",
                "clusters": [
                    {
                     "cluster_moid": cluster._GetMoId(),
                     "resource_pool_moid": rs._GetMoId(),
                     "datastore_moid": ds._GetMoId(),
                     "network_moid": ns._GetMoId(),
                     "is_install": False
                    }
                  ]  
                  }
            res = self.pio.post(self.deploy_on_prem, values)
            data = res.read().decode('utf-8')

            logger.debug(self.deploy_on_prem)
            logger.debug(data)

            self.assertEqual(res.getcode(), 200)

            data = json.loads(data)

            uuids = data.get("uuids")

            for uuid in uuids:
                values = {
                          "uuid": uuid,
                          "status": 1,
                          "progress": 20,
                          "message" : ""
                }

                res = self.pio.post(self.deploy_update, values)
                data = res.read().decode('utf-8')

                logger.debug(self.deploy_update)
                logger.debug(data)

                self.assertEqual(res.getcode(), 200)

                values = {
                          "uuid": uuid,
                          "status": 1,
                          "progress": 100,
                          "message" : ""
                }

                res = self.pio.post(self.deploy_update, values)
                data = res.read().decode('utf-8')

                logger.debug(self.deploy_update)
                logger.debug(data)

                self.assertEqual(res.getcode(), 200)
            
        except Exception as err:
            logger.exception(err)
            do_pass(self, 'test_03_deploy_gateway', 0)

        do_pass(self, 'test_03_deploy_gateway', 1)

    def test_04_deploy_on_vmc(self):
        try:
            data = {"cloud_ip" : DATACENTER}

            res = self.pio.get(self.deploy_on_cloud, data)
            data = res.read().decode('utf-8')

            logger.debug(self.deploy_on_prem)
            logger.debug(data)

            self.assertEqual(res.getcode(), 200)

            data = json.loads(data)

            cluster = None
            rs = None
            ds = None
            ns = None

            for d in data:
                if d["clusters"][0]["name"] != DATACENTER_CLUSTER_NAME:
                    continue

                cluster = d["clusters"][0]["moid"]

                for r in d["resource_pool"]:
                    if r["name"] != DATACENTER_RESOURCE_POOL:
                        continue
                    rs = r["moid"]

                for dt in d["datastores"]:
                    if dt["name"] != DATACENTER_DATASTORE:
                        continue
                    ds = dt["moid"]

                for n in d["networks"]:
                    if n["name"] != DATACENTER_NETWORK_NAME:
                        continue
                    ns = n["moid"]


            self.assertNotEqual(cluster, None)
            self.assertNotEqual(rs, None)
            self.assertNotEqual(ds, None)
            self.assertNotEqual(ns, None)

            services = []

            for service_type, scale in CLOUD_SERVICES:
                services.append({"service_type": service_type, "scale": scale})

            values = {
                "vcenter_ip": VCENTER_IP,
                "cloud_ip": DATACENTER,
                "clusters": [
                    {
                     "cluster_moid": cluster,
                     "resource_pool_moid": rs,
                     "datastore_moid": ds,
                     "network_moid": ns,
                     "services": services
                    }
                  ]  
                  }

            res = self.pio.post(self.deploy_on_cloud, values)
            data = res.read().decode('utf-8')

            logger.debug(self.deploy_on_cloud)
            logger.debug(data)

            self.assertEqual(res.getcode(), 200)

            data = json.loads(data)

            uuids = data.get("uuids")

            for uuid in uuids:
                values = {
                          "uuid": uuid,
                          "status": 1,
                          "progress": 100,
                          "message" : ""
                }

                res = self.pio.post(self.deploy_update, values)
                data = res.read().decode('utf-8')

                logger.debug(self.deploy_update)
                logger.debug(data)

                self.assertEqual(res.getcode(), 200)
            
        except Exception as err:
            logger.exception(err)
            do_pass(self, 'test_04_deploy_on_vmc', 0)

        do_pass(self, 'test_04_deploy_on_vmc', 1)

    def test_05_deploy_with_deploy_failure(self):
        #
        # test the setdata. Return code should be 0
        #
        try:
            data = {"cloud_ip" : DATACENTER}

            res = self.pio.get(self.deploy_on_cloud, data)
            data = res.read().decode('utf-8')

            logger.debug(self.deploy_on_prem)
            logger.debug(data)

            self.assertEqual(res.getcode(), 200)

            data = json.loads(data)

            cluster = None
            rs = None
            ds = None
            ns = None

            for d in data:
                if d["clusters"][0]["name"] != DATACENTER_CLUSTER_NAME:
                    continue

                cluster = d["clusters"][0]["moid"]

                for r in d["resource_pool"]:
                    if r["name"] != DATACENTER_RESOURCE_POOL:
                        continue
                    rs = r["moid"]

                for dt in d["datastores"]:
                    if dt["name"] != DATACENTER_DATASTORE:
                        continue
                    ds = dt["moid"]

                for n in d["networks"]:
                    if n["name"] != DATACENTER_NETWORK_NAME:
                        continue
                    ns = n["moid"]

            self.assertNotEqual(cluster, None)
            self.assertNotEqual(rs, None)
            self.assertNotEqual(ds, None)
            self.assertNotEqual(ns, None)

            services = []

            for service_type, scale in CLOUD_SERVICES:
                services.append({"service_type": service_type, "scale": scale})

            values = {
                "vcenter_ip": VCENTER_IP,
                "cloud_ip": DATACENTER,
                "clusters": [
                    {
                     "cluster_moid": cluster,
                     "resource_pool_moid": rs,
                     "datastore_moid": ds,
                     "network_moid": ns,
                     "services": services
                    }
                  ]  
                 }

            res = self.pio.post(self.deploy_on_cloud, values)
            data = res.read().decode('utf-8')

            logger.debug(self.deploy_on_cloud)
            logger.debug(data)

            self.assertEqual(res.getcode(), 200)

            data = json.loads(data)

            uuids = data.get("uuids")

            for uuid in uuids:

                values = {
                          "uuid": uuid,
                          "status": 2,
                          "progress": 0,
                          "message" : "Failed Failed Failed"
                }

                res = self.pio.post(self.deploy_update, values)
                data = res.read().decode('utf-8')

                logger.debug(self.deploy_update)
                logger.debug(data)

                self.assertEqual(res.getcode(), 200)

        except Exception as err:
            logger.exception(err)
            do_pass(self, 'test_05_deploy_with_deploy_failure', 0)

        do_pass(self, 'test_05_deploy_with_deploy_failure', 1)

if __name__ == "__main__":
    optlist, cmd_args = getopt.getopt(sys.argv[1:], '')
    args, logfolder = cmd_args
    args = [] if args=='none' else [args]
    unittest.main(argv=["deploy_on_cloud_test.py"] + args)
