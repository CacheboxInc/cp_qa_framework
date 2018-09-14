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
import logging
from sanity_suite.conf_tcs.config import *
from sanity_suite.lib_tcs.utils import *

from io import BytesIO

"""from logging.handlers import TimedRotatingFileHandler
log_level = logging.ERROR

LOG_ROTATION_TIME = 'MIDNIGHT'
TEST_LOGGING_FILE = "%s/%s.logs" % (os.getcwd(), "pio_log")
formatter = logging.Formatter('%(asctime)-15s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger("pio_log")
logger.setLevel(log_level)
dlr = TimedRotatingFileHandler(TEST_LOGGING_FILE, when=LOG_ROTATION_TIME)
dlr.setLevel(log_level)
dlr.setFormatter(formatter)
logger.addHandler(dlr)"""

PIO_IP = APPLIANCE_IP

class TestPIOLog(unittest.TestCase):

    #def __init__(self, pio_ip):
    #    self.pio_ip = pio_ip

    # Helper to run main log collection command
    PIO_IP = APPLIANCE_IP
    def main_log_cmd(self):
        try:
            ret = os.system("cd /root && python3.5 collect_pio_logs.py")
        except:
            traceback.print_exc()

        return ret

    # Helper to run daily log collection command
    def daily_log_cmd(self):
        try:
            ret = os.system("cd /root && python3.5 collect_logs.py")
        except:
            traceback.print_exc()

        return ret

    # This will test the main log collection command on the Host VM
    def test_1(self):
        try:
            ret = self.main_log_cmd()
            logger.info("\n Response got while reading the logs :%s "%(ret))
            assert ret == 0
        except:
            traceback.print_exc()
            assert False

        return 0

    # This will test the daily log command on the Host VM
    def test_2(self):
        try:
            ret = self.daily_log_cmd()
            logger.info("\n Response got while reading the logs :%s "%(ret))
            assert ret == 0
        except:
            traceback.print_exc()
            assert False

        return 0

if __name__ == "__main__":
    obj = TestPIOLog(PIO_IP)
    ret = obj.test_1()
    ret = obj.test_2()
