###################################################################
#
# This is the usuability interface for the CP Automation framework.
# There is no major requirements to get started and the framework
# setups or reuses whatever without failing fast. The process of running 
# test suites/cases should be painless and not cumbersome.
#
# It should be easy to add/intergrate new test suite, the framework in all 
# its simplicity, is just a wrapper to run almost all programs and test tools.
# For example : Look at CP unit test integration. 
#
# CP framework will abstract all the test setup and running in parallel or on
# remote seamlessly and mostly transparent to the user. 
#
##################################################################

# importing the required modules
import os
os.system("pip3 install -r tools/requirements.txt")
import argparse
from argparse import RawTextHelpFormatter
import sys

# Test Framework Libraries
from unit_suite.lib_tcs import unit_tests
from ui_suite.lib_tcs import ui_tests
from sanity_suite.lib_tcs import sanity_tests
from perf_suite.lib_tcs import perf_tests
import cp_global
        
# Why am i spending so much time on help messages ? USUABILITY
# For the sake of usuability, READMEs are great but humans dont read.
# If there are barrier to get started with the tool, humana loose interest to something 'simpler'
# Most of the frameworks and tools grow too complex, over time, to be usuable and involve learning curve.
#
# All test framework need to be friendly enough and itntelligent enough to just get the tests running.
# Hence, just taking user input as --unit and running all unit tests is a design consideration.

def main():
        # Lets figure out what needs to be done. What testing needs to be done.
        parser = argparse.ArgumentParser(description = "CP Automation test manager \
                                At your service !" ,formatter_class=RawTextHelpFormatter)
        parser.add_argument("--unit", help = "This option will Run all CP Unit tests. \
                                \nThe latest git unit test code is checked out. Use --runtests, --hosts & --duration \
                            \nNOTE : Beginners, please pay attention error messages to Get You Started.\n\n", action="store_true")
        parser.add_argument("--sanity", help = "This option will Run all CP sanity tests.\n\n", action="store_true")
        parser.add_argument("--scalability", help = "CP scalibility tests are run using Locust tool. \
                                \nUse this option for stress tests and to setup test bed.\n\n", action="store_true")
        parser.add_argument("--ui", help="It runs UI test cases using selenium.\n\n", action="store_true")
        parser.add_argument("--performance", help="TBD: Run performance tests\n\n", action="store_true")
        parser.add_argument("--showconfig", help="TBD:Show the default config values being used for the test.\n", action="store_true")
        parser.add_argument("--showTC", help="TBD: Describe the given TCs and its coverage areas.\n", action="store_true")
        parser.add_argument("--runtest", help="This option helps to run specific TCs, range of TCs and All TCs. \
                                \nEx: --runtest all, --runtest TC1-TC10 or --runtest TC1,TC2,TC3\n\n", action="store_true")
        parser.add_argument("--duration", help="TBD: Specify the duration of test run. \
                                \nEx: --duration 12mintues, --duration 1hour, --duration 1day\n\n", action="store_true")
        parser.add_argument("--burstmode", help="This is scale-in/out framework mode running tests concurrently on localhost \
                                \nand distributing among all test slaves. This option is experimental and optional. \
                                \nNOTE: Unit component tests are good candidates for this option.\n\n", action="store_true")
        parser.add_argument("--failfirst", help="By Default, the framework will abort at the first failure. \
                                \nUse this flag to ignore TC failures and execute entire suite.", action="store_true") 

        args = parser.parse_args()

        #Installing dependecies using pip
        #TBD Install those tools which are required for test suite to run
        #os.system("pip3 install -r tools/requirements.txt")

        if args.unit:
                print ("Call unit test cases related test cases\n")
                unit_tests.init_unit()
        elif args.sanity:
                print (" Call Sanity related test cases\n")
                sanity_tests.init_sanity()
        elif args.ui:
                print (" Call UI related test cases\n")
                ui_tests.init_ui()
        elif args.scalability:
                print ("TBD: Call Locust.io to do CP scalibility testing.\n")
        #elif args.recommendations:
        #        print ("TBD: Include recommendations, benefits TCs.\n")
        elif args.performance:
                print ("Running performance related testcases\n")
                perf_tests.init_perf()
        elif args.failfirst:
                print ("FAILFIRST")
                exit(1)
        else: 
                if len(sys.argv)==1:
                        parser.print_help(sys.stderr)


if __name__ == "__main__":
        # calling the main function
        main()

