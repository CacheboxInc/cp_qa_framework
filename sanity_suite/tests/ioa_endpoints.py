import asyncio
import aiohttp
import copy
import traceback

from sanity_suite.conf_tcs.config import *
from sanity_suite.lib_tcs.utils import *


NLB_PORT = "32820"

#PIO_IP = '192.168.2.43'
PIO_IP = APPLIANCE_IP

IOA_SERVER_CNT = 4

GET_VMS_STATS_URL             = 'get_vms_stats'
GET_VMDK_RECOMMENDATION_URL   = 'get_vmdk_recommendation'
APA_STATS_URL                 = 'apa/stats'
GET_STATS_URL                 = 'get_stats'
GET_VM_INFO                   = 'get_vm_info'
APA_VM_STATS_URL              = 'get_vm_apa_stats'
GET_VMDK_BENEFITS_URL         = 'get_vmdk_benefit'

def get_nginx_url(end_point, values=None, with_data=False):

    if with_data:
        url    = 'http://%s:%s/%s' % (PIO_IP, NLB_PORT, end_point)
    else:
        params = urllib.parse.urlencode(values)
        url    = 'http://%s:%s/%s?%s' % (PIO_IP, NLB_PORT, end_point, params)
    return url

# chunk list
def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

# since there could be a lot of request data/ vmdkuuids,
# using post to encapsulate the same
async def get_ioa_data(session, url, data):
    async with session.post(url, json=data) as response:
        try:
            # expecting data to be of json format
            out = await response.json()
        except:
            traceback.print_exc()
            out = {"status": -1}

    return out

# data is going to be always a list of vmdk uuid
# for which information is required from the 
# IOA 
async def chunk_and_submit_ioa_request(loop, url, data, values):
    results = []

    # create AIO HTTP session using the event loop that was set
    async with aiohttp.ClientSession(loop=loop) as session:
        tasks = []
        for d in chunks(data, IOA_SERVER_CNT):
            val = copy.copy(values)
            val["vmdks"] = d
            tasks.append(get_ioa_data(session, url, val))

        # wait until all the requests have been processed
        results = await asyncio.gather(*tasks)

    return results

def submit_ioa_request(end_point, data, values={}):
    # create and set a new event loop
    url = get_nginx_url(end_point, None, True)
    asyncio.set_event_loop(asyncio.new_event_loop())
    loop = asyncio.get_event_loop()
    data = loop.run_until_complete(chunk_and_submit_ioa_request(loop, url, data, values))
    loop.close()
    return data
