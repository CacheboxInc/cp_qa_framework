import os
import sys

from sanity_suite.conf_tcs.config import *
from sanity_suite.lib_tcs.utils import *

"""config_file, args = get_config_file(sys.argv)
config = __import__(config_file)

for member_name in dir(config):
    if not member_name.startswith("__"):
        globals()[member_name] = getattr(config, member_name)"""

sys.path = ["../"] + sys.path

from rest.common.keymanager import KeyManager

class TestKeyManager(QAMixin, unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_01_positive_setkey(self):
        edek = KeyManager.set_key()
        do_pass(self, 'test_01_positive_setkey')
        dek = KeyManager.get_key(edek)
        self.assertEqual(len(dek), 64)
        do_pass(self, 'test_01_positive_getkey')

    def test_02_vaio_handler_no_key(self):
        self.pio = PIOAppliance()
        self.pio.login()
        vaio_url = self.pio.get_url("/pio/vaio")
        logger.debug("Vcenter url is {}".format(vaio_url))

        values = {
                  "vmdkuuid" : VMDKUUID,
                  "dsuuid" : DSUUID,
                  "cmd" : "get_key"
                  }

        res = self.pio.get(vaio_url, values)
        logger.debug(res)

        data = json.loads(res.read().decode('utf-8'))
        logger.debug(data)

        # not yet migrated
        self.assertEqual(res.getcode(), 503)
        self.pio.logout()
        do_pass(self, 'test_02_vaio_handler_no_key')

    def test_03_vaio_handler_no_vmdkuuid(self):
        self.pio = PIOAppliance()
        self.pio.login()
        vaio_url = self.pio.get_url("/pio/vaio")
        logger.debug("vaio url is {}".format(vaio_url))

        values = {
                  "vmdkuuid" : "%s-%s" % (VMDKUUID, "test"),
                  "dsuuid" : DSUUID,
                  "cmd" : "get_key"
                  }

        res = self.pio.get(vaio_url, values)
        logger.debug(res)

        data = json.loads(res.read().decode('utf-8'))
        logger.debug(data)

        # not yet migrated
        self.assertEqual(res.getcode(), 503)
        self.pio.logout()
        do_pass(self, 'test_03_vaio_handler_no_vmdkuuid')

    def test_04_vaio_handler_bad_request_01(self):
        self.pio = PIOAppliance()
        self.pio.login()
        vaio_url = self.pio.get_url("/pio/vaio")
        logger.debug("vaio url is {}".format(vaio_url))

        values = {
                  "vmdkuuid" : VMDKUUID,
                  "dsuuid" : DSUUID,
                  }

        res = self.pio.get(vaio_url, values)
        logger.debug(res)

        data = json.loads(res.read().decode('utf-8'))
        logger.debug(data)

        # not yet migrated
        self.assertEqual(res.getcode(), 400)
        self.pio.logout()
        do_pass(self, 'test_04_vaio_handler_bad_request_01')

    def test_05_vaio_handler_bad_request_02(self):
        self.pio = PIOAppliance()
        self.pio.login()
        vaio_url = self.pio.get_url("/pio/vaio")
        logger.debug("vaio url is {}".format(vaio_url))

        values = {
                  "cmd" : "get_key",
                  "dsuuid" : DSUUID,
                  }

        res = self.pio.get(vaio_url, values)
        logger.debug(res)

        data = json.loads(res.read().decode('utf-8'))
        logger.debug(data)

        # not yet migrated
        self.assertEqual(res.getcode(), 400)
        self.pio.logout()
        do_pass(self, 'test_05_vaio_handler_bad_request_02')

    def test_06_vaio_handler_bad_request_03(self):
        self.pio = PIOAppliance()
        self.pio.login()
        vaio_url = self.pio.get_url("/pio/vaio")
        logger.debug("vaio url is {}".format(vaio_url))

        values = {
                  "vmdkuuid" : VMDKUUID,
                  "cmd" : "get_key",
                  }

        res = self.pio.get(vaio_url, values)
        logger.debug(res)

        data = json.loads(res.read().decode('utf-8'))
        logger.debug(data)

        # not yet migrated
        self.assertEqual(res.getcode(), 400)
        self.pio.logout()
        do_pass(self, 'test_06_vaio_handler_bad_request_03')

    def test_07_vaio_handler_bad_request_04(self):
        self.pio = PIOAppliance()
        self.pio.login()
        vaio_url = self.pio.get_url("/pio/vaio")
        logger.debug("vaio url is {}".format(vaio_url))

        values = {
                  "vmdkuuid" : VMDKUUID,
                  "dsuuid" : DSUUID,
                  "cmd" : "no_command",
                  }

        res = self.pio.get(vaio_url, values)
        logger.debug(res)

        data = json.loads(res.read().decode('utf-8'))
        logger.debug(data)

        # not yet migrated
        self.assertEqual(res.getcode(), 503)
        self.pio.logout()
        do_pass(self, 'test_07_vaio_handler_bad_request_04')

if __name__ == "__main__":

    args = [] if args=='none' else [args]
    unittest.main(argv=["test_key_manager.py"])
