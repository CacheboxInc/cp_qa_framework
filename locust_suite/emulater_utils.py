import random
import json
import time
import itertools
import logging
import os
import sys
import datetime
import pickle
import shutil
from math import ceil
from collections import OrderedDict
from browsermobproxy import Server

TOTAL_APA_VMDK_PER_VM = 3
TOTAL_VMDK_PER_VM = 3

#Adding apa_stats to the emulated VMDK data
apa_stats = {
			 'write_size_hist': [0, 0, 0, 1118, 219842, 131697, 1340, 32, 0, 10, 10, 20],
			 'read_populate_latency': [0, 0, 0, 11239, 54673, 23955, 13893, 9229, 6409, 4762, 3871, 3434, 2724, 21399],
			 'thit_pct': 87,
			 'dio_read_latency': [0, 0, 301, 9849, 26352, 35007, 28071, 18571, 12215, 8715, 6483, 4283, 3260, 88377],
			 'dio_diskwrites': 305877,
			 'used_pct': 7,
			 'cc3_read_latency': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
			 'format_partial': 0,
			 'ssd_readmiss': 155588,
			 'invalidate_requests': 0,
			 'format_unknown': 0,
			 'disk_read_bytes': 637288448,
			 'write_partial': 0,
			 'cc1_network_write_latency': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
			 'cc1_network_read_latency': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
			 'cc3_network_write_latency': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
			 'write_miss': 0,
			 'flush_calls': 57309,
			 'active_ios': 0,
			 'dio_rpcwrite_latency': [0, 0, 0, 8260, 51184, 30222, 19372, 16049, 15414, 16139, 16034, 15565, 13960, 103678],
			 'dio_reads': 241484,
			 'throttle_calls': 0,
			 'dio_diskread_latency': [0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 1, 2, 69024],
			 'hdd_reads': 155588,
			 'hdd_writes': 0,
			 'read_populate': 155588,
			 'dirty_pct': 3,
			 'read_nios': 631268,
			 'dirty_blocks': 148395,
			 'whit_pct': 100,
			 'pending_ios': 0,
			 'cc1_write_latency': [0, 6371, 47632, 147893, 157063, 101671, 77302, 58896, 42837, 31034, 22987, 17197, 12683, 66076],
			 'format_error': 0,
			 'write_nios': 634054,
			 'ssd_reads': 804541,
			 'read_cached': 475680,
			 'failed': 0,
			 'blocks_flushed': 328861,
			 'cc2_network_write_latency': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
			 'cc3_network_read_latency': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
			 'read_size_hist': [0, 0, 0, 0, 158066, 83418, 0, 0, 0, 0, 0, 0],
			 'hdd_read_latency': [0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 5, 2, 6, 155570],
			 'read_populates': 155588,
			 'cc3_write_latency': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
			 'rhit_pct': 75,
			 'dio_diskreads': 69030,
			 'ssd_writes': 789642,
			 'write_populate': 0,
			 'disk_write_bytes': 0,
			 'read_miss': 155588,
			 'read_requests': 236850,
			 'dio_diskwrite_latency': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
			 'write_bytes': 3234373632,
			 'ssd_readmiss_latency': [36282, 15946, 13388, 38632, 27184, 9435, 4498, 2557, 1580, 1210, 795, 667, 519, 2895],
			 'dio_writes': 354069,
			 'ssd_write_latency': [0, 0, 0, 18992, 127860, 78524, 51186, 42323, 39553, 40582, 39927, 38904, 35324, 276467],
			 'cache_size': 4354956,
			 'dio_rpcread_latency': [11357, 5071, 8870, 73903, 76997, 58506, 35301, 21675, 13891, 10038, 7393, 5154, 3946, 17327],
			 'cc3_ip': '',
			 'format_complete': 1,
			 'disk_reads': 155588,
			 'read_nfailed': 0,
			 'cc1_read_latency': [74756, 10291, 64186, 220419, 240035, 147247, 71441, 38307, 23694, 15509, 11848, 8351, 5872, 28173],
			 'cc2_ip': '',
			 'dio_rpcreads': 349429,
			 'cc2_network_read_latency': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
			 'write_cached': 634054,
			 'read_ninval': 0,
			 'dio_rpcwrites': 305877,
			 'cc1_ip': '192.168.2.134',
			 'disk_writes': 0,
			 'dio_write_latency': [10, 14, 18, 2155, 47460, 42935, 29802, 28832, 24127, 20627, 17812, 16375, 14415, 109487],
			 'read_bytes': 3295399936,
			 'blocks_evicted': 0,
			 'cc2_read_latency': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
			 'cc2_write_latency': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
			 'write_nfailed': 0,
			 'ssd_read_latency': [0, 128, 13923, 169208, 192430, 140820, 85256, 54426, 35773, 25981, 19349, 13486, 10157, 43604],
			 'read_partial': 0,
			 'write_ninval': 0,
			 'format_in_progress': False,
			 'write_requests': 236847,
			 'hdd_write_latency': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
		}

class Emulater(object):
    '''
    Class defining a set of methods to emulate the vmdk with IO traces
    '''
    def __init__(self, dirname="vmdk_data"):
        self.dir_name = dirname
        self._create_dir(self.dir_name)

    def _create_dir(self, dir_name, delete=True):
        dir_path = os.path.join(os.getcwd(), self.dir_name)
        if delete and os.path.exists(dir_path):
            #os.rmdir(dir_path)
            shutil.rmtree(dir_path)
            time.sleep(1)

        if not os.path.exists(dir_path):
            os.mkdir(dir_path)


    def emulate_vmdk(self, vmdk_rw_str, vmdk_id, VM_NAME, with_apa_stats):
        '''
        This method emulate the vmdk dictionary format
        '''
        read_iostats = self.emulate_iotraces()
        write_iostats = self.emulate_iotraces()
        vmdk_rw_str["tag"] = 1520848915824
        vmdk_rw_str["vmdk_id"] = "{0}_6000C2960dc48023d865148fe29fd46f_{1}".format(vmdk_id, VM_NAME)
        vmdk_rw_str["ds_uuid"] = "599f3f98-0a0b3022-5a5b-0050568be972g{}".format(VM_NAME)
        vmdk_rw_str["vm_id"] =  "192168188_421585f13fb7cd3480a2f1461b1a3a44_{}".format(VM_NAME)
        vmdk_rw_str["read_iostats"] = read_iostats
        vmdk_rw_str["write_iostats"] = write_iostats
        vmdk_rw_str["with_apa"] = with_apa_stats

        return vmdk_rw_str

    def create_raw_str(self, max_vmdk, VM_NAME_PATT, apa_vmkd_perc):
        '''
        This method created new emulated vmdk with vmdk_id, vm_uuid and other key components
        when the instance of the new user is emulated
        '''
        self.vmdk_dict = OrderedDict()
        vm_ls_len = len(VM_NAME_PATT)
        count = 0
        if vm_ls_len > max_vmdk:
            max_vmdk += max_vmdk
        max_vmdk = TOTAL_VMDK_PER_VM
        apa_with_vmdk = TOTAL_APA_VMDK_PER_VM

        for vm_name in VM_NAME_PATT[1:]:
            with_apa_stats = True
            for i in range(0, max_vmdk):
                vmdk_rw_str = OrderedDict()
                vmdk_id = ''.join([random.choice('0123456789') for k in range(10)])
                if i > apa_with_vmdk:
                    with_apa_stats = False
                vmdk  = self.emulate_vmdk(vmdk_rw_str, vmdk_id, vm_name, with_apa_stats)
                self.vmdk_dict[str(count)] = vmdk
                count += 1

        return self.vmdk_dict

    def emulate_iotraces(self):
        '''
        Dictionary Format for read_iostats and write_iostats
        stats = {
            'l1_stats': {
                    'num_ios' : ,
                    'sum_bw' :,
                    'sum_qd' :,
                    'blocksize_hist': [],
                    'latency_hist': [],
                    'l1_unique': 4906,
                    'l1_sdq' :,
                    'l1_mrc' :,
                        },
            'l2_stats': {'l2_unique': 0, 'l2_sdq': 0, 'l2_mrc'}#Same as l1_stats dictionary key and value
        }
        '''
        stats_max_data = ''
        blk_sz_histogram_list = [512, 4096, 8192]
        lat_histogram = [1,2,3,4,5,10,15,20,40,50,100,200]
        stats_max = {}
        stats_min = {}
        stats_min['num_ios'] = random.choice(range(0,100))
        stats_min['sum_bw'] = random.choice(range(0,100))
        stats_min['sum_qd'] = random.choice(range(0,100))
        stats_min['blocksize_hist'] = [random.choice(blk_sz_histogram_list) for i in range(12)]
        stats_min['latency_hist'] = [random.choice(lat_histogram) for i in range(12)]
        stats_min['l1_unique'] = random.choice(blk_sz_histogram_list)
        stats_min['l1_sdq'] = random.choice(range(0,100))
        stats_min['l1_mrc'] = [random.choice(range(100)) for i in range(60)]
        
        #Storing the emulated IO traces in the stats_max dictonary
        stats_max['l1_stats'] = stats_min
        stats_max['l2_stats'] = {'l2_unique': random.choice(blk_sz_histogram_list),
                                 'l2_sdq': random.choice(range(0,100)), 
                                 'l2_mrc': [random.choice(range(100)) for i in range(60)]
                                }
        stats_max_data = json.dumps(stats_max)

        return stats_max_data
    
    def creat_new_vmdk_data(self, old_vmdk, apa_vmkd_perc):
        '''
        This method update the already created vmdk with new Read and Write IO stats values
        '''
        new_vmdk_data = OrderedDict()
        i = 0
        j = 0
        vmdk_with_apa = TOTAL_APA_VMDK_PER_VM # ceil(len(old_vmdk.items()) * (apa_vmkd_perc/ 100))

        for key, vmdk_d in old_vmdk.items():
            new_vmdk = OrderedDict()
            new_vmdk["tag"] = vmdk_d["tag"]
            new_vmdk["vmdk_id"] = vmdk_d["vmdk_id"]
            new_vmdk["ds_uuid"] = vmdk_d["ds_uuid"]
            new_vmdk["vm_id"] = vmdk_d["vm_id"]
            new_vmdk["read_iostats"] = self.emulate_iotraces()
            new_vmdk["write_iostats"] = self.emulate_iotraces()

            '''
            if i < vmdk_with_apa:
                j += 1
                new_vmdk["apa_stats"] = json.dumps(apa_stats)
            '''

            i += 1 
            new_vmdk_data[key] = new_vmdk

        return new_vmdk_data
            
    
    def create_proxy_server(self, PATH, LATENCY):
        '''This method emulate a proxy server through which all the requests
           are served
        '''
        if LATENCY:
            print("Simulating the ProxyServer")
            latency = {
                 'downstream_kbps' : 20000,
                 'upstream_kbps' : 20000,
                 'latency' : LATENCY
            }
            creat_proxy_dict = {
                 'trustAllServers' : True
            }

            server = Server(PATH)
            server.start()
            time.sleep(2)
            proxy = server.create_proxy(creat_proxy_dict)
            proxy.limits(options=latency)
            proxy_server='{host}:{port}'.format(host='localhost', port=proxy.port)
            print("successfully started proxy server @: %s"%(proxy_server))
            proxy = {
                      "http": proxy_server,
                      "https": proxy_server
            }
            return proxy
        else:
            return None
        
    def get_duration_lvl(self, start_time):
        '''
        This will get total duration of run so far and set the value of the level list
        min_10: 1
        hr_2: 2
        day_1: 3
        day_12: 4
        '''
        level_set = set()
        current_time = datetime.datetime.now()
        total_duration = str(current_time - start_time)
        total_duration = total_duration.split(":")
        #print(total_duration)
        #input('wait')
        if total_duration[1] and len(list(level_set)) < 4:
            if len(list(level_set)) == 3 and int(total_duration[0]) >= 288:
                level_set.add("4")
            if len(list(level_set)) == 2 and int(total_duration[0]) >= 24:
                level_set.add("3")
            if int(total_duration[0]) >= 2:
                level_set.add("2")
        return(list(level_set))

    def get_existing_vmdks(self, usr_id, emul_vmdk=None):
        '''
        This method creates or pull emulated data.
        In case of new user it will dump the data to the file
        and Existing user data will be pulled from the file
        '''
        vmdk_data = None
        return vmdk_data
        vmdk_name = str(usr_id) + "_vmdk.db"
        dir_path = os.path.join(os.getcwd(), self.dir_name)
        vmdk_files =  os.listdir(dir_path)
        vmdk_path = os.path.join(dir_path, vmdk_name)

        if vmdk_name in vmdk_files:
            with open(vmdk_path, 'rb') as vmdk:
                vmdk_data = pickle.load(vmdk)
        if emul_vmdk:
            with open(vmdk_path, 'wb') as vmdk:
                pickle.dump(emul_vmdk, vmdk, pickle.HIGHEST_PROTOCOL)
        return vmdk_data

if __name__ == "__main__":
    emulate = Emulater()
    vmdk_dict = emulate.create_raw_str(1, ['win', 'lin'])
    data = json.dumps(vmdk_dict)
    print(data)
