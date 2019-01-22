import os
from fabric.api import run, hosts, cd, env,settings
import time


FIO_CMD = "fio --name=/data/test --ioengine=libaio --iodepth=4 --rw=randwrite --bs=32k --direct=0 --size=64m --numjobs=1"
CKSUM_CMD = "cksum /data/test.0.0"
def run_cmd(ip,user,password,cmd):
        #rc = os.system("eval `ssh-agent -s` && ssh-add")
        #print("rc: %s" %rc)
        #os.system("sudo restart ssh")
        #env.hosts = [ip]
        #env.password = password
        #env.user = user
        #env.host_string= ip
        with settings(host_string=ip,user=user,password=password,allow_agent=False ):
            result = run(cmd)

        return result



#print(do_fio("10.10.144.205","root","root123",FIO_CMD))
temp1 = run_cmd("10.10.96.81","root","root123",FIO_CMD)
#print(do_fio("10.10.144.205","root","root123",CKSUM_CMD))
#temp2 = do_fio("10.10.144.205","root","root123",CKSUM_CMD)

#print("Printing temp1 %s"%temp1)
#print("Printing temp2 %s"%temp2)
