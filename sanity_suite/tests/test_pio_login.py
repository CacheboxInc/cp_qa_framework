'''
Negative tests for login
'''

from sanity_suite.conf_tcs.config import *
from sanity_suite.lib_tcs.utils import *
import getopt

#config_file, args = get_config_file(sys.argv)
#config = __import__(config_file)

"""for member_name in dir(config):
    if not member_name.startswith("__"):
        globals()[member_name] = getattr(config, member_name)"""


pio = PIOAppliance()
MOD_SETUP_ERROR = ""

class PioApplianceLogin(QAMixin, unittest.TestCase):

    def __init__(self, *args, **kwargs):
      
        super(PioApplianceLogin, self).__init__(*args, **kwargs)
        self.pio = PIOAppliance()

    def setUp(self):
        logger.debug("Inside setup stage")
        sys.stdout.write("\r")
        self.login_url = self.pio.get_url("api-token-auth")

    def test_01_successfull_login(self):
        '''
            Validate login operation with correct credentials and verify REST
            response
        '''
        login_cred = {'username': APP_USERNAME,
                      'password': APP_PASSWORD
        }
        res = self.pio.post(self.login_url, login_cred)
        rc = res.getcode()
        ret = res.read()

        logger.debug(self.login_url)
        logger.debug(rc)
        logger.debug(ret)      
        self.assertEqual(res.getcode(), 200)
        do_pass(self, 'test_successfull_login', rc == 200 or rc == 503)

        return

    def test_02_unsuccessfull_login(self):
        '''
            Validate login operation with incorrect credentials and verify REST
            response
        '''

        login_cred = {'username': APP_USERNAME,
                      'password': "%s_rand_string" % APP_PASSWORD
        }

        res = self.pio.post(self.login_url, login_cred)
        rc = res.getcode()
        ret = res.read()

        logger.debug(self.login_url)
        logger.debug(rc)
        logger.debug(ret)

        self.assertEqual(res.getcode(), 404)
        do_pass(self, 'test_successfull_login', rc == 404 or rc == 503)

    def tearDown(self):
        return


if __name__ == "__main__":
    optlist, cmd_args = getopt.getopt(sys.argv[1:], '')
    args, logfolder = cmd_args
    args = [] if args=='none' else [args]
    unittest.main(argv=["pio_login.py"] + args)
