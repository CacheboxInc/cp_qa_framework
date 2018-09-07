##################################
#
# TBD : This file is temporary and all values to move to a common MRC suite 
# config file. Having too many config files and variables to enter is always a 
# bad idea. Presently, this is only present to facilitate faster trunaround for 
# number of TCs.
#
###################################

# Default : Disabled. Fail the the first TC failure of the suite.
abortfirst = 0
# Excute tests in parallel on local cores and also in cluster of test ndoes.
burstmode = 0
# Duration needs to be in the same format as required by FIO
runtime = '1'
# Use Existing test setup Or Create new one. Default : 0 : Use existing, 1: Create new setup
createsetup = 0
# Do a dry run of the MRC suite and list all config values and TCs to run.
# 0 : is trun if off.
# 1 : Turn on. List only.
showconfig = 0

# runtests : This takes a list of specific TCs to execute, this is good make suites 
# out of collection of TCs. One can run a set of failing TCs with this option.
# Default : All, run all the test cases in the suite or the framework can find.
runtest = []

# Which config file to use with the test suite.
# The default behavior is to use an exisiting config file, at a predefined location.
# If there is a requirement to change the config with present run then this option
# can be used.
use_config = 'default'
# REST specific, endpoints(restit).
GET_VMS_STATS_URL             = 'get_vms_stats'
GET_VMDK_RECOMMENDATION_URL   = 'get_vmdk_recommendation'
APA_STATS_URL                 = 'apa/stats'
GET_STATS_URL                 = 'get_stats'
GET_VM_INFO                   = 'get_vm_info'
APA_VM_STATS_URL              = 'get_vm_apa_stats'
GET_VMDK_BENEFITS_URL         = 'get_vmdk_benefit'
