import logging
import ssl
import time

from vim_utils import *
#from supervisor.utils.config import *

#from helpers.common import *

from pyVmomi import pbm
import urllib.parse

PIOANALYZER_DEFAULT_PROFILE_NAME = "default_spbm_profile"
PIOANALYZER_DEFAULT_PROFILE_DESC = "SPBM Policy created by Automation Testing framework"

DEFAULT_OPTIMIZE_POLICY = "WriteBack"
DEFAULT_OPTIMIZE_POLICY_DESC = "PIO-Analyzer auto policy generated when optimizing VMDK."
DEFAULT_OPTIMIZE_REPLICA_COUNT = "1"

PRAAPA_POLICY = "policy"
PRAAPA_APA = "apa"
PRAAPA_REPLICA = "replica"
PRAAPA_SIZE = "size"
PRAAPA_APP_IP = "applianceIp"

logger = logging.getLogger("poller")

class PBMUtils(object):

    def __init__(self, vcenter, kwargs = {}):
        self.vcenter = vcenter
        self.si = None
        self.content = None
        self.policy_name = kwargs.get('policy_name', PIOANALYZER_DEFAULT_PROFILE_NAME)
        self.policy_defination = kwargs.get('policy_desc', PIOANALYZER_DEFAULT_PROFILE_DESC)
        self.cache_policy = kwargs.get('cache_policy', "WriteBack")
        self.apa = kwargs.get('apa', "No")
        self.replica = kwargs.get('replica', "0")
        self.size = kwargs.get('size', 20)
        self.app_ip = kwargs.get('app_ip', "0")
        self.create_connection()

    def __get_vcenter_cookie(self):
        cookie = None
        vim_stub = self.vcenter.si._GetStub()
        for c in vim_stub.cookie.split(";"):
            tmp = c.split("=")
            if len(tmp) > 1:
                if tmp[0].strip().lower() == "vmware_soap_session":
                    cookie = tmp[1].strip()
                    break

        return cookie

    def __connect(self):
        cookie = self.__get_vcenter_cookie()
        assert cookie is not None
        context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        context.verify_mode = ssl.CERT_NONE
        try:
            stub = connect.SoapStubAdapter(self.vcenter.ip, 443,
                                           version="pbm.version.version2",
                                           path="/pbm", certKeyFile=None,
                                           certFile=None, thumbprint=None,
                                           sslContext=context,
                                           requestContext={"vcSessionCookie": cookie})
        except TypeError:
            # older versions didn't have sslContext as a keyword
            stub = connect.SoapStubAdapter(self.vcenter.ip, 443,
                                           version="pbm.version.version2",
                                           path="/pbm", certKeyFile=None,
                                           certFile=None, thumbprint=None,
                                           requestContext={"vcSessionCookie": cookie})

        self.si = pbm.PbmServiceInstance("ServiceInstance", stub)
        self.content = self.si.PbmRetrieveServiceContent()

    def create_connection(self):
        try:
            self.__connect()
        except:
            self.vcenter.connect()
            self.__connect()

    def get_profile_by_profile_id(self, profile_id):
        profiles = self.content.profileManager.PbmRetrieveContent(profileIds=[profile_id])
        if len(profiles) != 1:
            return None

        return profiles[0]

    def get_pbm_resource_type(self):
        resourcetype = pbm.profile.ResourceType()
        resourcetype.resourceType = pbm.profile.ResourceTypeEnum.STORAGE
        return resourcetype

    def create_default_profile(self, resource_type):
        cat_info = None
        metadata = self.content.profileManager.PbmFetchCapabilityMetadata(resourceType=resource_type)
        for cat in metadata:
            for c in cat.capabilityMetadata:
                if c.id.id.startswith(SUPPORTED_ID):
                    cat_info = c
                    break

        if cat_info is None:
            raise Exception("Could not find PrimaryIO Filter Driver. Please verify if PrimaryIO APA is installed on clusters.")

        rule = pbm.capability.ConstraintInstance()
        for prop_meta in cat_info.propertyMetadata:
            prop = pbm.capability.PropertyInstance()
            prop.id = prop_meta.id
            if prop_meta.id.startswith(PRAAPA_POLICY):
                prop.value = self.cache_policy
            elif prop_meta.id.startswith(PRAAPA_APA):
                prop.value = self.apa
            elif prop_meta.id.startswith(PRAAPA_REPLICA):
                prop.value = self.replica
            elif prop_meta.id.startswith(PRAAPA_SIZE):
                prop.value = self.size
            elif prop_meta.id.startswith(PRAAPA_APP_IP):
                prop.value = self.app_ip

            rule.propertyInstance.append(prop)

        capability = pbm.capability.CapabilityInstance()
        capability.id = cat_info.id
        capability.constraint.append(rule)

        sub_profile = pbm.profile.SubProfileCapabilityConstraints.SubProfile()
        sub_profile.capability.append(capability)

        constraint = pbm.profile.SubProfileCapabilityConstraints()
        sub_profile.name = "Rule-Set %s" % (len(constraint.subProfiles) + 1)

        constraint.subProfiles.append(sub_profile)

        spec = pbm.profile.CapabilityBasedProfileCreateSpec()
        spec.name = self.policy_name
        spec.resourceType = resource_type
        spec.description = self.policy_defination
        spec.constraints = constraint

        profile_id = self.content.profileManager.PbmCreate(spec)
        return profile_id

    def get_supported_profile(self):
        resource_type = self.get_pbm_resource_type()
        profile_ids = self.content.profileManager.PbmQueryProfile(resourceType=resource_type)
        profiles = self.content.profileManager.PbmRetrieveContent(profileIds=profile_ids)
        for profile in profiles:
            if profile.name.startswith(self.policy_name):
                return profile

        profile_id = self.create_default_profile(resource_type)
        if profile_id is None:
            raise Exception("Could not create SPBM. Please verify if PrimaryIO APA is installed on clusters.")

        profiles = self.content.profileManager.PbmRetrieveContent(profileIds=[profile_id])
        if len(profiles) != 1:
            raise Exception("Supported SPBM not found. Please verify if PrimaryIO APA is installed on clusters.")

        return profiles[0]

    def get_vmdk_storage_policies(self, vm, profile_unique_ids):
        result = []
        vmdks = GuestVM(vm).get_vmdks()
        for vmdk in vmdks:

            objRef = pbm.ServerObjectRef()
            objRef.serverUuid = self.vcenter.content.about.instanceUuid
            objRef.objectType = pbm.ServerObjectRef.ObjectType.virtualDiskId
            objRef.key = "%s:%s" % (vm._GetMoId(), str(vmdk.key))
            profile_id = self.content.profileManager.PbmQueryAssociatedProfile(objRef)

            for p_id in profile_id:
                if p_id.uniqueId in profile_unique_ids:
                    # only if it's supported profile
                    result.append((vmdk.key, p_id))

        return result

    def get_vm_vmdk_storage_policies(self, vm):
        resource_type = self.get_pbm_resource_type()
        profile_ids = self.content.profileManager.PbmQueryProfile(resourceType=resource_type)
        profile_unique_ids = [p.uniqueId for p in profile_ids]

        result = self.get_vmdk_storage_policies(vm, profile_unique_ids)
        return result

    def get_cluster_vms_and_corresponding_spbm(self, cluster):
        vms = self.vcenter.get_list_of_vms_using_filter(cluster, SUPPORTED_ID)
        result = []

        for vm in vms:
            result.append({
                          'obj' : vm,
                          'disks': self.get_vm_vmdk_storage_policies(vm)
                          })

        return result

    def get_upgrade_supported_policies(self):
        """
        Returns a list of unique profile IDs which are for praapa and policy type
        isn't passthrough and has replica count = 0
        """
        resource_type = self.get_pbm_resource_type()
        profile_ids = self.content.profileManager.PbmQueryProfile(resourceType=resource_type)

        upgrade_profile_ids = []

        for profile_id in profile_ids:
            try:
                profile = self.get_profile_by_profile_id(profile_id)
                if profile is None:
                    continue

                policy_details = {}
                for p in profile.constraints.subProfiles[0].capability[0].constraint[0].propertyInstance:
                    if p.id == 'policy':
                        policy_details['apa_policy'] = p.value
                    elif p.id == 'replica':
                        policy_details['apa_replica_count'] = p.value

                if policy_details['apa_policy'].lower() == "passthrough":
                    continue

                if int(policy_details['apa_replica_count']) > 0:
                    continue
            except:
                continue

            upgrade_profile_ids.append(profile_id.uniqueId)

        return upgrade_profile_ids

    def get_upgrade_cluster_vms_and_corresponding_spbm(self, cluster):
        """
        Only return the virtual machines and disks with disks which do not have
        passthrough policy and have replica count as 0 (L0R1 or L1R0) mode.

        No action is required in case the filter policy is passthrough or if
        the replica count is greater than 0. The VAIO code should be able to handle
        migrations and should work if one of the replica is uncertain.
        """
        vms = self.vcenter.get_list_of_vms_using_filter(cluster, SUPPORTED_ID)
        profile_unique_ids = self.get_upgrade_supported_policies()
        result = []

        for vm in vms:
            disks = self.get_vmdk_storage_policies(vm, profile_unique_ids)
            if len(disks) > 0:
                result.append({
                              'obj' : vm,
                              'disks': self.get_vmdk_storage_policies(vm, profile_unique_ids)
                              })

        return result

    def get_upgrade_policies_with_replicas(self):
        """
        Returns a list of unique profile IDs which are for praapa and policy type
        isn't passthrough and has replica count = 0
        """
        resource_type = self.get_pbm_resource_type()
        profile_ids = self.content.profileManager.PbmQueryProfile(resourceType=resource_type)

        upgrade_profile_ids = []

        for profile_id in profile_ids:
            try:
                profile = self.get_profile_by_profile_id(profile_id)
                if profile is None:
                    continue

                policy_details = {}
                for p in profile.constraints.subProfiles[0].capability[0].constraint[0].propertyInstance:
                    if p.id == 'policy':
                        policy_details['apa_policy'] = p.value
                    elif p.id == 'replica':
                        policy_details['apa_replica_count'] = p.value

                if policy_details['apa_policy'].lower() == "passthrough":
                    continue

                if int(policy_details['apa_replica_count']) == 0:
                    continue
            except:
                continue

            upgrade_profile_ids.append(profile_id.uniqueId)

        return upgrade_profile_ids

    def get_upgrade_cluster_vms_and_corresponding_with_replica_spbm(self, cluster):
        """
        Only return the virtual machines and disks with disks which do not have
        passthrough policy and have replica count as 0 (L0R1 or L1R0) mode.

        No action is required in case the filter policy is passthrough or if
        the replica count is greater than 0. The VAIO code should be able to handle
        migrations and should work if one of the replica is uncertain.
        """
        vms = self.vcenter.get_list_of_vms_using_filter(cluster, SUPPORTED_ID)
        profile_unique_ids = self.get_upgrade_policies_with_replicas()
        result = []

        for vm in vms:
            disks = self.get_vmdk_storage_policies(vm, profile_unique_ids)
            if len(disks) > 0:
                result.append({
                              'obj' : vm,
                              'disks': self.get_vmdk_storage_policies(vm, profile_unique_ids)
                              })

        return result

    def get_policy_value(self, profile_id):
        policy = ""

        profile = self.get_profile_by_profile_id(profile_id)
        if profile is None:
            return policy

        try:
            for p in profile.constraints.subProfiles[0].capability[0].constraint[0].propertyInstance:
                if p.id == 'policy':
                    policy = p.value
                    break
        except:
            pass

        return policy

    def get_attach_vmdk_spec(self, vmdk, cache_policy_kwargs):
        self.policy_name = cache_policy_kwargs.get('policy_name', PIOANALYZER_DEFAULT_PROFILE_NAME)
        self.policy_defination = cache_policy_kwargs.get('policy_desc', PIOANALYZER_DEFAULT_PROFILE_DESC)
        self.cache_policy = cache_policy_kwargs.get('cache_policy', "WriteBack")
        self.apa = cache_policy_kwargs.get('apa', "No")
        self.replica = cache_policy_kwargs.get('replica', "0")
        self.size = cache_policy_kwargs.get('size', 20)
        self.app_ip = cache_policy_kwargs.get('app_ip', "0")

        profile = self.get_supported_profile()

        if profile is None:
            raise Exception("Could not find supported SPBM. Please check if PrimaryIO is installed.")

        vm_profile_spec = vim.vm.DefinedProfileSpec()
        vm_profile_spec.profileId = profile.profileId.uniqueId

        virtual_device_spec = vim.vm.device.VirtualDiskSpec()
        virtual_device_spec.device = vmdk
        virtual_device_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.edit
        virtual_device_spec.profile.append(vm_profile_spec)

        return virtual_device_spec

    def get_deattach_vmdk_spec(self, vmdk):
        vm_profile_spec = vim.vm.EmptyProfileSpec()

        virtual_device_spec = vim.vm.device.VirtualDiskSpec()
        virtual_device_spec.device = vmdk
        virtual_device_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.edit
        virtual_device_spec.profile.append(vm_profile_spec)

        return virtual_device_spec

    def get_cluster_cache_configured(self, cluster):
        # get all the hosts that are present within the current 
        # cluster and get the size of cache available (in Bytes)
        cache_available = 0
        hosts_configured = 0
        host_cache_details = []
        for host in cluster.host:
            if host.runtime.vFlashResourceRuntimeInfo is not None:
                hosts_configured += 1
                host_cache_free  = host.runtime.vFlashResourceRuntimeInfo.freeForVmCache
                cache_available += host_cache_free
                tmp = ("%s (%sGB)" % (host.name, host_cache_free >> 30))
                host_cache_details.append(tmp)

        return cache_available, hosts_configured, host_cache_details

    def cluster_attach_policies(self, cluster_name, vm_vmdk_map, cache_policy, policy_desc, replica_count):
        """
        This function is only going to apply the set cache_policy to all the
        vmdk that have been selected for the vms
        """ 
        attach_tasks = {'status' : -1, 'message': 'Failed to apply policy'}
        vm_not_found = []
        vm_attach_failed = []
        vm_detach_specs = {}
        vm_detach_tasks = {}
        vm_attach_specs = {}
        vm_attach_tasks = {}
        vm_vmdk_mouuid = {}
        cache_req = 0
        try:
            cluster = self.vcenter.get_obj([vim.ClusterComputeResource], cluster_name)
            if cluster is None:
                attach_tasks['message'] = "Cluster %s not found" % cluster_name
                return attach_tasks

            for vm_name in list(vm_vmdk_map.keys()):
                vm = self.vcenter.get_obj([vim.VirtualMachine], vm_name)
                if vm is None:
                    vm_not_found.append(vm_name)
                    continue

                vm_vmdk_mouuid[vm] = []
                vmdk_policies = vm_vmdk_map.get(urllib.parse.unquote(vm.name))

                vm_config_spec = vim.vm.ConfigSpec()
                detach_vm_config_spec = vim.vm.ConfigSpec()

                local_vm_obj = GuestVM(vm)
                vmdks = local_vm_obj.get_vmdks()

                for vmdk in vmdks:
                    vmdk_label = vmdk.deviceInfo.label
                    vmdk_size = int(vmdk.capacityInKB) >> 20 # in GB
                    if vmdk_size >= 8192:
                        # policy on VMDK with cache size 8TB not supported
                        continue

                    vmdk_policy = vmdk_policies.get(vmdk_label)
                    if vmdk_policy is None:
                        # This VMDK was not selected for optimization
                        continue

                    cache_size = vmdk_policy.get("cache_size") # in GB
                    block_size = vmdk_policy.get("block_size") # in KB

                    if cache_size < 2:
                        # cache size < 2 GB is not supported
                        cache_size = 2

                    if cache_size > 1000:
                        # cache size >= 1000 GB is not supported
                        cache_size = 1000

                    disk_cache_size_perc = int((int(cache_size) * 100) / vmdk_size)

                    if disk_cache_size_perc > 100:
                        disk_cache_size_perc = 99

                    if disk_cache_size_perc < 5:
                        disk_cache_size_perc = 5

                    # re-adjust cache size based on the disk_cache_size_perc
                    cache_size = vmdk_size * (disk_cache_size_perc/ 100)
                    cache_req += (cache_size * (int(replica_count) + 1))

                    policy_name = "pio_%s_%s_%s_%s" % (cache_policy, "No", replica_count, disk_cache_size_perc)

                    cache_policy_kwargs = {
                                           'policy_name': policy_name,
                                           'policy_desc' : policy_desc,
                                           'cache_policy' : str(cache_policy),
                                           'apa' : "No",
                                           'replica' : str(replica_count),
                                           'size' : int(disk_cache_size_perc),
                                           'app_ip' : PIO_IP
                                          }

                    detach_virtual_device_spec = self.get_deattach_vmdk_spec(vmdk)
                    detach_vm_config_spec.deviceChange.append(detach_virtual_device_spec)

                    virtual_device_spec = self.get_attach_vmdk_spec(vmdk, cache_policy_kwargs)
                    vm_config_spec.deviceChange.append(virtual_device_spec)

                    vm_vmdk_mouuid[vm].append(get_mouuid(self.vcenter, vmdk))

                vm_detach_specs[vm] = detach_vm_config_spec
                vm_attach_specs[vm] = vm_config_spec

            # For cache policy which isn't passthrough, check if we have enough cache size
            # within the cluster to accomodate the request. If not raise exception.
            cache_available, hosts_configured, host_cache_details = self.get_cluster_cache_configured(cluster)

            cache_available = cache_available >> 30

            if hosts_configured < int(replica_count) + 1:
                if hosts_configured == 0:
                    hosts_configured = 1

                attach_tasks["status"] = -2
                attach_tasks["message"] = "Not enough nodes have flash to create cache: requested %s \
                                           copies, have %s." % (replica_count, hosts_configured - 1)
                return attach_tasks

            if cache_available < cache_req:
                attach_tasks["status"] = -2
                attach_tasks["message"] = "Not enough free flash capacity to create cache: requested %s \
                                           GB per copy, %s copies. Cache free details - %s" % (cache_req,\
                                           replica_count, ', '.join(host_cache_details))
                return attach_tasks

            attach_tasks["status"] = 0

            for vm in vm_detach_specs:
                # detach only if we have enough cache to accomodate the request
                detach_vm_config_spec = vm_detach_specs[vm]
                vm_detach_tasks[vm] = local_vm_obj.reconfigure(detach_vm_config_spec, wait=False)

            for vm in list(vm_detach_tasks.keys()):
                task = vm_detach_tasks.get(vm)
                task_status = wait_for_task(task)
                if task_status["status"] == ERROR:
                    # detach is failing, so would attach
                    del(vm_attach_specs[vm])
                    vm_attach_failed.append(urllib.parse.unquote(vm.name))
                    attach_tasks["status"] = -1
                    continue

                for uuid in vm_vmdk_mouuid.get(vm):
                    disk_obj = ProfileDB.get(uuid, False)
                    disk_obj.uuid = uuid
                    disk_obj.state = PROFILED
                    disk_obj.save()

            vm_attach_spec_keys = list(vm_attach_specs.keys())
            vm_attach_spec_keys.reverse()

            # sleep for 5 seconds, seeing lot of locking issues when applying apa
            time.sleep(5)

            for vm in vm_attach_spec_keys:
                vm_config_spec = vm_attach_specs.get(vm)
                vm_attach_tasks[vm] = local_vm_obj.reconfigure(vm_config_spec, wait = False)

            for vm in list(vm_attach_tasks.keys()):
                task = vm_attach_tasks.get(vm)
                task_status = wait_for_task(task)
                if task_status["status"] == ERROR:
                    # attach failed, reason would be tasks
                    vm_attach_failed.append(vm.name)
                    attach_tasks["status"] = -1
                    continue

                for uuid in vm_vmdk_mouuid.get(vm):
                    disk_obj = ProfileDB.get(uuid, False)
                    disk_obj.uuid = uuid
                    disk_obj.state = OPTIMIZING
                    disk_obj.save()

            attach_tasks["vm_not_found"] = vm_not_found
            attach_tasks["vm_attach_failed"] = vm_attach_failed
        except Exception as err:
            import traceback
            traceback.print_exc()

        return attach_tasks

    def cluster_detach_policies(self, cluster_name, vm_vmdk_map):
        detach_tasks = {'status' : -1, 'message': 'Failed to detach policy'}
        vm_not_found = []
        vm_detach_failed = []
        vm_detach_tasks = {}
        vm_attach_specs = {}
        vm_attach_tasks = {}
        vm_vmdk_mouuid = {}
        try:
            cluster = self.vcenter.get_obj([vim.ClusterComputeResource], cluster_name)
            if cluster is None:
                detach_tasks['message'] = "Cluster %s not found" % cluster_name
                return detach_tasks

            for vm_name in list(vm_vmdk_map.keys()):
                vm = self.vcenter.get_obj([vim.VirtualMachine], vm_name)
                if vm is None:
                    vm_not_found.append(vm_name)
                    continue

                vm_vmdk_mouuid[vm] = []
                vmdk_policies = vm_vmdk_map.get(vm.name)

                vm_config_spec = vim.vm.ConfigSpec()
                detach_vm_config_spec = vim.vm.ConfigSpec()

                local_vm_obj = GuestVM(vm)
                vmdks = local_vm_obj.get_vmdks()

                for vmdk in vmdks:
                    vmdk_label = vmdk.deviceInfo.label
                    vmdk_size = int(vmdk.capacityInKB) >> 20 # in GB
                    vmdk_policy = vmdk_policies.get(vmdk_label)
                    if vmdk_policy is None:
                        # This VMDK was not selected for optimization
                        continue

                    cache_policy_kwargs = {
                                           'policy_name': PIOANALYZER_DEFAULT_PROFILE_NAME,
                                           'policy_desc' : PIOANALYZER_DEFAULT_PROFILE_DESC,
                                           'cache_policy' : "PassThrough",
                                           'apa' : "No",
                                           'replica' : "0",
                                           'size' : 10, # not used
                                           'app_ip' : PIO_IP
                                          }

                    detach_virtual_device_spec = self.get_deattach_vmdk_spec(vmdk)
                    detach_vm_config_spec.deviceChange.append(detach_virtual_device_spec)

                    virtual_device_spec = self.get_attach_vmdk_spec(vmdk, cache_policy_kwargs)
                    vm_config_spec.deviceChange.append(virtual_device_spec)

                    vm_vmdk_mouuid[vm].append(get_mouuid(self.vcenter, vmdk))

                vm_detach_tasks[vm] = local_vm_obj.reconfigure(detach_vm_config_spec, wait=False)
                vm_attach_specs[vm] = vm_config_spec

            detach_tasks["status"] = 0

            for vm in list(vm_detach_tasks.keys()):
                task = vm_detach_tasks.get(vm)
                task_status = wait_for_task(task)
                if task_status["status"] == ERROR:
                    # detach is failing, so would attach
                    del(vm_attach_specs[vm])
                    vm_detach_failed.append(urllib.parse.unquote(vm.name))
                    detach_tasks["status"] = -1
                    continue

                for uuid in vm_vmdk_mouuid.get(vm):
                    disk_obj = ProfileDB.get(uuid, False)
                    disk_obj.uuid = uuid
                    disk_obj.state = PROFILED
                    disk_obj.save()

            vm_attach_spec_keys = list(vm_attach_specs.keys())
            vm_attach_spec_keys.reverse()

            # sleep for 5 seconds, seeing lot of locking issues when applying apa
            time.sleep(5)

            for vm in vm_attach_spec_keys:
                # again attach passthrough, should be always monitoring
                vm_config_spec = vm_attach_specs.get(vm)
                vm_attach_tasks[vm] = local_vm_obj.reconfigure(vm_config_spec, wait = False)

            for vm in list(vm_attach_tasks.keys()):
                task = vm_attach_tasks.get(vm)
                task_status = wait_for_task(task)
                if task_status["status"] == ERROR:
                    # attach failed, reason would be tasks
                    vm_detach_failed.append(urllib.parse.unquote(vm.name))
                    detach_tasks["status"] = -1
                    continue

                for uuid in vm_vmdk_mouuid.get(vm):
                    disk_obj = ProfileDB.get(uuid, False)
                    disk_obj.uuid = uuid
                    disk_obj.state = DETAILED
                    disk_obj.save()

            detach_tasks["vm_not_found"] = vm_not_found
            detach_tasks["vm_detach_failed"] = vm_detach_failed
        except Exception as err:
            import traceback
            traceback.print_exc()

        return detach_tasks
