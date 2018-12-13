
from sanity_suite.conf_tcs.config import *
from sanity_suite.lib_tcs.utils import *

"""config_file, args = get_config_file(sys.argv)
config = __import__(config_file)

for member_name in dir(config):
    if not member_name.startswith("__"):
        globals()[member_name] = getattr(config, member_name)"""


pio = PIOAppliance()
MOD_SETUP_ERROR = ""

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

    # Install vib

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

class PioUninstallNegative(QAMixin, unittest.TestCase):
    '''
        Validate negative scenarios for PIO uninstall
    '''

    def __init__(self, *args, **kwargs):
        super(PioUninstallNegative, self).__init__(*args, **kwargs)
        self.pio = PIOAppliance()

    def setUp(self):
        sys.stdout.write("\r")
        self.pio.login()

    def test_uninstall_wrong_cluster(self):
        '''
            Try to uninstall vib from cluster on which PIO is not installed or
            cluster is not present, it is expected that REST call should fail
        '''

        if MOD_SETUP_ERROR:
            raise Exception("Setup failed: %s" % MOD_SETUP_ERROR)

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
        uninstall_url = self.pio.get_url("/uninstall/0")

        vc_data = { 'vcenter_id': vc.get('id'),
                    'cluster_name': "RANDOM_CLUSTER"
                  }

        res = self.pio.post(uninstall_url, vc_data)
        rc = res.getcode()
        ret = res.read()

        logger.debug(uninstall_url)
        logger.debug(rc)
        logger.debug(ret)

        self.assertEqual(res.getcode(), 500)
        do_pass(self, 'test_uninstall_wrong_cluster', rc == 500 or rc == 503)

        return

if __name__ == "__main__":
    optlist, cmd_args = getopt.getopt(sys.argv[1:], '')
    args, logfolder = cmd_args
    args = [] if args=='none' else [args]
    unittest.main(argv=["pio_uninstall_negative.py"] + args)
