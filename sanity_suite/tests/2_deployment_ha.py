from sanity_suite.conf_tcs.config import *
from sanity_suite.lib_tcs.utils import *

"""config_file, args = get_config_file(sys.argv)
config = __import__(config_file)

for member_name in dir(config):
    if not member_name.startswith("__"):
        globals()[member_name] = getattr(config, member_name)"""

class DeployQA(QAMixin, unittest.TestCase):

    #def __init__(self, *args, **kwargs):
    #   super(DeployQA, self).__init__(*args, **kwargs)
    pio = PIOAppliance()

    vcenter_url = pio.get_url("/plugin")

    upload_pio_ovf = pio.get_url("PIOA_Primary/" + VERSION + "/upload/pio_ovf")
    upload_machine_ovf = pio.get_url("PIOA_Primary/" + VERSION + "/upload/machine_ovf")
    upload_vm_iso = pio.get_url("PIOA_Primary/" + VERSION + "/upload/vm_iso")

    deploy_pio_ovf = pio.get_url("PIOA_Primary/" + VERSION + "/deploy/pio_ovf")
    deploy_machine_ovf = pio.get_url("PIOA_Primary/" + VERSION + "/deploy/machine_ovf")

    cleanup_pio_vm = pio.get_url("PIOA_Primary/" + VERSION + "/cleanup/pio_vm")
    cleanup_machine_vm = pio.get_url("PIOA_Primary/" + VERSION + "/cleanup/machine_vm")

    get_machine_status = pio.get_url("PIOA_Primary/" + VERSION + "/vmopr/status_vm")
    start_machine = pio.get_url("PIOA_Primary/" + VERSION + "/vmopr/start_vm")
    stop_machine = pio.get_url("PIOA_Primary/" + VERSION + "/vmopr/stop_vm")

    cleanup_pio_ovf = pio.get_url("PIOA_Primary/" + VERSION + "/cleanup/pio_ovf")
    cleanup_machine_ovf = pio.get_url("PIOA_Primary/" + VERSION + "/cleanup/machine_ovf")
    cleanup_vm_iso = pio.get_url("PIOA_Primary/" + VERSION + "/cleanup/vm_iso")


    def setUp(self):
        sys.stdout.write("\r")
        self.pio.login()

    def tearDown(self):
        self.pio.logout()

    def get_vcenters(self):
        get_vcenter_url = self.pio.get_url("/plugin")
        logger.debug("Vcenter url is {}".format(get_vcenter_url))
        # self.pio.login()

        res = self.pio.get(get_vcenter_url)
        data = json.loads(res.read().decode('utf-8'))
        self.assertEqual(res.getcode(), 200)

        return data['data']


    def test_00_add_vcenter(self):
        '''
            Test which will try to re-add already added vCenter
            It is expected that this operation should fail
        '''
        data = {
                'ip': SANITY_VCENTER_IP,
                'username': VCENTER_USERNAME,
                'password': VCENTER_PASSWORD,
                'force_add': 0,
                'dtype': 0,
                'cloudburst_tag': 'HDM-CLOUDBURST',
                'workload_tag': 'HDM-APPLICATION-TYPE',
               }

        res = self.pio.post(self.vcenter_url, data)
        ret = json.loads(res.read().decode('utf-8'))
        logger.info(self.vcenter_url)
        logger.info(ret)

        rc = res.getcode()
        #do_pass(iself, 'test_00_add_vcenter', rc == 200 or rc == 201 or rc == 503 or rc == 409)
        assert rc==201, "Failed to add vCenter"

        

    """def test_01_upload_pio_ovf(self):
        #
        # test the setdata. Return code should be 0
        #
        try:
            values = {
                        'datacenter': DATACENTER,
                        'datacenter_username': DATACENTER_USERNAME,
                        'datacenter_type' : DATACENTER_TYPE,
                        'datacenter_datastore': DATACENTER_DATASTORE,
                     }

            res = self.pio.post(self.upload_pio_ovf, values)
            ret = res.read().decode('utf-8')

            logger.info(self.upload_pio_ovf)
            logger.info(values)
            logger.info(ret)

            assert res.getcode() == 200, "Failed to add pio_OVF"

            data = json.loads(ret)
            self.assertNotEqual(data.get("ovf_name"), None)
            self.__class__.pio_ovf_name = data.get("ovf_name")
        except Exception as err:
            logger.exception(err)
            do_pass(self, 'test_01_upload_pio_ovf', 0)

        do_pass(self, 'test_01_upload_pio_ovf', 1)"""

    def test_02_upload_machine_ovf(self):
        #
        # test the setdata. Return code should be 0
        #
        try:
            values = {
                        'datacenter': DATACENTER,
                        'datacenter_username': DATACENTER_USERNAME,
                        'datacenter_type' : DATACENTER_TYPE,
                        'datacenter_datastore': DATACENTER_DATASTORE,
                     }

            res = self.pio.post(self.upload_machine_ovf, values)
            ret = res.read().decode('utf-8')

            logger.info(self.upload_machine_ovf)
            logger.info(values)
            logger.info(ret)

            self.assertEqual(res.getcode(), 200)
            data = json.loads(ret)
            self.assertNotEqual(data.get("ovf_name"), None)
            self.__class__.machine_ovf_name = data.get("ovf_name")
        except Exception as err:
            logger.exception(err)
            do_pass(self, 'test_02_upload_machine_ovf', 0)

        do_pass(self, 'test_02_upload_machine_ovf', 1)

    def test_03_upload_vm_iso(self):
        try:
            values = {
                        'datacenter': DATACENTER,
                        'datacenter_username': DATACENTER_USERNAME,
                        'datacenter_type' : DATACENTER_TYPE,
                        'datacenter_datastore': DATACENTER_DATASTORE,
                        'iso_name': 'TEST_ISO'
                     }

            res = self.pio.post(self.upload_vm_iso, values)
            ret = res.read().decode('utf-8')

            logger.info(self.upload_machine_ovf)
            logger.info(values)
            logger.info(ret)

            self.assertEqual(res.getcode(), 200)
            data = json.loads(ret)
            self.assertNotEqual(data.get("iso_name"), None)
            self.__class__.vm_iso_name = data.get("iso_name")
        except Exception as err:
            logger.exception(err)
            do_pass(self, 'test_03_upload_vm_iso', 0)

        do_pass(self, 'test_03_upload_vm_iso', 1)

    def test_04_deploy_pio_ovf(self):
        try:
            values = {
                        'datacenter': DATACENTER,
                        'datacenter_username': DATACENTER_USERNAME,
                        'datacenter_type' : DATACENTER_TYPE,
                        'datacenter_datastore': DATACENTER_DATASTORE,
                        'datacenter_cluster_name' : DATACENTER_CLUSTER_NAME,
                        'datacenter_resource_pool': DATACENTER_RESOURCE_POOL,
                        'vm_name': "pio_vm"
                     }

            res = self.pio.post(self.deploy_pio_ovf, values)
            ret = res.read()

            logger.info(self.deploy_pio_ovf)
            logger.info(values)
            logger.info(ret)

            self.assertEqual(res.getcode(), 200)
            data = json.loads(ret)
        except Exception as err:
            logger.exception(err)
            do_pass(self, 'test_04_deploy_pio_ovf', 0)

        do_pass(self, 'test_04_deploy_pio_ovf', 1)

    def test_05_deploy_machine_ovf(self):
        try:
            values = {
                        'datacenter': DATACENTER,
                        'datacenter_username': DATACENTER_USERNAME,
                        'datacenter_type' : DATACENTER_TYPE,
                        'datacenter_datastore': DATACENTER_DATASTORE,
                        'datacenter_cluster_name' : DATACENTER_CLUSTER_NAME,
                        'datacenter_resource_pool': DATACENTER_RESOURCE_POOL,
                        'vm_name': "machine_vm"
                     }

            res = self.pio.post(self.deploy_machine_ovf, values)
            ret = res.read().decode('utf-8')

            logger.info(self.deploy_machine_ovf)
            logger.info(values)
            logger.info(ret)

            self.assertEqual(res.getcode(), 200)
            data = json.loads(ret)
        except Exception as err:
            logger.exception(err)
            do_pass(self, 'test_05_deploy_machine_ovf', 0)

        do_pass(self, 'test_05_deploy_machine_ovf', 1)

    def test_06_vm_get_status(self):
        #
        # test the setdata. Return code should be 0
        #
        try:
            values = {
                        'datacenter': DATACENTER,
                        'datacenter_username': DATACENTER_USERNAME,
                        'datacenter_type' : DATACENTER_TYPE,
                        "vm_name" : "machine_vm"
                     }

            res = self.pio.post(self.get_machine_status, values)
            ret = res.read().decode('utf-8')

            logger.info(self.get_machine_status)
            logger.info(values)
            logger.info(ret)

            self.assertEqual(res.getcode(), 200)
            data = json.loads(ret)
        except Exception as err:
            logger.exception(err)
            do_pass(self, 'test_06_vm_get_status', 0)

        do_pass(self, 'test_06_vm_get_status', 1)

    def test_07_stop_vm(self):
        #
        # test the setdata. Return code should be 0
        #
        try:
            values = {
                        'datacenter': DATACENTER,
                        'datacenter_username': DATACENTER_USERNAME,
                        'datacenter_type' : DATACENTER_TYPE,
                        "vm_name" : "machine_vm"
                     }

            res = self.pio.post(self.stop_machine, values)
            ret = res.read().decode('utf-8')

            logger.info(self.stop_machine)
            logger.info(values)
            logger.info(ret)

            self.assertEqual(res.getcode(), 200)
            data = json.loads(ret)
        except Exception as err:
            logger.exception(err)
            do_pass(self, 'test_07_stop_vm', 0)

        do_pass(self, 'test_07_stop_vm', 1)

    def test_08_start_vm(self):
        #
        # test the setdata. Return code should be 0
        #
        try:
            values = {
                        'datacenter': DATACENTER,
                        'datacenter_username': DATACENTER_USERNAME,
                        'datacenter_type' : DATACENTER_TYPE,
                        "vm_name" : "machine_vm"
                     }

            res = self.pio.post(self.start_machine, values)
            ret = res.read().decode('utf-8')

            logger.info(self.start_machine)
            logger.info(values)
            logger.info(ret)

            self.assertEqual(res.getcode(), 200)
            data = json.loads(ret)
        except Exception as err:
            logger.exception(err)
            do_pass(self, 'test_08_start_vm', 0)

        do_pass(self, 'test_08_start_vm', 1)

    def test_09_cleanup_pio_vm(self):
        #
        # test the setdata. Return code should be 0
        #
        try:
            values = {
                        'datacenter': DATACENTER,
                        'datacenter_username': DATACENTER_USERNAME,
                        'datacenter_type' : DATACENTER_TYPE,
                        "vm_name" : "pio_vm"
                     }

            res = self.pio.post(self.stop_machine, values)
            ret = res.read().decode('utf-8')

            logger.info(self.stop_machine)
            logger.info(values)
            logger.info(ret)

            self.assertEqual(res.getcode(), 200)

            values = {
                        'datacenter': DATACENTER,
                        'datacenter_username': DATACENTER_USERNAME,
                        'datacenter_type' : DATACENTER_TYPE,
                        "vm_name" : "pio_vm"
                     }

            res = self.pio.post(self.cleanup_pio_vm, values)
            ret = res.read().decode('utf-8')

            logger.info(self.cleanup_pio_vm)
            logger.info(values)
            logger.info(ret)

            self.assertEqual(res.getcode(), 200)
            data = json.loads(ret)
        except Exception as err:
            logger.exception(err)
            do_pass(self, 'test_09_cleanup_pio_vm', 0)

        do_pass(self, 'test_09_cleanup_pio_vm', 1)

    def test_10_cleanup_machine_vm(self):
        try:
            values = {
                        'datacenter': DATACENTER,
                        'datacenter_username': DATACENTER_USERNAME,
                        'datacenter_type' : DATACENTER_TYPE,
                        "vm_name" : "machine_vm"
                     }

            res = self.pio.post(self.stop_machine, values)
            ret = res.read().decode('utf-8')

            logger.info(self.stop_machine)
            logger.info(values)
            logger.info(ret)

            self.assertEqual(res.getcode(), 200)

            values = {
                        'datacenter': DATACENTER,
                        'datacenter_username': DATACENTER_USERNAME,
                        'datacenter_type' : DATACENTER_TYPE,
                        "vm_name" : "machine_vm"
                     }

            res = self.pio.post(self.cleanup_machine_vm, values)
            ret = res.read().decode('utf-8')

            logger.info(self.cleanup_machine_vm)
            logger.info(values)
            logger.info(ret)

            self.assertEqual(res.getcode(), 200)
            data = json.loads(ret)
        except Exception as err:
            logger.exception(err)
            do_pass(self, 'test_10_cleanup_machine_vm', 0)

        do_pass(self, 'test_10_cleanup_machine_vm', 1)

    def test_11_cleanup_pio_ovf(self):
        try:
            values = {
                        'datacenter': DATACENTER,
                        'datacenter_username': DATACENTER_USERNAME,
                        'datacenter_type' : DATACENTER_TYPE,
                     }

            res = self.pio.post(self.cleanup_pio_ovf, values)
            ret = res.read().decode('utf-8')

            logger.info(self.cleanup_pio_ovf)
            logger.info(values)
            logger.info(ret)

            self.assertEqual(res.getcode(), 200)
            data = json.loads(ret)
        except Exception as err:
            logger.exception(err)
            do_pass(self, 'test_11_cleanup_pio_ovf', 0)

        do_pass(self, 'test_11_cleanup_pio_ovf', 1)

    def test_12_cleanup_machine_ovf(self):
        try:
            values = {
                        'datacenter': DATACENTER,
                        'datacenter_username': DATACENTER_USERNAME,
                        'datacenter_type' : DATACENTER_TYPE,
                     }

            res = self.pio.post(self.cleanup_machine_ovf, values)
            ret = res.read().decode('utf-8')

            logger.info(self.cleanup_machine_ovf)
            logger.info(values)
            logger.info(ret)

            self.assertEqual(res.getcode(), 200)
            data = json.loads(ret)
        except Exception as err:
            logger.exception(err)
            do_pass(self, 'test_12_cleanup_machine_ovf', 0)

        do_pass(self, 'test_12_cleanup_machine_ovf', 1)

    def test_13_cleanup_vm_iso(self):
        try:
            values = {
                        'datacenter': DATACENTER,
                        'datacenter_username': DATACENTER_USERNAME,
                        'datacenter_type' : DATACENTER_TYPE,
                     }

            res = self.pio.post(self.cleanup_vm_iso, values)
            ret = res.read().decode('utf-8')

            logger.info(self.cleanup_vm_iso)
            logger.info(values)
            logger.info(ret)

            self.assertEqual(res.getcode(), 200)
            data = json.loads(ret)
        except Exception as err:
            logger.exception(err)
            assert False, "Exception occured"

        do_pass(self, 'test_13_cleanup_vm_iso', 1)
     
    def test_14_cleanup_vcenter(self):
        '''
            Test which would test delete vCenter PIO operation
            1.Add Vcenter
            2.Delte Vcenter
        '''
        data = {
                'username': VCENTER_USERNAME,
                'ip': VCENTER_IP,
                'password': VCENTER_PASSWORD,
                'force_add': 1,
                'cloudburst_tag': CLOUDBURST_TAG,
                'workload_tag': WORKLOAD_TAG,
                'dtype': 0,
               }
        vc_id = None
        vcenter = self.get_vcenters()
        for vc in vcenter:
            if vc.get('vcenter_ip') == VCENTER_IP:
                vc_id = vc.get('id')
                break

        data = {'force_delete': 1, 'id': vc_id}

        res = self.pio.delete(self.vcenter_url, data)
        ret = json.loads(res.read().decode('utf-8'))

        assert(res.getcode()== 200)

        logger.debug(self.vcenter_url)
        logger.debug(ret)

        rc = res.getcode()
        #do_pass(self, 'test_08_force_delete_vcenter', rc == 200 or rc == 503)
        assert rc == 200
  
         

if __name__ == "__main__":
    unittest.main(argv=["ha_deploy.py"] + args)
