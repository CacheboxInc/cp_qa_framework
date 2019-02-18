from sanity_suite.conf_tcs.config import *
from sanity_suite.lib_tcs.utils import *
import requests
import getopt
import time
from pyVim import connect
from pyVmomi import vmodl
from pyVmomi import vim
from sanity_suite.tests.vim_utils import *
from sanity_suite.tests.pbm_utils import *

import warnings

headers = {'Content-type':'application/json'}


class DeployQA(QAMixin, unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(DeployQA, self).__init__(*args, **kwargs)
        self.pio = PIOAppliance()
        self.vcenter_url = self.pio.get_url("plugin")
        self.deploy_on_prem = self.pio.get_url("/deployment/onprem")
        self.deploy_update = self.pio.get_url("PIOA_Primary/v1.0/deployment/update")
        self.register_plugin_url = self.pio.get_url("/install/2")
        self.unregister_plugin_url = self.pio.get_url("/uninstall/1")
        self.install_on_cluster_url = self.pio.get_url("/install/0")
        self.get_cluster_config_url = self.pio.get_url("/install/2")
        self.uninstall_on_cluster_url = self.pio.get_url("/uninstall/0")

        self.__class__.vcenter_id = None
    

    def setUp(self):
        warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed.*<ssl.SSLSocket.*>")
        '''self.add_vcenters()
        time.sleep(2)
        if self.__class__.vcenter_id is None:
            self.vcenter = self.get_vcenters()
            if (self.vcenter) == 0:
                logger.error("No vCenters :  Skipping all tests")
            for data in self.vcenter:
               if data["vcenter_ip"]==SANITY_VCENTER_IP:
                  self.__class__.vcenter_id = data['id']

        #Registring Plugin and         
        self.pio.login()
        values = {
                     'vcenter_id' : self.__class__.vcenter_id
                 }

        res = self.pio.post(self.register_plugin_url, values)
        data = res.read().decode('utf-8')

        logger.debug(self.register_plugin_url)
        logger.debug(data)
        assert res.getcode() == 200 , "Plugin registration gets failed"
        
        #Install VAIO
        values = {
                        'vcenter_id' : self.__class__.vcenter_id,
                        'cluster_name' : SANITY_VCENTER_CLUSTER
                     }

        res = self.pio.post(self.install_on_cluster_url, values)
        time.sleep(6)'''

        

        self.vcenter = VCenter(VCENTER_IP, VCENTER_USERNAME, VCENTER_PASSWORD)

    def tearDown(self):
        
        '''values = {
                        'vcenter_id' : self.__class__.vcenter_id,
                        'cluster_name' : SANITY_VCENTER_CLUSTER
                     }

        res = self.pio.post(self.uninstall_on_cluster_url, values)
        data = res.read().decode('utf-8')
        time.sleep(8)
        logger.debug(self.uninstall_on_cluster_url)
        
        #Unregister Plugin
        values = {
                  'vcenter_id' : self.__class__.vcenter_id
                 }

        res = self.pio.post(self.unregister_plugin_url, values)
        data = res.read().decode('utf-8')

        logger.debug(self.unregister_plugin_url)
        logger.debug(data)

        self.assertEqual(res.getcode(), 200)

        self.delete_vcenters()
        #self.pio.login()
        #self.vcenter.disconnect()
        #self.pio.logout()'''


    def add_vcenters(self):
        '''
            Test which would test add vCenter PIO operation
        '''
        data = {
                'username': VCENTER_USERNAME,
                'ip': SANITY_VCENTER_IP,
                'password': VCENTER_PASSWORD,
                'cloudburst_tag': CLOUDBURST_TAG,
                'workload_tag': WORKLOAD_TAG,
                'force_add': 1,
                'dtype': 0,
               }
        resp = requests.post(self.vcenter_url, json=data, verify=False, headers=headers)
        ret = resp.status_code
        logger.info(self.vcenter_url)
        logger.info(ret)
        logger.info(resp)
        #assert ret == 201, "Vcenter is not added successfully"

    def get_vcenters(self):
        get_vcenter_url = self.pio.get_url("/plugin")

        self.pio.login()

        res = self.pio.get(get_vcenter_url)
        ret = res.read()

        logger.debug(get_vcenter_url)
        logger.debug(ret)

        data = json.loads(ret.decode('utf-8'))
        self.assertEqual(res.getcode(), 200)
        print(ret)
        return data['data']


    def delete_vcenters(self):

        self.vcenters = self.get_vcenters()
        vc_id = None

        for vc in self.vcenter:
            if vc.get('vcenter_ip') == SANITY_VCENTER_IP:
                vc_id = vc.get('id')
                data = {'force_delete': 1, 'id': vc_id}

                res = self.pio.delete(self.vcenter_url, data)
                ret = json.loads(res.read().decode('utf-8'))

                assert(res.getcode()== 200)

                logger.debug(self.vcenter_url)
                logger.debug(ret)

                rc = res.getcode()
                assert rc == 200

    """def test_01_deploy_with_install(self):
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

        do_pass(self, 'test_01_deploy_with_install', 1)"""

    def test_02_deploy_without_install(self):
        try:
            rs = self.vcenter.get_obj([vim.ResourcePool], VCENTER_RESOURCEPOOL)
            ds = self.vcenter.get_obj([vim.Datastore], VCENTER_DATASTORE)
            ns = self.vcenter.get_obj([vim.Network], VCENTER_NETWORK)
            cluster = self.vcenter.get_obj([vim.ClusterComputeResource], VCENTER_CLUSTER)

            values = {
                "vcenter_ip": VCENTER_IP,
                "service_type": "VDDK",
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

    """def test_03_deploy_with_deploy_failure(self):
        #
        # test the setdata. Return code should be 0
        #
        try:
            rs = self.vcenter.get_obj([vim.ResourcePool], SANITY_VCENTER_RESOURCEPOOL)
            ds = self.vcenter.get_obj([vim.Datastore], SANITY_VCENTER_DATASTORE)
            ns = self.vcenter.get_obj([vim.Network], VCENTER_NETWORK)
            cluster = self.vcenter.get_obj([vim.ClusterComputeResource], SANITY_VCENTER_CLUSTER)

            values = {
                "vcenter_ip": SANITY_VCENTER_IP,
                "service_type": "VDDK",
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

                logger.info(self.deploy_update)
                logger.info(data)
                logger.info(res.getcode())
                #self.assertEqual(res.getcode(), 200)
                assert res.getcode() ==200 , "failed to deploy with faliure"

        except Exception as err:
            logger.exception(err)
            do_pass(self, 'test_03_deploy_with_deploy_failure', 0)

        do_pass(self, 'test_03_deploy_with_deploy_failure', 1)"""




