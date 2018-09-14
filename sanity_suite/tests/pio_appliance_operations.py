from sanity_suite.conf_tcs.config import *
from sanity_suite.lib_tcs.utils import *
import getopt

"""config_file, args = get_config_file(sys.argv)
config = __import__(config_file)

for member_name in dir(config):
    if not member_name.startswith("__"):
        globals()[member_name] = getattr(config, member_name)"""


pio = PIOAppliance()
MOD_SETUP_ERROR = ""
IS_POLICY_ATTACHED = False

def setUpModule():
    global MOD_SETUP_ERROR

    pio.login()

    # Add vCenter
    vc_cred = { 'username': VCENTER_USERNAME,
                'ip': VCENTER_IP,
                'password': VCENTER_PASSWORD,
                'force_add': 0}

    ret = pio.add_vcenter(vc_cred)

    if ret is False:
        MOD_SETUP_ERROR = "Failed to add vCenter"
        return
    
    # Get vCenters
    vcenter_list = pio.get_vcenters()
    vc_id = None

    if not vcenter_list:
        MOD_SETUP_ERROR = "Failed to get vCenter list"
        return

    for vc in vcenter_list:
        if vc.get('vcenter_ip') == VCENTER_IP:
            vc_id = vc.get('id')
            break

    if vc_id is None:
        MOD_SETUP_ERROR = "Failed to get vCenter ID"
        return

    cluster_name = ",".join(CLUSTER_NAMES)

    vc_data = { 'vcenter_id': vc.get('id'),
                'cluster_name': cluster_name
              }

    ret = pio.install(vc_data)

    if ret is False:
        MOD_SETUP_ERROR = "Failed to install vib"
        return

    # Configure clusters/hosts
    for cluster in CLUSTER_NAMES:
        cluster_data = { 'vcenter_id': vc.get('id'),
                        'cluster_name': cluster
                       }
        cluster_config = pio.get_cluster_config(cluster_data)
        selected_config = {}
        
        if cluster_config is None:
            MOD_SETUP_ERROR = "Failed to get cluster config info"
            return
        
        for conf in list(cluster_config.values()):
            for host in conf:
                selected_config[host['ip']] = {'addr': host['ip'], 'fd': 'default', 'enable_fd': 'True'}
                
        if not selected_config:
            MOD_SETUP_ERROR = "No config is selected for cluster configuration"
            return

        clust_config_data = { 'vcenter_id': vc_id,
                              'cluster_name': cluster,
                              'selected_config': selected_config
                            }

        ret = pio.configure_cluster(clust_config_data)
        if ret is False:
            MOD_SETUP_ERROR = "Failed to configure cluster %s" % cluster
            return

    # Reigster Plugin
    ret = pio.register({'vcenter_id': vc_id})

    if ret is False:
        MOD_SETUP_ERROR = "Failed to register plugin"
        return


def tearDownModule():

    pio.login()

    if IS_POLICY_ATTACHED is True:
        logger.error("Can't perform tearDownModule as Praapa is already"
                     "being used")
        return

    # Get vCenters
    vcenter_list = pio.get_vcenters()
    vc_id = None

    if not vcenter_list:
        logger.error("Failed to get vCenter list")
        return

    for vc in vcenter_list:
        if vc.get('vcenter_ip') == VCENTER_IP:
            vc_id = vc.get('id')
            break

    if vc_id is None:
        logger.error("Failed to get vCenter ID")
        return

    # Uninstall vib

    cluster_name = ",".join(CLUSTER_NAMES)

    vc_data = { 'vcenter_id': vc.get('id'),
                'cluster_name': cluster_name
              }

    ret = pio.uninstall(vc_data)

    if ret is False:
        logger.error("Failed to uninstall vib in tearDownModule")
        return

    # Unregister Plugin
    ret = pio.unregister({'vcenter_id': vc_id})

    if ret is False:
        logger.error ("Failed to unregister plugin in tearDownModule")
        return

    # Delete vCenter
    ret = pio.delete_vcenter({'force_delete': 0, 'id': vc_id})
    if ret is False:
        logger.error("Failed to delete vCenter in tearDownModule")

    return

class PioApplianceOperations(QAMixin, unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(PioApplianceOperations, self).__init__(*args, **kwargs)
        self.pio = PIOAppliance()
        self.vcenter_url = self.pio.get_url("/plugin")

        self.__class__.vcenter_id = None

        self.__class__.clusters = []
        self.__class__.cluster_net_config = {}
        self.__class__.cluster_name = None


    def setUp(self):
        sys.stdout.write("\r")
        self.pio.login()

    def test_01_enable_monitoring(self):
        logger.debug('Inside Test-case test_01_enable_monitoring')
        global IS_POLICY_ATTACHED

        if MOD_SETUP_ERROR:
            raise Exception("Setup failed: %s" % MOD_SETUP_ERROR)

        vm_uuid = None

        # Get VM uuid
        get_vms_url = self.pio.get_url("/report/vms/")

        res = self.pio.get(get_vms_url)
        rc = res.getcode()
        self.assertEqual(res.getcode(), 200)

        data = json.loads(res.read().decode('utf-8'))
        logger.debug(data)
        vm_list = data['data']

        for vm in vm_list:
            if vm.get('name') == VM_NAME_1:
                vm_uuid = vm.get('uuid')
                break

        self.assertNotEqual(vm_uuid, None)

        # Enable monitoring for selected VM
        enable_monitor_url = self.pio.get_url("/report/enabledetmon/%s" % vm_uuid)
        res = self.pio.post(enable_monitor_url, {})
        rc = res.getcode()
        self.assertEqual(res.getcode(), 200)

        do_pass(self, 'test_01_enable_monitoring', rc == 200 or rc == 503)

        IS_POLICY_ATTACHED = True

        return

    def test_02_pio_policy_attach(self):
        logger.debug('Inside Test-case test_02_pio_policy_attach')
        global IS_POLICY_ATTACHED

        if MOD_SETUP_ERROR:
            raise Exception("Setup failed: %s" % MOD_SETUP_ERROR)

        vm_uuid = None

        # Get VM uuid
        get_vms_url = self.pio.get_url("/report/vms/")

        res = self.pio.get(get_vms_url)
        rc = res.getcode()
        self.assertEqual(res.getcode(), 200)
        
        data = json.loads(res.read().decode('utf-8'))
        logger.debug(data)
        vm_list = data['data']

        for vm in vm_list:
            if vm.get('name') == VM_NAME:
                vm_uuid = vm.get('uuid')
                break

        self.assertNotEqual(vm_uuid, None)

        # Get cache data
        policy_attach_url = self.pio.get_url("/report/getdetails/%s" % vm_uuid)

        res = self.pio.get(policy_attach_url)
        rc = res.getcode()
        self.assertEqual(res.getcode(), 200)

        data = json.loads(res.read().decode('utf-8'))
        cache_data = data['data']

        # Send policy data
        attach_policy_data = { 'cache_size': int(cache_data['locality']),
                               'replica': CACHE_REPLICA,
                               'cache_policy': ATTACH_POLICY
                             }

        res = self.pio.post(policy_attach_url, attach_policy_data)
        rc = res.getcode()
        self.assertEqual(res.getcode(), 200)
        do_pass(self, 'test_02_pio_policy_attach', rc == 200 or rc == 503)

        IS_POLICY_ATTACHED = True

        return

    def test_03_get_overall_csv_report(self):
        logger.debug('Inside Test-case test_03_get_overall_csv_report')
        '''
        Download overall reorts at a given time
        '''
        if MOD_SETUP_ERROR:
            raise Exception("Setup failed: %s" % MOD_SETUP_ERROR)

        url = "/reportcsv?atime=0&component=Overall"
        report_url = self.pio.get_url(url)

        res = self.pio.get(report_url)
        rc = res.getcode()

        self.assertEqual(res.getcode(), 200)

        # Write CSV data to a file
        data = res.read()
        logger.debug(data)

        with open("overall_reports.csv", "w") as fd:
            fd.write(str(data))

        do_pass(self, 'test_03_get_overall_csv_report', rc == 200 or rc == 503)
        return

    def test_04_get_vm_csv_report(self):
        logger.debug('Inside Test-case test_04_get_vm_csv_report')
        '''
            Get reports of a particular VM
        '''

        if MOD_SETUP_ERROR:
            raise Exception("Setup failed: %s" % MOD_SETUP_ERROR)

        vm_uuid = None

        # Get VM uuid
        get_vms_url = self.pio.get_url("/report/vms/")

        res = self.pio.get(get_vms_url)
        rc = res.getcode()
        self.assertEqual(res.getcode(), 200)

        data = json.loads(res.read().decode('utf-8'))
        logger.debug(data)
        vm_list = data['data']

        for vm in vm_list:
            if vm.get('name') == VM_NAME:
                vm_uuid = vm.get('uuid')
                break

        self.assertNotEqual(vm_uuid, None)

        url = "/reportcsv?atime=0&component=%s" % vm_uuid
        vm_report_url = self.pio.get_url(url)

        res = self.pio.get(vm_report_url)
        rc = res.getcode()

        self.assertEqual(res.getcode(), 200)

        # Write CSV data to a file
        data = res.read()
        logger.debug(data)

        with open("%s_reports.csv" % vm.get('name'), "w") as fd:
            fd.write(str(data))

        do_pass(self, 'test_04_get_vm_csv_report', rc == 200 or rc == 503)
        return

    def tearDown(self):
        self.pio.logout()

if __name__ == "__main__":
    optlist, cmd_args = getopt.getopt(sys.argv[1:], '')
    args, logfolder = cmd_args
    args = [] if args=='none' else [args]
    unittest.main(argv=["pio_appliance_operations.py"] + args)
