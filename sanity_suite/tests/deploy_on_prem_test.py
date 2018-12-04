from sanity_suite.conf_tcs.config import *
from sanity_suite.lib_tcs.utils import *
import getopt

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

class DeployQA(QAMixin, unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(DeployQA, self).__init__(*args, **kwargs)
        self.pio = PIOAppliance()
        self.deploy_on_prem = self.pio.get_url("/deployment/onprem")
        self.deploy_update = self.pio.get_url("PIOA_Primary/v1.0/deployment/update")

    def setUp(self):
        warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed.*<ssl.SSLSocket.*>")
        self.vcenter = VCenter(VCENTER_IP, VCENTER_USERNAME, VCENTER_PASSWORD)
        sys.stdout.write("\r")

    def tearDown(self):
        self.vcenter.disconnect()
        self.pio.logout()

    def test_01_deploy_with_install(self):
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
                "service_type": "opsd",
                "scale": "1",
                "clusters": [
                    {
                     "cluster_moid": cluster._GetMoId(),
                     "resource_pool_moid": rs._GetMoId(),
                     "datastore_moid": ds._GetMoId(),
                     "network_moid": ns._GetMoId(),
                     "is_install": True
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
            do_pass(self, 'test_01_deploy_with_install', 0)

        do_pass(self, 'test_01_deploy_with_install', 1)

    def test_02_deploy_without_install(self):
        try:
            rs = self.vcenter.get_obj([vim.ResourcePool], VCENTER_RESOURCEPOOL)
            ds = self.vcenter.get_obj([vim.Datastore], VCENTER_DATASTORE)
            ns = self.vcenter.get_obj([vim.Network], VCENTER_NETWORK)
            cluster = self.vcenter.get_obj([vim.ClusterComputeResource], VCENTER_CLUSTER)

            values = {
                "vcenter_ip": VCENTER_IP,
                "service_type": "opsd",
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
            do_pass(self, 'test_02_deploy_with_install', 0)

        do_pass(self, 'test_02_deploy_with_install', 1)

    def test_03_deploy_with_deploy_failure(self):
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
                "service_type": "opsd",
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
            do_pass(self, 'test_03_deploy_with_deploy_failure', 0)

        do_pass(self, 'test_03_deploy_with_deploy_failure', 1)

if __name__ == "__main__":
    optlist, cmd_args = getopt.getopt(sys.argv[1:], '')
    args, logfolder = cmd_args
    args = [] if args=='none' else [args]
    unittest.main(argv=["deploy_on_prem_test.py"] + args)
