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
CONTAINERS_TEST_LOG_FILE = "%s/%s.logs" % (os.getcwd(), "containers_test")
formatter = logging.Formatter('%(asctime)-15s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger("containers_test")
logger.setLevel(log_level)
dlr = TimedRotatingFileHandler(CONTAINERS_TEST_LOG_FILE, when=LOG_ROTATION_TIME)
dlr.setLevel(log_level)
dlr.setFormatter(formatter)
logger.addHandler(dlr)"""

PIO_IP=APPLIANCE_IP

class TestContainers(unittest.TestCase):

    #def __init__(self, pio_ip):
    #    self.pio_ip = pio_ip
    PIO=APPLIANCE_IP

    # Helper to stop ioa containers
    def stop_ioa_containers(self):
        try:
            ret = os.system("docker stop $(docker ps -f 'name=pio_analyzer' | awk {'print$1'} | sed -n '1!p')")
        except:
            traceback.print_exc()

        return ret

    # Helper to stop pm container
    def stop_pm_container(self):
        try:
            ret = os.system("docker stop $(docker ps -f 'name=pio_manager' | awk {'print$1'} | sed -n '1!p')")
        except:
            traceback.print_exc()

        return ret

    # Helper to stop nlb container
    def stop_nlb_container(self):
        try:
            ret = os.system("docker stop $(docker ps -f 'name=nginx_load_balancer' | awk {'print$1'} | sed -n '1!p')")
        except:
            traceback.print_exc()

        return ret

    # Helper to stop all containers
    def stop_all_containers(self):
        try:
            ret = os.system("docker stop $(docker ps -f 'name=pio_analyzer' -f 'name=pio_manager' -f 'name=nginx_load_balancer' | awk {'print$1'} | sed -n '1!p')")
        except:
            traceback.print_exc()

        return ret


    # Helper to kill ioa containers
    def kill_ioa_containers(self):
        try:
            ret = os.system("docker kill $(docker ps -f 'name=pio_analyzer' | awk {'print$1'} | sed -n '1!p')")
        except:
            traceback.print_exc()

        return ret

    # Helper to kill pm container
    def kill_pm_container(self):
        try:
            ret = os.system("docker kill $(docker ps -f 'name=pio_manager' | awk {'print$1'} | sed -n '1!p')")
        except:
            traceback.print_exc()

        return ret

    # Helper to kill nlb container
    def kill_nlb_container(self):
        try:
            ret = os.system("docker kill $(docker ps -f 'name=nginx_load_balancer' | awk {'print$1'} | sed -n '1!p')")
        except:
            traceback.print_exc()

        return ret

    # Helper to kill all containers
    def kill_all_containers(self):
        try:
            ret = os.system("docker kill $(docker ps -f 'name=pio_analyzer' -f 'name=pio_manager' -f 'name=nginx_load_balancer' | awk {'print$1'} | sed -n '1!p')")
        except:
            traceback.print_exc()

        return ret

    # Helper to run docker container restart
    def run_docker_container_restart(self):
        try:
            ret = os.system("cd /root && ./docker_containers_restart.sh")
        except:
            traceback.print_exc()

        return ret

    # Helper to run pio analyzer container restart
    def run_pio_analyzer_restart(self):
        try:
            ret = os.system("cd /root && ./pio_analyzers_restart.sh")
        except:
            traceback.print_exc()

        return ret

    # This will test the killing of PM container only
    def test_1(self):
        try:
            ret = self.kill_pm_container()
            ret = self.run_docker_container_restart()
            if ret == 0:
                print("\ntest_1 SUCCESS\n")
            else:
                print("\ntest_1 FAILURE\n")
        except:
            traceback.print_exc()

        return 0

    # This will test the killing of NLB container only
    def test_2(self):
        try:
            ret = self.kill_nlb_container()
            ret = self.run_docker_container_restart()
            if ret == 0:
                print("\ntest_2 SUCCESS\n")
            else:
                print("\ntest_2 FAILURE\n")
        except:
            traceback.print_exc()

        return 0

    # This will test the killing of IOA containers only
    def test_3(self):
        try:
            ret = self.kill_ioa_containers()
            ret = self.run_docker_container_restart()
            if ret == 0:
                print("\ntest_3 SUCCESS\n")
            else:
                print("\ntest_3 FAILURE\n")
        except:
            traceback.print_exc()

        return 0

    # This will test the killing of all PIOA containers
    def test_4(self):
        try:
            ret = self.kill_all_containers()
            ret = self.run_docker_container_restart()
            if ret == 0:
                print("\ntest_4 SUCCESS\n")
            else:
                print("\ntest_4 FAILURE\n")
        except:
            traceback.print_exc()

        return 0

    # This will test the stopping of PM container only
    def test_5(self):
        try:
            ret = self.stop_pm_container()
            ret = self.run_docker_container_restart()
            if ret == 0:
                print("\ntest_5 SUCCESS\n")
            else:
                print("\ntest_5 FAILURE\n")
        except:
            traceback.print_exc()

        return 0

    # This will test the stopping of NLB container only
    def test_6(self):
        try:
            ret = self.stop_nlb_container()
            ret = self.run_docker_container_restart()
            if ret == 0:
                print("\ntest_6 SUCCESS\n")
            else:
                print("\ntest_6 FAILURE\n")
        except:
            traceback.print_exc()

        return 0

    # This will test the stopping of IOA containers only
    def test_7(self):
        try:
            ret = self.stop_ioa_containers()
            ret = self.run_docker_container_restart()
            if ret == 0:
                print("\ntest_7 SUCCESS\n")
            else:
                print("\ntest_7 FAILURE\n")
        except:
            traceback.print_exc()

        return 0

    # This will test the stopping of all PIOA containers
    def test_8(self):
        try:
            ret = self.stop_all_containers()
            ret = self.run_docker_container_restart()
            if ret == 0:
                print("\ntest_8 SUCCESS\n")
            else:
                print("\ntest_8 FAILURE\n")
        except:
            traceback.print_exc()

        return 0

    # This will test the killing of IOA containers only
    # with pio_analyzer_restart
    def test_9(self):
        try:
            ret = self.kill_ioa_containers()
            ret = self.run_docker_container_restart()
            if ret == 0:
                print("\ntest_9 SUCCESS\n")
            else:
                print("\ntest_9 FAILURE\n")
        except:
            traceback.print_exc()

        return 0


    # This will test the stopping of IOA containers only
    # with pio_analyzer_restart
    def test_10(self):
        try:
            ret = self.stop_ioa_containers()
            ret = self.run_docker_container_restart()
            if ret == 0:
                print("\ntest_10 SUCCESS\n")
            else:
                print("\ntest_10 FAILURE\n")
        except:
            traceback.print_exc()

        return 0

if __name__ == "__main__":
    obj = TestContainers(PIO_IP)
    ret = obj.test_1()
    ret = obj.test_2()
    ret = obj.test_3()
    ret = obj.test_4()
    ret = obj.test_5()
    ret = obj.test_6()
    ret = obj.test_7()
    ret = obj.test_8()
    ret = obj.test_9()
    ret = obj.test_10()
