'''
    Automated tests which would test dashboard URLs
    It is assumed that praapa is installed on cluster and VMs are monitored
    at-least for an hour
'''
from utils import *
import getopt

config_file, args = get_config_file(sys.argv)
config = __import__(config_file)

for member_name in dir(config):
    if not member_name.startswith("__"):
        globals()[member_name] = getattr(config, member_name)


pio = PIOAppliance()

class PioDashboardOperations(QAMixin, unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(PioDashboardOperations, self).__init__(*args, **kwargs)
        self.pio = PIOAppliance()
        self.__class__.setting_data = None

    def setUp(self):
        sys.stdout.write("\r")
        self.pio.login()

        return

    def test_01_get_health(self):
        '''
            Get health of the cluster
        '''
        get_health_url = self.pio.get_url("dashboard/health/0")

        res = self.pio.get(get_health_url)
        rc = res.getcode()
        data = res.read()

        logger.debug(get_health_url)
        logger.debug(rc)
        logger.debug(data)

        self.assertEqual(res.getcode(), 200)
        do_pass(self, 'test_01_get_health', rc == 200 or rc == 503)

        return

    def test_02_get_storage(self):
        '''
            Get storage info
        '''

        get_storage_url = self.pio.get_url("dashboard/storage")

        res = self.pio.get(get_storage_url)
        rc = res.getcode()
        data = res.read()


        logger.debug(get_storage_url)
        logger.debug(rc)
        logger.debug(data)

        self.assertEqual(res.getcode(), 200)

        do_pass(self, 'test_02_get_storage', rc == 200 or rc == 503)
        return

    def test_03_get_locality(self):
        '''
            Get locality info
        '''

        get_locality_url = self.pio.get_url("dashboard/locality/0")

        res = self.pio.get(get_locality_url)
        rc = res.getcode()
        data = res.read()

        logger.debug(get_locality_url)
        logger.debug(rc)
        logger.debug(data)

        self.assertEqual(res.getcode(), 200)

        do_pass(self, 'test_03_get_locality', rc == 200 or rc == 503)
        return

    def test_04_get_dataset(self):
        '''
            Get dataset
        '''

        get_dataset_url = self.pio.get_url("dashboard/dataset/0")

        res = self.pio.get(get_dataset_url)
        rc = res.getcode()
        data = res.read()

        logger.debug(get_dataset_url)
        logger.debug(rc)
        logger.debug(data)

        self.assertEqual(res.getcode(), 200)

        do_pass(self, 'test_04_get_dataset', rc == 200 or rc == 503)

        return

    def test_05_get_setting(self):
        '''
            Get settings information
        '''

        get_settings_url = self.pio.get_url("settings")

        res = self.pio.get(get_settings_url)
        rc = res.getcode()
        data = res.read().decode('utf-8')
        
        logger.debug(get_settings_url)
        logger.debug(rc)
        logger.debug(data)

        self.assertEqual(res.getcode(), 200)
        do_pass(self, 'test_05_get_setting', rc == 200 or rc == 503)

        # Need this info while executing set setting info test
        self.__class__.setting_data = json.loads(data)

        return

    def test_06_set_setting(self):
        '''
            Set setting information (threasholds)
        '''

        if self.__class__.setting_data is None:
            self.skipTest("test_06_set_setting")
            return

        set_settings_url = self.pio.get_url("settings")

        for threshold in self.__class__.setting_data['data'][1]:
            if threshold['id'] == "outstanding_io_high_threshold":
                threshold['value'] = 2000
                break

        res = self.pio.post(set_settings_url, self.__class__.setting_data)
        rc = res.getcode()
        data = res.read()

        logger.debug(set_settings_url)
        logger.debug(rc)
        logger.debug(data)

        self.assertEqual(res.getcode(), 201)
        do_pass(self, 'test_06_set_setting', rc == 201 or rc == 503)

        return

    def test_07_download_logs(self):
        '''
            Download debug logs (zip)
        '''

        get_logs_url = self.pio.get_url("getlogs")

        res = self.pio.get(get_logs_url)
        rc = res.getcode()
        data = res.read()

        logger.debug(dir(res))
        logger.debug(get_logs_url)
        logger.debug(rc)

        self.assertEqual(res.getcode(), 200)

        with open("pio_logs.zip", "w") as fd:
            fd.write(str(data))

        do_pass(self, 'test_04_get_dataset', rc == 200 or rc == 503)

        return

    def tearDown(self):
        self.pio.logout()

        return

if __name__ == "__main__":
    optlist, cmd_args = getopt.getopt(sys.argv[1:], '')
    args, logfolder = cmd_args
    args = [] if args=='none' else [args]
    unittest.main(argv=["pio_dashboard_operations.py"] + args)