import getopt

from sanity_suite.conf_tcs.config import *
from sanity_suite.tests.utils import *

"""config_file, args = get_config_file(sys.argv)
config = __import__(config_file)

for member_name in dir(config):
    if not member_name.startswith("__"):
        globals()[member_name] = getattr(config, member_name)"""

class InstallQA(QAMixin, unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(InstallQA, self).__init__(*args, **kwargs)
        self.pio = PIOAppliance()
        self.get_cluster_url = self.pio.get_url("/install/1")
        self.install_on_cluster_url = self.pio.get_url("/install/0")
        self.get_cluster_config_url = self.pio.get_url("/install/2")
        self.configure_cluster_url = self.pio.get_url("/install/1")
        self.register_plugin_url = self.pio.get_url("/install/2")

        self.uninstall_on_cluster_url = self.pio.get_url("/uninstall/0")
        self.unregister_plugin_url = self.pio.get_url("/uninstall/1")

        self.__class__.vcenter_id = None

        self.__class__.clusters = []
        self.__class__.cluster_net_config = {}
        self.__class__.cluster_name = None

    def setUp(self):
        sys.stdout.write("\r")

        if self.__class__.vcenter_id is None:
            self.vcenter = self.get_vcenters()
            if len(self.vcenter) == 0:
                logger.error("No vCenters :  Skipping all tests")
                self.skipTest('InstallQA')
                return

            self.__class__.vcenter_id = random.choice(self.vcenter)['id']

    def tearDown(self):
        self.pio.logout()

    def get_vcenters(self):
        get_vcenter_url = self.pio.get_url("/plugin")

        self.pio.login()

        res = self.pio.get(get_vcenter_url)
        ret = res.read()

        logger.debug(get_vcenter_url)
        logger.debug(ret)

        data = json.loads(ret.decode('utf-8'))
        self.assertEqual(res.getcode(), 200)

        return data['data']


    def test_01_get_clusters(self):
        #
        # test the setdata. Return code should be 0
        #
        try:
            self.pio.login()
            values = {
                        'vcenter_id': self.__class__.vcenter_id
                     }

            res = self.pio.get(self.get_cluster_url, values)
            data = res.read().decode('utf-8')

            logger.debug(self.get_cluster_url)
            logger.debug(data)

            self.assertEqual(res.getcode(), 200)
            self.__class__.clusters = data['clusters']
            
        except Exception as err:
            logger.exception(err)
            do_pass(self, 'test_01_get_clusters', 0)

        do_pass(self, 'test_01_get_clusters', 1)

    def test_02_install_on_cluster(self):
        #
        # test the setdata. Return code should be 0
        #
        try:
            self.pio.login()

            if len(self.__class__.clusters) == 0:
                logger.error("No clusters :  Skipping test_02_install_on_cluster")
                self.skipTest('test_02_install_on_cluster')
                return

            for cluster in self.__class__.clusters:
                if cluster['can_install']:
                    break

            if len(self.__class__.clusters) == 0:
                logger.error("No clusters to install :  Skipping test_02_install_on_cluster")
                self.skipTest('test_02_install_on_cluster')
                return

            self.__class__.cluster_name = cluster['cluster_name']

            values = {
                        'vcenter_id' : self.__class__.vcenter_id,
                        'cluster_name' : self.__class__.cluster_name
                     }

            res = self.pio.post(self.install_on_cluster_url, values)
            data = res.read().decode('utf-8')

            logger.debug(self.install_on_cluster_url)
            logger.debug(data)

            rc = res.getcode()
            do_pass(self, 'test_02_install_on_cluster', rc == 200 or rc == 503)
            
        except Exception as err:
            logger.exception(err)
            do_pass(self, 'test_02_install_on_cluster', 0)

        do_pass(self, 'test_02_install_on_cluster', 1)

    def test_03_get_cluster_config(self):
        try:
            self.pio.login()

            if self.__class__.cluster_name == None:
                logger.error("cluster name not set :  Skipping test_03_get_cluster_config")
                self.skipTest('test_03_get_cluster_config')
                return

            values = {
                        'vcenter_id' : self.__class__.vcenter_id,
                        'cluster_name' : self.__class__.cluster_name
                     }

            res = self.pio.get(self.get_cluster_config_url, values)
            data = res.read().decode('utf-8')

            logger.debug(self.get_cluster_url)
            logger.debug(data)
            self.assertEqual(res.getcode(), 200)
            
            self.__class__.cluster_net_config[self.__class__.cluster_name] = data['config']
        except Exception as err:
            logger.exception(err)
            do_pass(self, 'test_03_get_cluster_config', 0)

        do_pass(self, 'test_03_get_cluster_config', 1)

    def test_04_configure_cluster(self):
        try:
            self.pio.login()

            if self.__class__.cluster_name == None:
                logger.error("cluster name not set :  test_04_configure_cluster")
                self.skipTest('test_04_configure_cluster')
                return

            if len(list(self.__class__.cluster_net_config.keys())) == 0:
                logger.error("No clusters config found:  test_04_configure_cluster")
                self.skipTest('test_04_configure_cluster')
                return

            selected_config = {}

            for config in list(self.__class__.cluster_net_config.get(self.__class__.cluster_name, {}).values()):
                for host in config:
                    selected_config[host['ip']] = {'addr': host['ip'], 'fd': 'default', 'enable_fd': 'True'}

            values = {
                        'vcenter_id' : self.vcenter_id,
                        'cluster_name' : self.__class__.cluster_name,
                        'selected_config' : selected_config
                     }

            res = self.pio.post(self.configure_cluster_url, values)
            data = res.read().decode('utf-8')

            logger.debug(self.configure_cluster_url)
            logger.debug(data)

            self.assertEqual(res.getcode(), 200)
            
        except Exception as err:
            logger.exception(err)
            do_pass(self, 'test_04_configure_cluster', 0)

        do_pass(self, 'test_04_configure_cluster', 1)

    def test_05_register_plugin(self):
        try:
            self.pio.login()

            values = {
                        'vcenter_id' : self.__class__.vcenter_id
                     }

            res = self.pio.post(self.register_plugin_url, values)
            data = res.read().decode('utf-8')

            logger.debug(self.register_plugin_url)
            logger.debug(data)

            self.assertEqual(res.getcode(), 200)
            
        except Exception as err:
            logger.exception(err)
            do_pass(self, 'test_05_register_plugin', 0)

        do_pass(self, 'test_05_register_plugin', 1)

    def test_06_uninstall_on_cluster(self):
        #
        # test the setdata. Return code should be 0
        #
        try:
            self.pio.login()

            if self.__class__.cluster_name == None:
                logger.error("cluster name not set :  Skipping test_06_uninstall_on_cluster")
                self.skipTest('test_06_uninstall_on_cluster')
                return

            values = {
                        'vcenter_id' : self.__class__.vcenter_id,
                        'cluster_name' : self.__class__.cluster_name
                     }

            res = self.pio.post(self.uninstall_on_cluster_url, values)
            data = res.read().decode('utf-8')

            logger.debug(self.uninstall_on_cluster_url)
            logger.debug(data)
            
            rc = res.getcode()
            do_pass(self, 'test_06_uninstall_on_cluster', rc == 200 or rc == 503)
           
        except Exception as err:
            logger.exception(err)
            do_pass(self, 'test_06_uninstall_on_cluster', 0)

        do_pass(self, 'test_06_uninstall_on_cluster', 1)

    def test_07_unregister_plugin(self):
        try:
            self.pio.login()

            values = {
                        'vcenter_id' : self.__class__.vcenter_id
                     }

            res = self.pio.post(self.unregister_plugin_url, values)
            data = res.read().decode('utf-8')

            logger.debug(self.unregister_plugin_url)
            logger.debug(data)

            self.assertEqual(res.getcode(), 200)
           
        except Exception as err:
            logger.exception(err)
            do_pass(self, 'test_07_unregister_plugin', 0)

        do_pass(self, 'test_07_unregister_plugin', 1)

if __name__ == "__main__":
    optlist, cmd_args = getopt.getopt(sys.argv[1:], '')
    args, logfolder = cmd_args
    args = [] if args=='none' else [args]
    unittest.main(argv=["pio_install.py"] + args)
