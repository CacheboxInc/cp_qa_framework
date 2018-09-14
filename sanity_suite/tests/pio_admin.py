#
# Copyright 2018 PrimaryIO, Pvt. Ltd. All rights reserved.
# This software is property of PrimaryIO, Pvt. Ltd. and
# contains trade secrets, confidential & proprietary
# information. Use, disclosure or copying this without
# explicit written permission from PrimaryIO, Pvt. Ltd.
# is prohibited.
#
# Author: PrimaryIO, Pvt. Ltd. (sales@primaryio.com)
#

import os
import sys
import traceback
from sanity_suite.conf_tcs.config import *
from sanity_suite.lib_tcs.utils import *

from io import BytesIO

"""from logging.handlers import TimedRotatingFileHandler
log_level = logging.ERROR

LOG_ROTATION_TIME = 'MIDNIGHT'
PIOADMIN_TEST_LOG_FILE = "%s/%s.logs" % (os.getcwd(), "pioadmin")
formatter = logging.Formatter('%(asctime)-15s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger("pioadmin")
logger.setLevel(log_level)
dlr = TimedRotatingFileHandler(PIOADMIN_TEST_LOG_FILE, when=LOG_ROTATION_TIME)
dlr.setLevel(log_level)
dlr.setFormatter(formatter)
logger.addHandler(dlr)"""

VC_IP       = VCENTER_IP
VC_USERNAME = VCENTER_USERNAME
VC_PASSWORD = VCENTER_PASSWORD

class TestPIOAdmin():

    def __init__(self, vc_ip, vc_username, vc_password):
        self.vc_ip = vc_ip
        self.vc_username = vc_username
        self.vc_password = vc_password

    # Helper to run base pio_admin command
    def base_cmd(self):
        try:
            ret = os.system("pio_admin")
        except:
            traceback.print_exc()

        return ret

    # Helper to run pio_admin help command
    def help_cmd(self):
        try:
            ret = os.system("pio_admin --help")
        except:
            traceback.print_exc()

        return ret

    # This will test the base pio_admin command on the Host VM
    def test_1(self):
        try:
            ret = self.base_cmd()
            if ret == 512:
                print("\ntest_1 SUCCESS\n")
            elif ret == 32512:
                print("\ntest_1 FAILURE\n")
        except:
            traceback.print_exc()

        return 0

    # This will test the pio_admin help command on the Host VM
    def test_2(self):
        try:
            ret = self.help_cmd()
            if ret == 0:
                print("\ntest_2 SUCCESS\n")
            elif ret == 32512:
                print("\ntest_2 FAILURE\n")
        except:
            traceback.print_exc()

        return 0

if __name__ == "__main__":
    obj = TestPIOAdmin(VC_IP, VC_USERNAME, VC_PASSWORD)
    ret = obj.test_1()
    ret = obj.test_2()
