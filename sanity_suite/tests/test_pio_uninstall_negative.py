
from sanity_suite.conf_tcs.config import *
from sanity_suite.lib_tcs.utils import *

"""config_file, args = get_config_file(sys.argv)
config = __import__(config_file)

for member_name in dir(config):
    if not member_name.startswith("__"):
        globals()[member_name] = getattr(config, member_name)"""


pio = PIOAppliance()
MOD_SETUP_ERROR = ""
VCENTER_IP= SANITY_VCENTER_IP


class PioUninstallNegative(QAMixin, unittest.TestCase):
    '''
        Validate negative scenarios for PIO uninstall
    '''

    def __init__(self, *args, **kwargs):
        super(PioUninstallNegative, self).__init__(*args, **kwargs)
        self.pio = PIOAppliance()


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
            if vc.get('vcenter_ip') == _sanity_VCENTER_IP:
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
