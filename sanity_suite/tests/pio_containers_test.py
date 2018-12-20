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
from fabric.api import run, hosts, cd, env,settings
import time
from assertpy import assert_that
from io import BytesIO


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

    # Helper to get docker status
    def get_status(self,docker_name):
        with settings(host_string=APPLIANCE_IP, user='root', password='admin@123'):
           result = run('docker ps -a -f name=%s* --format {{.Status}}'%docker_name)

        return result

    # This will test pio-status
    def test_1(self):
        ret = self.get_status('pio_manager')
        logger.info(ret)
        assert "Up" in ret

   # This will test HA_MANAGER status
    def test_2(self):
        ret = self.get_status('HA_MANAGER')
        logger.info(ret)
        assert "Up" in ret


   # This will test Nginx-0 status
    def test_3(self):
        ret = self.get_status('Nginx-0')
        logger.info(ret)
        assert "Up" in ret


   # This will test etcd
    def test_4(self):
        ret = self.get_status('etcd')
        logger.info(ret)
        assert "Up" in ret


