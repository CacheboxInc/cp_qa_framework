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
import atexit
import subprocess
import sys
import time
import threading

import ssl
import urllib.parse

from pyVim import connect
from pyVmomi import vmodl
from pyVmomi import vim

ERROR = -1
SUCCESS = 0

RETRY = 3

SUPPORTED_ID = "praapa"

class TimeoutError(Exception): pass

def timelimit(timeout):
    def internal(function):
        def internal2(*args, **kw):
            class InterruptableThread(threading.Thread):
                def __init__(self):
                    threading.Thread.__init__(self)
                    self.result = None
                    self.error = None

                def run(self):
                    try:
                        self.result = function(*args, **kw)
                    except:
                        self.error = sys.exc_info()[0]

            c = InterruptableThread()
            c.start()
            c.join(timeout)
            if c.isAlive():
                c._Thread__stop()
                raise TimeoutError

            if c.error:
                raise c.error

            return c.result
        return internal2
    return internal

#Connect to host
@timelimit(60)
def host_connect(host, username, password):
    context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    context.verify_mode = ssl.CERT_NONE
    service_instance = connect.SmartConnect(host=host,
                                            user=username,
                                            pwd=password,
                                            connectionPoolTimeout=-1,
                                            sslContext=ssl._create_unverified_context())

    atexit.register(connect.Disconnect, service_instance)
    content = service_instance.RetrieveContent()
    return service_instance, content

def wait_for_task(task):
    #
    # Waitis for task to complete and then 
    # returns a dictionary containing the following:
    # status :  error (-1)  or success (0)
    # message : error or success message
    # details :  a list of details in case of error
    #

    task_done = False
    status = ERROR
    message = ''
    details = []

    while not task_done:
        if task.info.state == 'success':
            status = SUCCESS
            break

        if task.info.state == 'error':
            message = task.info.error.msg
            if len(task.info.error.faultMessage) > 0:
                for fault in task.info.error.faultMessage:
                    details.append(fault.message)
            task_done = True

    return {
            'status' : status,
            'message' : message,
            'details': details
           }


class VCenter(object):

    def __init__(self, ip, username, password):
        self.ip = ip
        self.username = username
        self.password = password
        self.si = None
        self.content = None
        self.connect()

    def connect(self):
        si, content = host_connect(self.ip, self.username, self.password)
        # Store vim.HostSystem
        self.si = si
        self.content = content

    def disconnect(self):
        connect.Disconnect(self.si)

    def get_obj(self, vimtype, name):
        #
        # Get the vsphere managed object associated with a given text name
        #
        obj = None
        container = self.content.viewManager.CreateContainerView(self.content.rootFolder,
                                                        vimtype, True)
        for c in container.view:
            if urllib.parse.unquote(c.name) == name:
               obj = c
               break

        return obj

    def get_obj_by_moId(self, vimtype, moid):
        #
        # Get the vsphere managed object by moid value
        #
        obj = None
        container = self.content.viewManager.CreateContainerView(self.content.rootFolder,
                                                        vimtype, True)
        for c in container.view:
            if c._GetMoId() == moid:
                obj = c
                break

        return obj

    def add_custom_field_def(self, mob, key, value):
        field_manager = self.content.customFieldsManager
        try:
            field_manager.AddCustomFieldDef(key, type(mob), None, None)
        except vim.fault.DuplicateName:
            # In case the field has already been added, ignore
            pass

        mob.SetCustomValue(key, value = value)

    def set_custom_field(self, mob, key, value):
        field_manager = self.content.customFieldsManager

        try:
            mob.SetCustomValue(key, value=value)
        except:
            return False

        return True

    def get_datacenters(self):
        try:
            datacenters = self.si.content.rootFolder.childEntity
        except:
            self.connect()
            datacenters = self.si.content.rootFolder.childEntity

        return datacenters


    def get_clusters(self, datacenter):
        clusters = []

        try:
            # Folder at the top may or may not be datacenter and thus
            # would not have hostFolder
            for cluster in datacenter.hostFolder.childEntity:
                if ("vim.ClusterComputeResource" == cluster.__class__.__name__):
                    clusters.append(cluster)
        except:
            pass

        return clusters

    def get_hosts(self, datacenter):
        clusters = self.get_clusters(datacenter)
        hosts = []

        try:
            # Folder at the top may or may not be datacenter and thus
            # would not have hostFolder
            for cluster in datacenter.hostFolder.childEntity:
                if ("vim.ComputeResource" == cluster.__class__.__name__):
                    if cluster not in clusters:
                        hosts.append(cluster)
        except:
            pass

        return hosts

    def get_vim_host(self, host_ip):
        host = None
        try:
            for datacenter in self.get_datacenters():
                host = self.si.content.searchIndex.FindByIp(datacenter, host_ip, False)
                if host is not None:
                    break

                host = self.si.content.searchIndex.FindByDnsName(datacenter, host_ip, False)
                if host is not None:
                    break
        except:
            # Can happen if the host is deleted or is being modified
            host = None
            pass

        return host

    def is_praapa_installed(self, filter_name = SUPPORTED_ID):
        is_installed = False

        for d in self.get_datacenters():
            for c in self.get_clusters(d):
                praapa_filter = self.get_filter_detail(c)
                if praapa_filter.get('name') == filter_name:
                    # break if praapa filter is found
                    is_installed = True
                    break

            if is_installed:
                break

        return is_installed

    def is_installed_or_upgrade_required(self, version, filter_name = SUPPORTED_ID):
        should_install = False
        should_upgrade = False

        cls = 0
        is_installed = 0

        for d in self.get_datacenters():
            for c in self.get_clusters(d):
                cls += 1
                praapa_filter = self.get_filter_detail(c)
                if praapa_filter.get('name') == filter_name:
                    # break if praapa filter is found
                    installed_version = praapa_filter['version'].split("-")[0].split(".")
                    current_version = version.split(".")

                    for i in range(3):
                        if int(current_version[i]) > int(installed_version[i]):
                            should_upgrade = True

                    if not should_upgrade:
                        is_installed += 1

        if is_installed < cls and not should_upgrade:
            should_install = True

        return (should_install, should_upgrade, cls)

    def get_filter_detail(self, cluster, filter_name = SUPPORTED_ID):
        #
        # Takes in the filter name and cluster and returns a dictionay with filter
        # details
        #
        praapa_filter = {}

        io_filter_mngr = self.content.ioFilterManager
        for flt in io_filter_mngr.QueryIoFilterInfo(cluster):
             if flt.name == filter_name:
                 praapa_filter = {
                                  'id'            : flt.id,
                                  'name'          : flt.name,
                                  'vendor'        : flt.vendor,
                                  'version'       : flt.version,
                                  'releaseDate'   : flt.releaseDate
                                }

        return praapa_filter

    def install_filter_on_cluster(self, cluster, vib_url, filter_name = SUPPORTED_ID):
        #
        # Takes in the VIB URL, filter name and cluster as the input
        # and returns the task object
        #

        flt = self.get_filter_detail(cluster, filter_name)
        if len(flt) > 0:
            return None

        io_filter_mngr = self.content.ioFilterManager
        return io_filter_mngr.InstallIoFilter(vib_url, cluster)

    def uninstall_filter_on_cluster(self, cluster, filter_name = SUPPORTED_ID):
        #
        # Takes in the VIB URL and cluster as the input
        # and returns the task object
        #
        flt = self.get_filter_detail(cluster, filter_name)
        if len(flt) == 0:
            return None

        filter_id = flt['id']
        io_filter_mngr = self.content.ioFilterManager
        return io_filter_mngr.UninstallIoFilter(filter_id, cluster)

    def upgrade_filter_on_cluster(self, cluster, vib_url, filter_name = SUPPORTED_ID):
        #
        # Takes in the VIB URL and cluster as the input
        # and returns the task object
        #
        flt = self.get_filter_detail(cluster, filter_name)
        if len(flt) == 0:
            return None

        filter_id = flt['id']
        io_filter_mngr = self.content.ioFilterManager
        return io_filter_mngr.UpgradeIoFilter(filter_id, cluster, vib_url)

    def resolve_filter_issue_on_host(self, cluster, host, filter_name = SUPPORTED_ID):
        #
        # Takes in the cluster and host as the input
        # and returns the task object
        #
        flt = self.get_filter_detail(cluster, filter_name)
        if len(flt) == 0:
            return None

        filter_id = flt['id']
        io_filter_mngr = self.content.ioFilterManager
        return io_filter_mngr.ResolveInstallationErrorsOnHost(filter_id, host)

    def query_filter_issue(self, cluster, filter_name = SUPPORTED_ID):
        #
        # Returns a dictionary of hosts on which the last
        # operation was performed, along with the issues
        #
        filter_issues = {}
        flt = self.get_filter_detail(cluster, filter_name)
        if len(flt) == 0:
            return filter_issues

        filter_id = flt['id']
        io_filter_mngr = self.content.ioFilterManager
        issue = io_filter_mngr.QueryIoFilterIssues(filter_id, cluster)
        if issue.hostIssue:
            for flt_issue in issue.hostIssue:
                if len(flt_issue.issue[0].faultMessage) > 0:
                    msg = flt_issue.issue[0].faultMessage[0].message
                    filter_issues[flt_issue.host] = msg

        return filter_issues

    def get_list_of_vms_using_filter(self, cluster, filter_name = SUPPORTED_ID):
        #
        # For cluster gets the list of virtual machine which 
        # has filter associated with atleast one of it's vmdk
        #
        flt = self.get_filter_detail(cluster, filter_name)
        if len(flt) == 0:
            return []

        filter_id = flt['id']
        io_filter_mngr = self.content.ioFilterManager
        vms = []
        disks = io_filter_mngr.QueryDisksUsingFilter(filter_id, cluster)

        for d in disks:
            if d.vm in vms:
                continue

            vms.append(d.vm)

        return vms

class VCenterCluster(object):

    def __init__(self, handle):
        #Store vim.VirtualMachine
        self.handle = handle

    def get_hosts(self):
        lst = []
        for i in self.handle.host:
            lst.append(i)

        return lst

    def get_host_network_configuration(self):
        lst = {}
        for i in self.handle.host:
            lst.update(EsxHost(i).get_network_configuration())

        return lst

class EsxHost(object):


    def __init__(self, handle):
        self.handle = handle

    #get vms hosted on this esx
    def get_vms(self):
        lst = []
        try:
            vms = self.handle.vm
        except:
            self.connect()
            vms = self.handle.vm

        for i in vms:
            lst.append(i)

        return lst

    def __get_datacenter_for_host(self, si):
        for dc in si.content.rootFolder.childEntity:
            if si.content.searchIndex.FindByIp(dc, self.handle.name, False) is not None:
                break

        return dc

    #get vms hosted on this esx
    def get_datastores(self):
        try:
            datastores = self.handle.datastore
        except:
            self.connect()
            datastores = self.handle.datastore

        return datastores

    def get_esx_vmdk_list(self):
        vm_dict = {}
        for v in self.get_vms():
            vm = GuestVM(v)
            disks = vm.get_disks()
            path = v.summary.config.vmPathName.split("]")[-1].strip().replace(" ", "_")
            vm_dict[path] = {
                             "name" : v.summary.config.name,
                             "disks" : disks
                             }
        return vm_dict

    def remote_clone_vm(self, datastore_name, guest_name, guest_cpu, guest_mem, remote_vm):
        # get service instance for the host
        s = self.handle._GetStub()
        si = vim.ServiceInstance("ServiceInstance", s)

        # find the datacenter fo the host
        dc = self.__get_datacenter_for_host(si)
        vm_folder = dc.vmFolder
        resource_pool = self.handle.parent.resourcePool

        # define th VMX file for the new VM
        datastore_path = '[' + datastore_name + '] ' + guest_name
        vmx_file = vim.vm.FileInfo(logDirectory=None,
                                   snapshotDirectory=None,
                                   suspendDirectory=None,
                                   vmPathName=datastore_path)

        devices = []

        for hardware in remote_vm.config.hardware.device:
            if isinstance(hardware, vim.vm.device.VirtualKeyboard):
                continue

            if isinstance(hardware, vim.vm.device.VirtualPointingDevice):
                continue

            if isinstance(hardware, vim.vm.device.VirtualCdrom):
                continue

            dev_spec = vim.vm.device.VirtualDeviceSpec()
            dev_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
            dev_spec.device = eval("%s()" % type(hardware).__name__)

            if hardware.controllerKey:
                dev_spec.device.controllerKey = hardware.controllerKey
            if hardware.key:
                dev_spec.device.key = hardware.key
            try:
                dev_spec.device.capacityInKB = hardware.capacityInKB
            except:
                pass
            try:
                dev_spec.device.busNumber = hardware.busNumber
            except:
                pass

            if hardware.backing:
                dev_spec.device.backing = eval("%s()" % type(hardware.backing).__name__)
                dev_spec.fileOperation = "create"

                if hardware.unitNumber is not None:
                    dev_spec.device.unitNumber = hardware.unitNumber

                try:
                    if hardware.backing.thinProvisioned:
                        dev_spec.device.backing.thinProvisioned = True
                except:
                    pass

                try:
                    dev_spec.device.backing.diskMode = hardware.backing.diskMode
                except:
                    pass

                try:
                    dev_spec.device.backing.deviceName = hardware.backing.deviceName
                except:
                    pass

            try:
                dev_spec.device.connectable = eval("%s()" % type(hardware.connectable).__name__)
                dev_spec.device.connectable.startConnected = True
                dev_spec.device.connectable.allowGuestControl = True
                dev_spec.fileOperation = None
            except:
                pass

            try:
                if hardware.sharedBus is not None:
                    dev_spec.device.sharedBus = "noSharing"
                    dev_spec.device.scsiCtlrUnitNumber = hardware.scsiCtlrUnitNumber
                    dev_spec.device.hotAddRemove = hardware.hotAddRemove
            except:
                pass

            try:
                dev_spec.device.allowUnrestrictedCommunication = hardware.allowUnrestrictedCommunication
                dev_spec.device.filterEnable = hardware.filterEnable
            except:
               pass

            devices.append(dev_spec)

        boot_options = vim.vm.BootOptions()
        boot_options.enterBIOSSetup = False

        config = vim.vm.ConfigSpec(name=guest_name,
                                   memoryMB=guest_mem,
                                   numCPUs=guest_cpu,
                                   files=vmx_file,
                                   guestId=remote_vm.config.guestId,
                                   version=remote_vm.config.version,
                                   bootOptions=boot_options,
                                   deviceChange=devices)

        task = vm_folder.CreateVM_Task(config=config, pool=resource_pool)
        return wait_for_task(task)

    def get_virtual_switches(self):
        vswitches = {}
        for vswitch in self.handle.config.network.vswitch:
            vswitches[vswitch.key] = {
                                     'key': vswitch.key,
                                     'p_nics': vswitch.pnic,
                                     'name' : vswitch.name,
                                     'portgroup' : vswitch.portgroup
                                     }

        return vswitches

    def get_opaque_switches(self):
        oswitches = {}
        for oswitch in self.handle.config.network.opaqueSwitch:
            oswitches[oswitch.key] = {
                                     'key': oswitch.key,
                                     'p_nics': oswitch.pnic,
                                     'name' : oswitch.name,
                                     'portgroup' : []
                                     }

        return oswitches


    def get_proxy_switches(self):
        pswitches = {}
        for pswitch in self.handle.config.network.proxySwitch:
            key = pswitch.dvsUuid.replace(" ", "")
            pswitches[key] = {
                                     'key': pswitch.key,
                                     'p_nics': pswitch.pnic,
                                     'name' : pswitch.dvsName,
                                     'portgroup' : []
                                     }

        return pswitches

    def get_all_network_switches(self):
        switches = {}
        switches.update(self.get_virtual_switches())
        switches.update(self.get_opaque_switches())
        switches.update(self.get_proxy_switches())

        return switches

    def get_pnic_details(self):
        pnics = {}
        for pnic in self.handle.config.network.pnic:
            try:
                speed = pnic.linkSpeed.speedMb
                duplex = pnic.linkSpeed.duplex
                link_up = True
            except:
                speed = "-na-"
                duplex = "-na-"
                link_up = False

            pnics[pnic.key] = {
                             'key': pnic.key,
                             'device' : pnic.device,
                             'mac' : pnic.mac,
                             'speed' : speed,
                             'duplex' : duplex,
                             'is_link_up' : link_up
                             }

        return pnics

    def get_vnic_details(self):
        virtual_nics = {}
        host_nconfigs = self.handle.config.virtualNicManagerInfo.netConfig
        for host_nconfig in host_nconfigs:
            nic_type = host_nconfig.nicType
            for candidate_vnic in host_nconfig.candidateVnic:
                device = candidate_vnic.device
                if virtual_nics.get(device) is not None:
                    virtual_nics[device]["nic_type"] += ", %s" % nic_type
                    continue

                virtual_nics[device] = {}
                if candidate_vnic.spec:
                    try:
                        switch_uuid = candidate_vnic.spec.distributedVirtualPort.switchUuid.replace(" ", "")
                    except:
                        switch_uuid = ""

                    virtual_nics[device] = {
                        "mtu" : candidate_vnic.spec.mtu,
                        "ip" :  candidate_vnic.spec.ip.ipAddress,
                        "switch_uuid" : switch_uuid,
                        "port_group" : candidate_vnic.portgroup,
                        "mac" : candidate_vnic.spec.mac,
                        "nic_type" : nic_type
                    }

        return virtual_nics

    def get_portgroups(self):
        portgroups = {}
        for pg in self.handle.config.network.portgroup:
            try:
                pnics = pg.spec.policy.nicTeaming.nicOrder.activeNic
            except:
                pnics = []

            portgroups[pg.spec.name] = {
                                  'key': pg.key,
                                  'switch': pg.vswitch,
                                  'pnics': pnics
                                  }
        return portgroups

    def get_network_configuration(self):
        net_config = []
        vnics = self.get_vnic_details()
        pnics =  self.get_pnic_details()
        switches =  self.get_all_network_switches()
        portgroups = self.get_portgroups()

        for vnic in list(vnics.keys()):
            is_configured = True
            is_connected = True
            connection_state = "not responding"
            temp = vnics.get(vnic)
            temp['pnics'] = []
            temp['name'] = vnic
            if portgroups.get(vnics[vnic]['port_group']):
                switch_id = portgroups.get(vnics[vnic]['port_group'])['switch']
            else:
                switch_id = vnics[vnic]['switch_uuid']

            switch = switches.get(switch_id)
            temp['switch'] = switch['name']
            for pn in switch['p_nics']:
                pnic = pnics.get(pn)

                # Check whether Host is connected to vCenter or not, if not
                # then set is_configured to False
                conn_state = self.handle.runtime.connectionState
                connection_state = "connected"
                if conn_state is vim.HostSystem.ConnectionState.disconnected:
                    is_configured = False
                    is_connected = False
                    connection_state = "disconnected"
                elif conn_state is vim.HostSystem.ConnectionState.notResponding:
                    is_configured = False
                    is_connected = False
                    connection_state = "not responding"

                temp['pnics'].append({
                                     'device': pnic['device'],
                                     'duplex': pnic['duplex'],
                                     'speed': pnic['speed'],
                                     'link': pnic['is_link_up']
                                    })
                if not pnic['is_link_up']:
                    is_configured = False

            temp['is_configured'] = is_configured
            temp['is_connected'] = is_connected
            temp['connection_state'] = connection_state
            net_config.append(temp)

        return {self.handle.name : net_config}


class GuestVM(object):

    def __init__(self, handle):
        # Store vim.VirtualMachine
        self.handle = handle

    def get_vmdks(self):
        vmdks = []
        try:
            if self.handle.config.hardware is None:
                return vmdks

            vm_hardware = self.handle.config.hardware
            for each_vm_hardware in vm_hardware.device:
                if (each_vm_hardware.key >= 2000) and (each_vm_hardware.key < 3000):
                    vmdks.append(each_vm_hardware)
        except:
            pass

        return vmdks

    def is_on(self):
       return self.handle.runtime.powerState == vim.VirtualMachinePowerState.poweredOn

    def shutdown(self):
        initiated_off = False
        while self.is_on():
            try:
               if not initiated_off:
                   task = self.handle.ShutdownGuest()
                   time.sleep(20)
            except:
               # can happen if vmware tools not installed
               if not initiated_off:
                   task = self.handle.PowerOff()
                   initiated_off = True

            time.sleep(1)

        return

    def poweron(self):
        i = 0
        if not self.is_on():
            while i < RETRY:
                task = self.handle.PowerOn()
                while task.info.state not in [vim.TaskInfo.State.success,
                                              vim.TaskInfo.State.error]:
                    time.sleep(1)
                if task.info.state == vim.TaskInfo.State.error:
                    i += 1
                    time.sleep(60)
                    continue

                break
        return

    def delete(self):
        task = self.handle.Destroy_Task()
        time.sleep(5)

        return

    def reconfigure(self, spec, wait=True):
        task = self.handle.ReconfigVM_Task(spec)
        if not wait:
            return task

        return wait_for_task(task)

def get_mouuid(vcenter, obj):

    if obj is None:
        return None
    if isinstance(obj, vim.Datacenter):
        uuid = "%s_%s" % (vcenter.ip, obj.name)
    elif isinstance(obj, vim.ClusterComputeResource):
        vc = vcenter.ip.replace(" ", "").replace("-", "").replace(".", "")
        uuid = "%s_%s" % (vc, obj.name)
        return uuid
    elif isinstance(obj, vim.HostSystem):
        uuid = "%s_%s" % (vcenter.ip, obj.hardware.systemInfo.uuid)
    elif isinstance(obj, vim.VirtualMachine):
        if obj.config is None:
            return None
        uuid = "%s_%s" % (vcenter.ip, obj.config.uuid)
        uuid = uuid.replace(" ", "").replace("-", "").replace(".", "")
        uuid = "%s_%s" % (uuid, obj.config.files.vmPathName.split("/")[-2].split("] ")[-1].strip())
        return uuid
    elif isinstance(obj, vim.Datastore):
        uuid = "%s_%s" % (vcenter.ip, list(filter(None, obj.summary.url.split("/")))[-1])
    elif isinstance(obj, vim.VirtualDevice):
        uuid = "%s_%s" % (vcenter.ip, obj.backing.uuid)
        uuid = uuid.replace(" ", "").replace("-", "").replace(".", "")
        uuid = "%s_%s" % (uuid, obj.backing.fileName.split("]")[1].strip().split("/")[0])
        return uuid

    return uuid.replace(" ", "").replace("-", "").replace(".", "")
