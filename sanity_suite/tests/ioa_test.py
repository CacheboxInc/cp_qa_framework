import requests
import json
import sys
import os
import django
import random
from sanity_suite.conf_tcs.config import *
from sanity_suite.lib_tcs.utils import *

sys.path = ["../"] + sys.path
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "appliance.settings")

django.setup()

from helpers.db_operations import *
from supervisor.utils.config import *

vm_uuid   = "testDSUUID3"
tag       = "0"
op        = "0"
level     = "0"

class IOATest:

    def get(self, vn_uuid, tag, op, level):
        opr = DBOpr(component=self.vm_uuid)
        details = opr.get_vm_disks()
        vm_data = {}
        vm_data[details["component"]] = {}

        for disk in details["disks"]:
            vmdk_uuid = disk["uuid"]
            values = {
                       "vm_id"   : self.vm_uuid,
                       "tag"     : self.tag,
                       "vmdk_id" : vmdk_uuid,
                       "op"      : op,
                       "level"   : level
            }
            end_point = "get_stats"
            url = get_nginx_url(end_point, values)
            r = requests.get(url)
            vm_data[details["component"]][disk["name"]] = json.loads(r.text)

        return vm_data

obj = IOATest()
dest = obj.get(vm_uuid , tag, op, level)
print(dest)
