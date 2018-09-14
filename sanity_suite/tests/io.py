import pycurl
import json
import time
import threading
import sys
import threading
import copy
from sanity_suite.conf_tcs.config import *
from sanity_suite.lib_tcs.utils import *


URL = "http://192.168.4.40:8080"
STATS = "/stats"


class IOTest:
    def __init__(self, url):
        self.url = url

    def push(self, param, data):
        c = pycurl.Curl()
        c.setopt(c.URL, "%s%s?%s" % (self.url, STATS, param))
        c.setopt(pycurl.HTTPHEADER, ['Accept: application/json'])
        c.setopt(pycurl.POST, 1)
        c.setopt(pycurl.POSTFIELDS, data)
        c.setopt(pycurl.VERBOSE, 1)
        c.setopt(pycurl.CONNECTTIMEOUT, 3)
        c.setopt(pycurl.SSL_VERIFYPEER, 0)
        c.setopt(pycurl.SSL_VERIFYHOST, 0)
        c.perform()
        c.close()




if __name__ == "__main__":
    l, VMDK = int(sys.argv[1]), int(sys.argv[2])
    obj = IOTest(URL)
    testVMDKUUID = []
    testDSUUID = []
    testVMID = []
    
    for i in range(l, VMDK):
        testVMDKUUID.append("testVMDKUUID%d" % i)

    for i in range(l, VMDK):
        testDSUUID.append("testDSUUID%d" % i)

    for i in range(l, VMDK):
        testVMID.append("testVMID%d" % i)

    i = copy.copy(l)
    p = 0
    threads = []
    while(1):
        if i == VMDK :
            time.sleep(10)
            p = 0
            i = l
        
        param = "vm_id=%s&tag=0&vmdk_id=%s&op=0&level=0" % (testVMID[p], testVMDKUUID[p])
        d = {"vmdk_uuid": testVMDKUUID[p], "ds_uuid": testDSUUID[p], "read_iostats": "{\"l1_stats\": {\"num_ios\": 0, \"sum_bw\": 0, \"sum_qd\": 0, \"blocksize_hist\": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], \"latency_hist\": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], \"l1_unique\": 0, \"l1_sdq\": 0, \"l1_mrc\": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}, \"l2_stats\": {}}", "write_iostats": "{\"l1_stats\": {\"num_ios\": 0, \"sum_bw\": 0, \"sum_qd\": 0, \"blocksize_hist\": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], \"latency_hist\": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], \"l1_unique\": 0, \"l1_sdq\": 0, \"l1_mrc\": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}, \"l2_stats\": {}}"}
        data = json.dumps(d)
        t1 = threading.Thread(target=obj.push, args=(param, data))
        threads.append(t1)
        t1.start()
        i = i + 1
        p = p + 1

