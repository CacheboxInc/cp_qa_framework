'''
    Automated tests which would test dashboard URLs
    It is assumed that praapa is installed on cluster and VMs are monitored
    at-least for an hour
'''
from sanity_suite.conf_tcs.config import *
from sanity_suite.lib_tcs.utils import *
import getopt

"""config_file, args = get_config_file(sys.argv)
config = __import__(config_file)

for member_name in dir(config):
    if not member_name.startswith("__"):
        globals()[member_name] = getattr(config, member_name)"""


pio = PIOAppliance()

class PioBenefits(QAMixin, unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(PioBenefits, self).__init__(*args, **kwargs)
        self.pio = PIOAppliance()
        self.__class__.setting_data = None

    def setUp(self):
        sys.stdout.write("\r")
        self.pio.login()

        return

    def test_01_get_benefit(self):
        '''
            Get health of the cluster
        '''
        url = self.pio.get_url("benefits")
        values = {
                    'vcenter_ip' : VCENTER_IP,
                    'cluster_name' : VCENTER_CLUSTER,
                    'level': 0
                  }

        res = self.pio.get(url, values)
        rc = res.getcode()
        data = res.read()

        logger.debug(url)
        logger.debug(rc)
        logger.debug(data)

        self.assertEqual(res.getcode(), 200)
        do_pass(self, 'test_01_get_benefit', rc == 200 or rc == 503)

        return

    def tearDown(self):
        self.pio.logout()

        return

if __name__ == "__main__":
    optlist, cmd_args = getopt.getopt(sys.argv[1:], '')
    args, logfolder = cmd_args
    args = [] if args=='none' else [args]
    unittest.main(argv=["pio_benefit.py"] + args)
