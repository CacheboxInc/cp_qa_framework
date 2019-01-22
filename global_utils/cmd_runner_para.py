import sys
import paramiko
import os

FIO_CMD = "fio --name=/data/test --ioengine=libaio --iodepth=4 --rw=randwrite --bs=32k --direct=0 --size=64m --numjobs=1"
CKSUM_CMD = "cksum /data/test.0.0"


def run_cmd(hostname, username, password,cmd): 
	#os.system("eval `ssh-agent -s` && ssh-add")

	ssh = paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	ssh.connect(hostname=hostname, username=username, password=password, allow_agent=False)
	stdin, stdout, stderr = ssh.exec_command(cmd)
	#print(stdout.read())
	return(stdout.read())
	ssh.close()


temp2 = run_cmd("10.10.96.81","root","root123",CKSUM_CMD)
#tempi = run_cmd("10.10.96.81","root","root123",FIO_CMD)
print(temp2)
