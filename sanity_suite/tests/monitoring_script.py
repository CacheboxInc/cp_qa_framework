import datetime
import math
import random
import time
from sanity_suite.conf_tcs.config import *
from sanity_suite.lib_tcs.utils import *

PROFILED = 0
MONITORING = 1

TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"
COMPARE_FORMAT = "%Y-%m-%dT%H:%M:%S"

# priority_esx : {"vcenter ip" : [list of clusters name in lower
#                                  for which esx monitoring should be 
#                                  prioritized], ..}
all_clusters = {}

num_clusters = 37
num_host_per_cluster = 13
total_vmdks = 13

start_time = datetime.datetime.now()

PRIORITY_CLUSTER = {'cls1', 'cls2'}

# 20 % of max esx to monitor will always be from
# PRIORITY_CLUSTER
PROIRITY_PERC = 20

START_MONITORING_FOR_ALL = 2 * 60 # 2 min

# Maximum number of ESX to monitor at a time
MAX_ESX_TO_MONITOR = 40

# Maximum number of VMDK to monitor at atime
MAX_VMDK_TO_MONITOR = 1000

# Cycle to cycle hosts being monitored
MONITOR_TRANSITION_INTERVAL = 10 # every 10 seconds

TIME_SLOTS = []

# time_slots from T1 - T6 
for i in range(6):
    TIME_SLOTS.append("T%d" % (i + 1))

L1_WEEKDAY_SLOT = 'weekday'
L1_WEEKEND_SLOT = 'weekend'

class ManagedObject(object):

    def __init__(self, a, i):
        self.ip = "192.168.%s.%s" % (a, i)
        self.name = self.ip
        self.private = {'total_vmdks' : total_vmdks}
        self.state = PROFILED
        self.created = datetime.datetime.now()

    def save(self):
        pass

for a in range(num_clusters):
    all_clusters['cls%s' % a] = []
    for i in range(num_host_per_cluster):
        all_clusters['cls%s' % a].append(ManagedObject(a, i))

vCenter = ManagedObject(200, 200)

def get_current_time_slot(now, monitor_transition_interval):
    """
    Based on current time returns a list
    t[0] = weekend/ weekday
    t[1] = time_slot
    """
    l1_slot = L1_WEEKDAY_SLOT
    if now.isoweekday() > 5:
        l1_slot = L1_WEEKEND_SLOT

    interval =  int((now.second/ (monitor_transition_interval)) + 1) % (len(TIME_SLOTS) + 1)

    if monitor_transition_interval >= 3600:
        interval =  int((now.hour/ (monitor_transition_interval/ 3600)) + 1) % (len(TIME_SLOTS) + 1)
    elif monitor_transition_interval < 3600 and monitor_transition_interval >= 60:
        interval =  int((now.minute/ (monitor_transition_interval/ 60)) + 1) % (len(TIME_SLOTS) + 1)

    l2_slot = 'T%d' % interval

    assert(l2_slot in TIME_SLOTS)

    return [l1_slot, l2_slot]

def schedule_esx_for_monitoring(now, priority_esx_list, non_priority_esx_list,
                                current_time_slot, vcenter_monitor_cycle_start,
                                current_monitoring_index, monitor_transition_interval,
                                max_vmdk_to_monitor, max_priority_esx_to_monitor, max_esx_to_monitor):
    monitored_hosts = []
    hosts_to_monitor = []

    try:
        hosts_to_monitor = []
        hosts_not_to_monitor = {
                'non_priority' : [],
                'priority' : []
                }

        total_vmdk_to_monitor = 0
        priority_esx_added = 0
        non_priority_esx_added = 0

        print("sorted hosts %s" % [h.name for h in non_priority_esx_list])

        # get the hosts which were currently being monitored
        monitored_hosts = list(filter(lambda x: x.state == MONITORING, priority_esx_list + non_priority_esx_list))

        print("hosts being monitored = %s" % len(monitored_hosts))

        # get the time when the last host was monitored
        last_monitoring_time = None

        if len(monitored_hosts) > 0:
            last_monitoring_time = monitored_hosts[-1].private.get('monitoring_start')
            # continue monitoring if hosts have not been monitored for
            # required time
            if last_monitoring_time is None:
                last_monitoring_time = now - datetime.timedelta(seconds = monitor_transition_interval)
                last_monitoring_time = last_monitoring_time.strftime(TIME_FORMAT)
                for h in monitored_hosts:
                    h.private['monitoring_start'] = last_monitoring_time
                    h.save()

            if last_monitoring_time is not None:
                last_monitoring_time = datetime.datetime.strptime(last_monitoring_time, TIME_FORMAT)
                if last_monitoring_time + datetime.timedelta(seconds = monitor_transition_interval) >= now:
                    return hosts_to_monitor, monitored_hosts

        # for host in prioirty esx list and under non_priority_esx_list
        for host in priority_esx_list + non_priority_esx_list[current_monitoring_index:] + \
                    non_priority_esx_list[:current_monitoring_index]:

            print("%s -%s, %s - %s" % (host.name, host.private.get('total_vmdks', 0), \
                    host.private.get('monitoring_start'), host.private.get(current_time_slot[0])))

            host_level = 'non_priority'
            if host in priority_esx_list:
                host_level = 'priority'

            if host.private.get(current_time_slot[0]) is None:
                host.private[L1_WEEKDAY_SLOT] = []
                host.private[L1_WEEKEND_SLOT] = []

            if len(host.private[current_time_slot[0]]) == len(TIME_SLOTS):
                # if hosts have monitored across all time slots - reset
                host.private[current_time_slot[0]] = []

            # get the datetime when this host was last monitored
            host_last_monitored_on = host.private.get('monitoring_start')

            if host_last_monitored_on is not None:
                host_last_monitored_on = datetime.datetime.strptime(host_last_monitored_on, TIME_FORMAT)

            if current_time_slot[1] in host.private[current_time_slot[0]]:
                # if host has already already been monitored in the slot
                hosts_not_to_monitor[host_level].append(host)
                continue


            if host_last_monitored_on is not None and last_monitoring_time is not None and host_last_monitored_on > last_monitoring_time:
                # safe programming - only let hosts that have not been monitored or monitored before the
                # current set of hosts
                hosts_not_to_monitor[host_level].append(host)
                continue

            if host in monitored_hosts:
                # may only be seen if number of hosts < MAX_ESX_TO_MONITOR
                hosts_not_to_monitor[host_level].append(host)
                continue

            if host_last_monitored_on is not None and host_last_monitored_on > vcenter_monitor_cycle_start:
                # Host has not been monitored even once since the vcenter monitoring cycle started
                hosts_not_to_monitor[host_level].append(host)
                continue

            vmdk_on_host = host.private.get('total_vmdks', 0)
            if vmdk_on_host > max_vmdk_to_monitor:
                # If the VMDK on the ESX is more than the bound. Monitor only the host
                hosts_to_monitor = [host]
                break

            if host in priority_esx_list and priority_esx_added >= max_priority_esx_to_monitor:
                # all slots for prioirty ESX have been assigned
                hosts_not_to_monitor[host_level].append(host)
                continue

            total_vmdk_to_monitor += vmdk_on_host

            if total_vmdk_to_monitor > max_vmdk_to_monitor:
                # make sure the current VMDK to monitor is within bound
                total_vmdk_to_monitor -= vmdk_on_host
                break

            hosts_to_monitor.append(host)

            if host in priority_esx_list:
                # if host is a part of prioirty esx increment the counter
                priority_esx_added += 1
            else:
                non_priority_esx_added += 1

            if non_priority_esx_added >= max_esx_to_monitor - max_priority_esx_to_monitor:
                # make sure the ESX count for monitoring is within bounds
                break

        if len(hosts_to_monitor) < max_esx_to_monitor and total_vmdk_to_monitor < max_vmdk_to_monitor:
            # This can happen if the remaining ESX to monitor are way less then the bounds
            # here the prioirty is given to host not belonging to prioirty esx list
            for host in hosts_not_to_monitor['non_priority'] + hosts_not_to_monitor['priority']:
                if host not in priority_esx_list and non_priority_esx_added >= max_esx_to_monitor - max_priority_esx_to_monitor:
                    # all slots for prioirty ESX have been assigned
                    continue

                total_vmdk_to_monitor += host.private.get('total_vmdks', 0)
                if total_vmdk_to_monitor > max_vmdk_to_monitor:
                    break

                hosts_to_monitor.append(host)
                if len(hosts_to_monitor) >= max_esx_to_monitor:
                    break

                if host not in priority_esx_list:
                    non_priority_esx_added += 1

    except Exception as e:
        import traceback
        tarceback.print_exc()

    return (hosts_to_monitor, monitored_hosts)

def change_hosts_to_monitor(comp, monitor_transition_interval = MONITOR_TRANSITION_INTERVAL,
                            max_vmdk_to_monitor = MAX_VMDK_TO_MONITOR, max_esx_to_monitor = MAX_ESX_TO_MONITOR):
    """
    For a profiled vCenter, gets a list of ESX and sorts them 
    based on last monitored datetime. It then marks ESX for monitoring
    based on the following criteria:
    - At-least one ESX should be marked for monitoring for the vCenter
    - Marking more than one cluster for monitoring will depend on the following
      configurable conditions:
        - total number of ESX <= MAX_ESX_TO_MONITOR
        - total number of VMDK to monitor within the ESX <= MAX_VMDK_TO_MONITOR
        - ESX has not already been monitored for the time slot
        - ESX has at-least been monitored once since the monitoring cycle restarted
          for the vCenter

    Once ESX have been identified, mark the which were already being monitored 
    as NOT MONITORING and mark the next set of ESX for MONITORING.
    """
    try:
        now = datetime.datetime.now()

        if comp.private is None:
            comp.private = {}
            comp.save()

        current_monitoring_index = comp.private.get('current_monitoring_index', 0)
        vcenter_monitor_cycle_start = datetime.datetime.strptime(comp.private.get('vcenter_monitor_cycle_start', \
                                                                 now.strftime(TIME_FORMAT)), TIME_FORMAT)
        time_slot_start_time = datetime.datetime.strptime(comp.private.get('time_slot_start_time', \
                                                          now.strftime(TIME_FORMAT)), TIME_FORMAT)

        only_priority = comp.private.get('only_priority', True)
        comp.private['only_priority'] = only_priority

        #
        # Get all the hosts within the vCenter from the database
        #
        priority_esx_list = []
        non_priority_esx_list = []
        apply_filter = True

        priority_cluster = PRIORITY_CLUSTER

        if len(priority_cluster) == 0:
            # if there are not cluster in priority list, monitoring for all
            # is enabled. Else clusters will be filtered
            apply_filter = False

        for cl in all_clusters.keys():
            if apply_filter and cl.lower() not in PRIORITY_CLUSTER:
                # if cluster not a part of priority list and monitoring for this needs to
                # start after START_MONITORING_FOR_ALL. Check if the cluster meets the criteria
                created = datetime.datetime.strptime(start_time.strftime(TIME_FORMAT), TIME_FORMAT)
                since = now - datetime.timedelta(seconds = START_MONITORING_FOR_ALL)
                since = datetime.datetime.strptime(since.strftime(TIME_FORMAT), TIME_FORMAT)
                if since < created:
                    continue

            # only select ESX which are not in error state
            host_objs  = all_clusters.get(cl)

            if cl in PRIORITY_CLUSTER:
                # if part of priority list
                priority_esx_list.extend(host_objs)
            else:
                if only_priority is True:
                    only_priority = False

                # if not part of priority list
                non_priority_esx_list.extend(host_objs)

        print("hosts under the vCenter(%s) scheduled for monitoring = %s" % (comp.ip, (len(non_priority_esx_list) + len(priority_esx_list))))
        print("hosts priority = %s" % [h.name for h in priority_esx_list])

        # sort the hosts based on the oldest monitoring tiem in ascending order
        # older monitored host will come before latest monitored hosts
        non_priority_esx_list.sort(key=lambda x: datetime.datetime.strptime(x.private.get('monitoring_start', \
                                  x.created.strftime(TIME_FORMAT)), TIME_FORMAT))

        # sort the hosts based on the oldest monitoring tiem in ascending order
        # older monitored host will come before latest monitored hosts
        priority_esx_list.sort(key=lambda x: datetime.datetime.strptime(x.private.get('monitoring_start', \
                                  x.created.strftime(TIME_FORMAT)), TIME_FORMAT))

        # get the current time slot
        current_time_slot = get_current_time_slot(now, monitor_transition_interval)

        # the number of priority ESX that should be monitored within the time slot
        max_priority_esx_to_monitor = min(int((PROIRITY_PERC/ 100.0) * max_esx_to_monitor), len(priority_esx_list))

        max_non_priority_esx_to_monitor = max_esx_to_monitor - max_priority_esx_to_monitor

        hosts_to_monitor, monitored_hosts = schedule_esx_for_monitoring(now,
                                                                        priority_esx_list,
                                                                        non_priority_esx_list,
                                                                        current_time_slot,
                                                                        vcenter_monitor_cycle_start,
                                                                        current_monitoring_index,
                                                                        monitor_transition_interval,
                                                                        max_vmdk_to_monitor,
                                                                        max_priority_esx_to_monitor,
                                                                        max_esx_to_monitor)

        if len(hosts_to_monitor) == 0 and len(monitored_hosts) > 0:
            print(" continue monitoring last hosts")
            # no change is required. The current host being monitored will continue
            return

        # greater of the two monitoring counts which needs to be monitored
        time_to_monitornon_non_priority = int(math.ceil(len(non_priority_esx_list) / max_non_priority_esx_to_monitor)) * monitor_transition_interval
        time_to_monitornon_priority = int(math.ceil(len(priority_esx_list) / max_priority_esx_to_monitor)) * monitor_transition_interval

        # time required in seconds to monitor each esx at-least in one time slot
        time_required_to_monitor_each_esx_once = max(time_to_monitornon_non_priority, time_to_monitornon_priority)

        # time required in seconds to complete all time slots
        time_required_to_complete_all_slots = int(len(TIME_SLOTS)) * monitor_transition_interval

        print("hosts now not monitored = %s" % [h.name for h in monitored_hosts])
        for host in monitored_hosts:
            host.state = PROFILED
            host.save()

        print("hosts to start monitoring = %s and time_slot = %s" % ([h.name for h in hosts_to_monitor], current_time_slot))
        host_monitoring_from_prioirty_list = []
        for host in hosts_to_monitor:
            host.state = MONITORING
            host.private['monitoring_start'] = now.strftime(TIME_FORMAT)
            host.private[current_time_slot[0]].append(current_time_slot[1])
            host.save()
            if host in priority_esx_list:
                host_monitoring_from_prioirty_list.append(host)

        print("priority hosts to start monitoring  = %s" % ([h.name for h in host_monitoring_from_prioirty_list]))

        # reset vcenter_monitor_cycle_start whenever all esx comes into picture
        if comp.private['only_priority'] and only_priority is False:
            comp.private['only_priority'] = only_priority
            vcenter_monitor_cycle_start = now

        if now - datetime.timedelta(seconds = time_required_to_monitor_each_esx_once) >= vcenter_monitor_cycle_start:
            # if for vcenter all ESX has been monitored once
            hosts = []
            for h in non_priority_esx_list + priority_esx_list:
                monitoring_start = datetime.datetime.strptime(h.private['monitoring_start'], TIME_FORMAT)
                monitoring_start = datetime.datetime.strptime(monitoring_start.strftime(COMPARE_FORMAT), COMPARE_FORMAT)
                cycle_start = datetime.datetime.strptime(vcenter_monitor_cycle_start.strftime(COMPARE_FORMAT), COMPARE_FORMAT)

                if not monitoring_start >= cycle_start:
                    hosts.append(h)

            for h in hosts:
                print ("%s, %s, %s" % (h.name, h.private, vcenter_monitor_cycle_start))

            vcenter_monitor_cycle_start = now
            print("setting vcenter_monitor_cycle_start = %s" % vcenter_monitor_cycle_start)

        if now - datetime.timedelta(seconds = time_required_to_complete_all_slots) >= time_slot_start_time:
            # if the time slot cycle is complete
            time_slot_start_time = now
            current_monitoring_index += 2 * max_esx_to_monitor
            if current_monitoring_index >= len(non_priority_esx_list):
                current_monitoring_index = 0

            print("current_monitoring_index = %s, time_slot_start_time = %s" % \
                         (current_monitoring_index, time_slot_start_time))

        comp.private['current_monitoring_index'] = current_monitoring_index
        comp.private['vcenter_monitor_cycle_start'] = vcenter_monitor_cycle_start.strftime(TIME_FORMAT)
        comp.private['time_slot_start_time'] = time_slot_start_time.strftime(TIME_FORMAT)

        comp.save()

        if len(non_priority_esx_list) == 0:
            assert(len(host_monitoring_from_prioirty_list) == len(hosts_to_monitor))

        if len(non_priority_esx_list) > 1:
            assert(len(host_monitoring_from_prioirty_list) == max_priority_esx_to_monitor)

        assert(len(hosts_to_monitor) == max_esx_to_monitor or \
               len(hosts_to_monitor) == len(host_monitoring_from_prioirty_list) or \
               len(hosts_to_monitor) == (len(non_priority_esx_list) + len(priority_esx_list)))

    except Exception as e:
        import traceback
        traceback.print_exc()
        import sys
        sys.exit(1)

    return

while True:
    change_hosts_to_monitor(vCenter)
    time.sleep(int(MONITOR_TRANSITION_INTERVAL/ 2))

"""
start = datetime.datetime.now()
cycle_start = start
a = []

max_esx = 5

monitoring_interval = 1 # 1 seconds
time_slots = []

for i in range(12):
    time_slots.append("T%d" % (i + 1))

print (time_slots)

for i in range((max_esx * 35)):
    a.append([i, start, []])

sorted_a = a
print ([m[0] for m in sorted_a])
time.sleep(monitoring_interval)

change_group = True

if (len(a) / max_esx) % len(time_slots):
    change_group = False

time_required_to_monitor_each_esx_once = int((len(a)/ max_esx)) * monitoring_interval

print ("%s, %s, %s - %s" % (len(a) / max_esx, len(time_slots), change_group, time_required_to_monitor_each_esx_once))

last_schedule = []
index = 0
slots_done = []
for t in range(300):
    i = 0
    esx_scheduled = []
    not_scheduled = []
    current_slot_index = t % len(time_slots)
    current_slot = time_slots[current_slot_index]
    now = datetime.datetime.now()
    slots_done.append(current_slot)
    for l in sorted_a[index:] + sorted_a[:index]:

        if l[1] is not None and l[1] > cycle_start:
            # if already monitored in 
            not_scheduled.append(l)
            continue

        if l[0] in last_schedule:
            not_scheduled.append(l)
            continue

        if len(l[2]) == len(time_slots):
            l[2] = []

        if current_slot in l[2]:
            not_scheduled.append(l)
            continue

        if i == max_esx:
            break

        esx_scheduled.append(l[0])
        l[2].append(current_slot)
        sorted_a[sorted_a.index(l)] = [l[0], now, l[2]]
        i += 1

    i = len(esx_scheduled) - 1
    if len(esx_scheduled) < max_esx:
        for l in not_scheduled:
            if i == max_esx:
                break
            esx_scheduled.append(l[0])
            l[2].append(current_slot)
            sorted_a[sorted_a.index(l)] = [l[0], now, l[2]]
            i += 1


    if len(slots_done) == len(time_slots):
        start = datetime.datetime.now()
        slots_done = []
        index += max_esx * 2
        if index >= len(sorted_a):
            index = 0

    print ("current slot = %s - scheduled = %s" % (current_slot, esx_scheduled))
    last_schedule = esx_scheduled
    sorted_a = sorted(sorted_a, key=lambda x: x[1])

    if now - datetime.timedelta(seconds = time_required_to_monitor_each_esx_once) >= cycle_start:
        cycle_start = now

    time.sleep(monitoring_interval)
"""
