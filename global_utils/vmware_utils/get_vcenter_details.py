import time
import atexit
from pyVim import connect
from pyVmomi import vmodl
from pyVmomi import vim
import tasks
import argparse
import sys
import datetime
sys.path.insert(0,'..')
from vim_utils import *
from pbm_utils import *

def reconfigure(vm_obj, spec, wait=True):
        task = vm_obj.ReconfigVM_Task(spec)
        if not wait:
            return task

        return wait_for_task(task)

def attach_vmdk(vm_obj, vmdk, vcenter,cache_policy_kwargs):
        pbm_util = PBMUtils(vcenter, cache_policy_kwargs)
        profile = pbm_util.get_supported_profile()
        
        if profile is None:
            raise Exception("Could not find supported SPBM. Please check if PrimaryIO is installed.")

        vm_profile_spec = vim.vm.DefinedProfileSpec()
        vm_profile_spec.profileId = profile.profileId.uniqueId
        
        virtual_device_spec = vim.vm.device.VirtualDiskSpec()
        virtual_device_spec.device = vmdk
        virtual_device_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.edit
        virtual_device_spec.profile.append(vm_profile_spec)

        return virtual_device_spec

def deattach_vmdk(vm_obj, vmdk):
        vm_profile_spec = vim.vm.EmptyProfileSpec()

        virtual_device_spec = vim.vm.device.VirtualDiskSpec()
        virtual_device_spec.device = vmdk
        virtual_device_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.edit
        virtual_device_spec.profile.append(vm_profile_spec)

        return virtual_device_spec

def get_obj(content, vimtype, name):
    obj = None
    container = content.viewManager.CreateContainerView(
        content.rootFolder, vimtype, True)
    for c in container.view:
        if c.name == name:
            obj = c
            break
    return obj

def create_vm_summary(vm, vm_summary_dict):
    vm_details = []
    summary = vm.summary
    vm_details.append(summary.config.guestFullName)
    tools_version = summary.guest.toolsStatus
    if summary.guest is not None:
        ip_address = summary.guest.ipAddress
        vm_details.append(ip_address)
    vm_summary_dict[summary.config.name] = vm_details
    vm_details.append(summary.config.uuid)
    vm_details.append(summary.config.vmPathName.split()[0].strip('[').strip(']'))
    vm_details.append(summary.config.numVirtualDisks)
    

def get_args():
    parser = argparse.ArgumentParser(
        description='Arguments for talking to vCenter')

    parser.add_argument('-s', '--host',
                        required=True,
                        action='store',
                        help='vSpehre service to connect to')

    parser.add_argument('-o', '--port',
                        type=int,
                        default=443,
                        action='store',
                        help='Port to connect on')

    parser.add_argument('-u', '--user',
                        required=False,
                        default='administrator@vsphere.local',
                        action='store',
                        help='User name to use')

    parser.add_argument('-p', '--password',
                        required=False,
                        action='store',
                        default='Root@123',
                        help='Password to use')

    parser.add_argument('-v', '--vm-name',
                        required=False,
                        action='store',
                        help='name of the vm')

    parser.add_argument('--uuid',
                        required=False,
                        action='store',
                        help='vmuuid of vm')

    parser.add_argument('--disk-type',
                        required=False,
                        action='store',
                        default='thin',
                        choices=['thick', 'thin'],
                        help='thick or thin')

    parser.add_argument('--disk-size',
                        required=False,
                        action='store',
                        default = 5,
                        help='Size of the disk')
    args = parser.parse_args()
    if not args.password:
        args.password = getpass.getpass(
            prompt='Enter password')
    return args

def get_appliance_ip(si):
    for v in si.content.rootFolder.customValue:
        for x in si.content.customFieldsManager.field:
            if x.name == "PrimaryIO.appliance" and x.key == v.key:
                return v.value

def add_disk(vm, si, disk_size, disk_type):
        spec = vim.vm.ConfigSpec()
        # get all disks on a VM, set unit_number to the next available
        unit_number = 0
        for dev in vm.config.hardware.device:
            if hasattr(dev.backing, 'fileName'):
                unit_number = int(dev.unitNumber) + 1
                # unit_number 7 reserved for scsi controller
                if unit_number == 7:
                    unit_number += 1
                if unit_number >= 16:
                    print("we don't support this many disks")
                    return
            if isinstance(dev, vim.vm.device.VirtualSCSIController):
                controller = dev
        # add disk here
        dev_changes = []
        new_disk_kb = int(disk_size) * 1024 * 1024
        disk_spec = vim.vm.device.VirtualDeviceSpec()
        disk_spec.fileOperation = "create"
        disk_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
        disk_spec.device = vim.vm.device.VirtualDisk()
        disk_spec.device.backing = \
            vim.vm.device.VirtualDisk.FlatVer2BackingInfo()
        if disk_type == 'thin':
            disk_spec.device.backing.thinProvisioned = True
        disk_spec.device.backing.diskMode = 'persistent'
        disk_spec.device.unitNumber = unit_number
        disk_spec.device.capacityInKB = new_disk_kb
        disk_spec.device.controllerKey = controller.key
        dev_changes.append(disk_spec)
        spec.deviceChange = dev_changes
        #vm.ReconfigVM_Task(spec=spec)
        #print("%sGB disk added to %s" % (disk_size, vm.config.name))
        val = vm.ReconfigVM_Task(spec=spec)
        print("%sGB disk added to %s" % (disk_size, vm.config.name))

def delete_virtual_disk(si, vm_obj, disk_number, language='Hard disk '):
   
    hdd_prefix_label = language
    if not hdd_prefix_label:
        raise RuntimeError('Hdd prefix label could not be found')

    hdd_label = hdd_prefix_label + str(disk_number)
    virtual_hdd_device = None
    for dev in vm_obj.config.hardware.device:
        if isinstance(dev, vim.vm.device.VirtualDisk) \
                and dev.deviceInfo.label == hdd_label:
            virtual_hdd_device = dev
    if not virtual_hdd_device:
        raise RuntimeError('Virtual {} could not '
                           'be found.'.format(virtual_hdd_device))

    virtual_hdd_spec = vim.vm.device.VirtualDeviceSpec()
    virtual_hdd_spec.operation = \
        vim.vm.device.VirtualDeviceSpec.Operation.remove
    virtual_hdd_spec.device = virtual_hdd_device

    spec = vim.vm.ConfigSpec()
    spec.deviceChange = [virtual_hdd_spec]
    task = vm_obj.ReconfigVM_Task(spec=spec)
    tasks.wait_for_tasks(si, [task])
    return True

def policy_operation(args, content, viewType, vmnames_args):
    vm_obj = get_obj(content, viewType, vmnames_args)
    add_disk(vm_obj, service_instance, args.disk_size, args.disk_type)
    print("Completed adding disk")
    
    vm_hardaware = vm_obj.config.hardware
    disk_obj_lst = []
    
    for device in vm_hardaware.device:
        if (device.key >= 2000) and (device.key < 3000):
            disk_obj_lst.append(device)

    vcenter = VCenter(args.host, args.user, args.password)
    virtual_device_spec = attach_vmdk(vm_obj, disk_obj_lst[-1], vcenter, cache_policy_kwargs)
    vm_config_spec.deviceChange.append(virtual_device_spec)
    reconfigure(vm_obj, vm_config_spec, wait=True)
    print('Attach_Complete')

    time.sleep(20)
    delete_virtual_disk(service_instance, vm_obj, disk_number)
    print("completed deleting disk")


def main():
    try:
        args = get_args()
        service_instance = connect.SmartConnectNoSSL(host=args.host,
                                                             user=args.user,
                                                             pwd=args.password,
                                                             port=int(args.port))

        atexit.register(connect.Disconnect, service_instance)

        content = service_instance.RetrieveContent()
        print("Connected to VCENTER SERVER !")
        container = content.rootFolder  # starting point to look into
        viewType = [vim.VirtualMachine]  # object types to look for
        recursive = True  # whether we should look into it recursively
        containerView = content.viewManager.CreateContainerView(container, viewType, recursive)
          
        #Getting Vcenter config objects
        children = containerView.view
        vm_config_spec = vim.vm.ConfigSpec()
        detach_vm_config_spec = vim.vm.ConfigSpec()

        
        appliance_ip = get_appliance_ip(service_instance)
        vm_summary = {}
        for child in children:
            create_vm_summary(child, vm_summary)

        vmnames_args = args.vm_name.split(',')[0] if len(args.vm_name.split(',')) == 1 else args.vm_name.split(',')
        policy_name = 'spbm_auto_policy_{0}'.format(datetime.datetime.today().strftime('%m%d_%H%M%S%f'))
        
        cache_policy_kwargs = {
                                           'policy_name': policy_name,
                                           'policy_desc' : 'policy_desc',
                                           'cache_policy' : str('WriteBack'),
                                           'apa' : "No",
                                           'replica' : str(0),
                                           'size' : int(20),
                                           'app_ip' : appliance_ip
                                          }
        
        if not isinstance(vmnames_args, list):
           

        elif isinstance(vmnames_args, list):
            for vmname, value  in vm_summary.items():
                   vmname = vmname.strip()
                if vmname in vm.for vm in vmnames_args:
                    vm_obj = get_obj(content, viewType, vmname)
                    add_disk(vm_obj, service_instance, args.disk_size, args.disk_type)
 
    except vmodl.MethodFault as error:
            print("Caught vmodl fault : " + error.msg)
            return -1

    return 0

if __name__ == '__main__':
    main()
