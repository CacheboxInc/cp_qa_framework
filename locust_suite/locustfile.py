import gevent
gevent.monkey.patch_all()

import json
import time
import random
import os
import datetime
from emulater_utils import Emulater 
from locust import HttpLocust, TaskSet, task, events
import requests
import itertools
import logging
import socket
import datetime
import uuid
from logging.handlers import RotatingFileHandler
import locust.stats
from conf_tcs.config import *

locust.stats.CSV_STATS_INTERVAL_SEC = 5 # default is 2 seconds
POST_STATS = "/stats" # Stats for POST method
GET_STATS = "/get_stats" # Stats for GET method
VMDK_COUNT = 3
APA_VMDK_COUNT_PERC = 500
PROXY_SERVER = None
#HOST = "http://192.168.2.106:32820" # Host_IP of the Applinace
HOST = "http://%s:32820"%APPLIANCE_IP # Host_IP of the Applinace
VM_NAME = ['Win_2012', 'UbAll_16']
LATENCY =  None   #In miliseconds for injecting latencies Default value should be None
PATH_PROXY_JAR = os.getcwd() + "/browsermob-proxy-2.1.4/bin/browsermob-proxy.bat" #In Case of Linux path should be /browsermob-proxy-2.1.4/bin/browsermob-proxy"
TIMEOUT = None
USER_COUNT = []
IO_LOAD_DURATION = datetime.datetime.now() # For storing the starting time of the script to push data on the IOAnalyzer


#Creating Emulater class object for instantiating single emulater object for all the Clients
emu = Emulater()
#Instantiating sinlge Proxy server for all the user
PROXIES = emu.create_proxy_server(PATH_PROXY_JAR, LATENCY)

def append_file_logger():
    '''
    For logging gerneral logs amd error messages to the log file and maitaining
    all the logs to sinle file
    '''
    #This will create log all errors and gerneral logs
    log_file = "%s/%s.log" % (os.getcwd()+LOG_LOCATION, "locust")
    root_logger = logging.getLogger()
    log_format = "%(asctime)s.%(msecs)03d000 [%(levelname)s] {0}/%(name)s : %(message)s".format(socket.gethostname())
    formatter = logging.Formatter(log_format, '%Y-%m-%d %H:%M:%S')
    file_handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=3)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)

    #For logging stats and console messages to the logfile
    console_logger = logging.getLogger("console_logger")
    #create console handler
    logging.FileHandler(filename=log_file)
    sh = logging.StreamHandler()
    sh.setLevel(logging.INFO)

    #formatter that doesn't include anything but the message
    sh.setFormatter(logging.Formatter('%(message)s'))
    console_logger.addHandler(sh)
    console_logger.propagate = False


append_file_logger()
counter = itertools.count()



class IOABehavior(TaskSet):
    global USER_COUNT
    USER_COUNT = []
    
    def on_start(self):
        """
        on_start is called only once when a Locust start before,
        any task is scheduled
        """
        self.vmdk_data = None
        self.emu = emu
        self.locust.userId = str(uuid.uuid4()) #Creating unique instance UUID
        USER_COUNT.append(self.locust.userId)
        self.current_usr = len(USER_COUNT)
        self.update_stats = False #For creating unique read and write io_stats
        self.client.verify = False #For disabling the SSL certificate validation error
        self.schedule_task(self.task1, args=None, kwargs=None, first=True)
        requests.packages.urllib3.disable_warnings() # For disabling the insecure https session warnings
        self.old_vmdk_data = self.emu.get_existing_vmdks(self.current_usr)
        self.vm_id = str(uuid.uuid4())

        if not self.old_vmdk_data:
            self.vmdk_data = self.emu.create_raw_str(VMDK_COUNT, VM_NAME, APA_VMDK_COUNT_PERC)
        else:
            self.vmdk_data = self.old_vmdk_data

        self.logger = logging.getLogger('locust-%03d' % counter.__next__())
        self.starttime = IO_LOAD_DURATION
        self.logger.info('Hatching locust')

    @task(90)
    def task1(self):
        '''
        Execute the POST calls to the nginx server with emulated vmdk data
        '''
        if self.update_stats:
            self.vmdk_data = self.emu.create_new_vmdk_data(self.vmdk_data, APA_VMDK_COUNT_PERC)

        greens = []
        data = json.dumps({ 'data' : self.vmdk_data})
        #print(data)
        response = self.client.post("%s/%s" % (POST_STATS, self.vm_id), data, name="POST_STATS", proxies=PROXIES)
        if not response.ok:
            self.logger.error(response.text) # TODO add status code, url, and reponse to the log

        self.update_stats = random.choice([True, False])

    #@task(10)
    def task2(self):
        '''
        Execute GET REST calls to the nginx for fetching the stats.
        '''
        duration_level = ["1"]
        lvl = self.emu.get_duration_lvl(self.starttime)
        duration_level.extend(lvl)
        vmdk =  random.choice(list(self.vmdk_data.items()))

        values = {
            "tag"       : vmdk[1]["tag"],
            "vmdk_id"   : vmdk[1]["vmdk_id"],
            "vm_id"     : vmdk[1]["vm_id"],
            "op"        : random.choice(["0", "1"]),
            "level"     : random.choice(duration_level)
        }
        data = json.dumps(values)
        response = self.client.get("%s%s" % (GET_STATS,self.vm_id), params=json.loads(data),name="GET_STATS")
        if not response.ok:
            self.logger.warn(response.text) #TODO add status code, url, and reponse to the log

    def on_stop(self):
        """
        on_stop is called only once when a Locust task is going to exit
        """
        #This will dump emulated vmdk data to file incase of new user.
        if not self.old_vmdk_data:
            self.old_vmdk_data = self.emu.get_existing_vmdks(self.current_usr, emul_vmdk=self.vmdk_data)
        self.vmdk_data = {}
        USER_COUNT.remove(self.locust.userId)#Removing the instance id's from the user current list


class IOAnalyzer(HttpLocust):
   task_set = IOABehavior
   min_wait = 10000
   max_wait = 10000
   host = HOST
   stop_timeout = TIMEOUT
