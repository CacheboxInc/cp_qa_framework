from sanity_suite.conf_tcs.config import *
from sanity_suite.lib_tcs.utils import *

import getopt

"""config_file, args = get_config_file(sys.argv)
config = __import__(config_file)

for member_name in dir(config):
    if not member_name.startswith("__"):
        globals()[member_name] = getattr(config, member_name)"""


class PioInstallNegative(QAMixin, unittest.TestCase):
    '''
        Validate negative scenarios for PIO install
    '''

    setup_error = ""
    vc_id = None

    def __init__(self, *args, **kwargs):
        super(PioInstallNegative, self).__init__(*args, **kwargs)
        self.pio = PIOAppliance()

    def setUp(self):
        sys.stdout.write("\r")
        self.pio.login()

        # Add vCenter
        vc_cred = { 'username': VCENTER_USERNAME,
                    'ip': VCENTER_IP,
                    'password': VCENTER_PASSWORD,
                    'force_add': 0}

        ret = self.pio.add_vcenter(vc_cred)
        if ret is False:
            self.setup_error = "Failed to add vCenter"

        return

    def tearDown(self):
        # Delete vCenter
        if self.vc_id is not None:
            ret = self.pio.delete_vcenter({'force_delete': 0, 'id': self.vc_id})
            if ret is False:
                logger.error("Failed to delete vCenter in tearDown")

        self.pio.logout()

    def test_install_wrong_cluster(self):
        '''
            Try to install vib from cluster on which PIO is not installed or
            cluster is not present, it is expected that REST call should fail
        '''

        if self.setup_error:
            raise Exception("Setup failed: %s" % self.setup_error)

        # Get vCenters
        vcenter_list = self.pio.get_vcenters()

        if not vcenter_list:
            logger.error("Failed to get vCenter list")
            return

        for vc in vcenter_list:
            if vc.get('vcenter_ip') == VCENTER_IP:
                self.vc_id = vc.get('id')
                break

        if self.vc_id is None:
            logger.error("Failed to get vCenter ID")
            return

        # Uninstall vib
        install_url = self.pio.get_url("/install/0")

        vc_data = { 'vcenter_id': vc.get('id'),
                    'cluster_name': "RANDOM_CLUSTER"
                  }

        logger.debug("\n vc_data = ", vc_data)

        res = self.pio.post(install_url, vc_data)
        rc = res.getcode()
        ret = res.read()

        logger.debug(install_url)
        logger.debug(rc)
        logger.debug(res)

        self.assertEqual(res.getcode(), 500)
        do_pass(self, 'test_install_wrong_cluster', rc == 500 or rc == 503)

        return

    '''
    def test_install_already_installed(self):
            Try to install vib on a cluster on which vib has been already
            un-installed
        pass
    '''

if __name__ == "__main__":
    optlist, cmd_args = getopt.getopt(sys.argv[1:], '')
    args, logfolder = cmd_args
    args = [] if args=='none' else [args]
    unittest.main(argv=["pio_install_negative.py"] + args)
