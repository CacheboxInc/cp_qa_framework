import requests
import getopt
from sanity_suite.conf_tcs.config import *
from sanity_suite.lib_tcs.utils import *
headers = {'Content-type':'application/json'}


class AddRemoveVcenter(QAMixin, unittest.TestCase):

    def __init__(self, *args, **kwargs):
        logger.debug("Inside init() method")
        super(AddRemoveVcenter, self).__init__(*args, **kwargs)
        self.pio = PIOAppliance()
        self.vcenter_url = self.pio.get_url("plugin")
        self.__class__.vcenter_id = None

        self.__class__.clusters = []
        self.__class__.cluster_net_config = {}
        self.__class__.cluster_name = None

    def setUp(self):
        logger.debug("Inside setUp")
        sys.stdout.write("\r")
        self.pio.login()

    def tearDown(self):
        logger.debug("Inside tearDown")
        self.pio.logout()

    def get_vcenters(self):
        get_vcenter_url = self.pio.get_url("/plugin")
        logger.debug("Vcenter url is {}".format(get_vcenter_url))
        # self.pio.login()

        res = self.pio.get(get_vcenter_url)
        data = json.loads(res.read().decode('utf-8'))
        self.assertEqual(res.getcode(), 200)

        return data['data'] 

    def test_01_add_vcenter(self):
        '''
            Test which would test add vCenter PIO operation
        '''
        data = {
                'username': VCENTER_USERNAME,
                'ip': SANITY_VCENTER_IP,
                'password': VCENTER_PASSWORD,
                'cloudburst_tag': CLOUDBURST_TAG,
                'workload_tag': WORKLOAD_TAG,
                'force_add': 0,
                'dtype': 0,
               }
        resp = requests.post(self.vcenter_url, json=data, verify=False, headers=headers)
        ret = resp.status_code
        logger.info(self.vcenter_url)
        logger.info(ret)
        logger.info(resp)
        assert ret == 201, "Vcenter is not added successfully"


    def test_02_re_add_existing_vcenter(self):
        '''
            Test which will try to re-add already added vCenter
            It is expected that this operation should fail
        '''
        data = {
                'username': VCENTER_USERNAME,
                'ip': SANITY_VCENTER_IP,
                'password': VCENTER_PASSWORD,
                'cloudburst_tag': CLOUDBURST_TAG,
                'workload_tag': WORKLOAD_TAG,
                'force_add': 0,
                'dtype': 0,
 
                
               }
        res = self.pio.post(self.vcenter_url, data)
        ret = json.loads(res.read().decode('utf-8'))
        assert(res.getcode()== 409) 
        logger.debug(self.vcenter_url)
        logger.debug(ret)

        rc = res.getcode()
        #do_pass(self, 'test_02_re_add_existing_vcenter', rc == 409 or rc == 503)
        assert(rc == 409 or rc == 503)


    def test_03_delete_vcenter(self):
        '''
            Test which would test delete vCenter PIO operation
        '''
        self.vcenter = self.get_vcenters()
        vc_id = None

        for vc in self.vcenter:
            if vc.get('vcenter_ip') == SANITY_VCENTER_IP:
                vc_id = vc.get('id')
                break

        data = {'force_delete': 0, 'id': vc_id}

        res = self.pio.delete(self.vcenter_url, data)
        ret = json.loads(res.read().decode('utf-8'))

        assert(res.getcode()==200)

        logger.debug(self.vcenter_url)
        logger.debug(ret)

        rc = res.getcode()
        #do_pass(self, 'test_03_delete_vcenter', rc == 200 or rc == 503)
        assert(rc == 200 or rc == 503)

    
    def test_04_force_add(self):
        '''
            Force add the vcenter to the PIO_Appliance
            1.Using Force option to add the vcenter
            2.Delete the vcenter after add
        '''
        data = {
                'username': VCENTER_USERNAME,
                'ip': SANITY_VCENTER_IP,
                'password': VCENTER_PASSWORD,
                'force_add': 1,
                'cloudburst_tag': CLOUDBURST_TAG,
                'workload_tag': WORKLOAD_TAG,

                'dtype': 0,

               }
        res = self.pio.post(self.vcenter_url, data)
        
        ret = json.loads(res.read().decode('utf-8'))
        self.assertEqual(res.getcode(), 201) 
        logger.debug(self.vcenter_url)
        logger.debug(ret)
        rc = res.getcode()
        #do_pass(self, 'test_04_force_add', rc == 201 or rc == 503)
        assert(rc == 201 or rc == 503)
        
        self.vcenter = self.get_vcenters()
        vc_id = None
        for vc in self.vcenter:
            if vc.get('vcenter_ip') == SANITY_VCENTER_IP:
                vc_id = vc.get('id')
                break

        data = {'force_delete': 0, 'id': vc_id}

        res = self.pio.delete(self.vcenter_url, data)
        ret = json.loads(res.read().decode('utf-8'))

        assert(res.getcode()== 200)

        logger.debug(self.vcenter_url)
        logger.debug(ret)
    
    def test_05_add_vcenter_invalid_ip(self):
        '''
        Add vcenter with invalid IP to the PIO_Appliance
        '''
        INVALID_VC_IP = '169.168.0.0'
        err_msg = "Error: PM-141: Please ensure that vCenter {} is reachable from the appliance.".format(INVALID_VC_IP)
        data = {
                'username': VCENTER_USERNAME,
                'ip': INVALID_VC_IP,
                'password': VCENTER_PASSWORD,
                'force_add': 1,
                'cloudburst_tag': CLOUDBURST_TAG,
                'workload_tag': WORKLOAD_TAG,
                'dtype': 0,

               }
        res = self.pio.post(self.vcenter_url, data)
        ret = json.loads(res.read().decode('utf-8'))
        ret_msg = ret['msg']
        assert(ret_msg== err_msg)
        logger.debug(self.vcenter_url)
        logger.debug(ret)
        rc = res.getcode()
        #do_pass(self, 'test_05_add_vcenter_invalid_ip', rc == 500)
        assert rc != 201 , "Vcenter with invalid Ip added successfully"
        
    def test_06_add_vcenter_invalid_userid(self):
        '''
        Add vcenter with wrong user_id
        '''
        err_msg = "Please check the credentials for vCenter {}.".format(SANITY_VCENTER_IP)
        data = {
                'username':"%s_rand_string" %VCENTER_USERNAME,
                'ip': SANITY_VCENTER_IP,
                'password': VCENTER_PASSWORD,
                'force_add': 0,
                'cloudburst_tag': CLOUDBURST_TAG,
                'workload_tag': WORKLOAD_TAG,
                'dtype': 0,

               }
        res = self.pio.post(self.vcenter_url, data)
        ret = json.loads(res.read().decode('utf-8'))
        ret_msg = ret['msg']
        assert (ret_msg== err_msg , "Proper error message is not getting displayed")
        logger.debug(self.vcenter_url)
        logger.debug(ret)
        rc = res.getcode()
        assert rc != 201 ,"vCenter got added with invalid credentials"
        
    def test_07_add_vcenter_invalid_pwd(self):
        '''
        Add vcenter with wrong user_id
        '''
        err_msg = "Please check the credentials for vCenter {}.".format(SANITY_VCENTER_IP)
        data = {
                'username': VCENTER_USERNAME,
                'ip': SANITY_VCENTER_IP,
                'password': "%s_rand_string"%VCENTER_PASSWORD,
                'force_add': 0,
                'cloudburst_tag': CLOUDBURST_TAG,
                'workload_tag': WORKLOAD_TAG,
                'dtype': 0,

               }
        res = self.pio.post(self.vcenter_url, data)
        ret = json.loads(res.read().decode('utf-8'))
        ret_msg = ret['msg']
        assert(ret_msg == err_msg ,"Proper error message is not getting displayed"  )
        logger.debug(self.vcenter_url)
        logger.debug(ret)
        rc = res.getcode()
        #do_pass(self, 'test_07_add_vcenter_invalid_pwd', rc == 500)
        assert rc == 500 

    def test_07_add_vcenter_invalid_credentials(self):
        '''
        Add vcenter with wrong user_id
        '''
        err_msg = "Please check the credentials for vCenter {}.".format(SANITY_VCENTER_IP)
        data = {
                'username': 'test',
                'ip': '10.10.0.0',
                'password': "%s_rand_string"%VCENTER_PASSWORD,
                'force_add': 0,
                'cloudburst_tag': CLOUDBURST_TAG,
                'workload_tag': WORKLOAD_TAG,
                'dtype': 0,

               }
        res = self.pio.post(self.vcenter_url, data)
        ret = json.loads(res.read().decode('utf-8'))
        ret_msg = ret['msg']
        assert(ret_msg == err_msg ,"Proper error message is not getting displayed"  )
        logger.debug(self.vcenter_url)
        logger.debug(ret)
        rc = res.getcode()
        #do_pass(self, 'test_07_add_vcenter_invalid_pwd', rc == 500)
        assert rc == 500


    def test_09_force_delete_vcenter(self):
        '''
            Test which would test delete vCenter PIO operation
            1.Add Vcenter
            2.Delte Vcenter
        '''
        data = {
                'username': VCENTER_USERNAME,
                'ip': SANITY_VCENTER_IP,
                'password': VCENTER_PASSWORD,
                'force_add': 1,
                'cloudburst_tag': CLOUDBURST_TAG,
                'workload_tag': WORKLOAD_TAG,
                'dtype': 0,
               }
        res = self.pio.post(self.vcenter_url, data)
        ret = json.loads(res.read().decode('utf-8'))
        assert(res.getcode() == 201)
        logger.debug(self.vcenter_url)
        logger.debug(ret)
        rc = res.getcode()
        self.vcenter = self.get_vcenters()
        vc_id = None
        
        for vc in self.vcenter:
            if vc.get('vcenter_ip') == SANITY_VCENTER_IP:
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

