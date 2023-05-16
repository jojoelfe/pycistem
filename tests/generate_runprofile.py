from pycistem.core import *

hosts= [
    "host1",
    "host2",
    "host3",
    "host4",
    "host5",
    "host6",
    "host7",
    "host8",
]

manager_command = "/software/CISTEM/$command"
program_command = "/software/CISTEM/$command"
num_threads =2
delay=100
rpm = RunProfileManager()
# 96 GPus
rp = RunProfile()
rp.name = "96GPUs"
rp.manager_command = manager_command
rp.RemoveAll()
for host in hosts:
    for igpu in range(0,8):
        rp.AddCommand(f'ssh -f {host} "unset CUDA_VISIBLE_DEVICES && export CUDA_VISIBLE_DEVICES={igpu} && {program_command}"',1,num_threads,False,0,delay)
rpm.AddProfile(rp)

rp = RunProfile()
rp.name = "88GPUs"
rp.manager_command = manager_command
rp.RemoveAll()
for host in hosts[1:]:
    for igpu in range(0,8):
        rp.AddCommand(f'ssh -f {host} "unset CUDA_VISIBLE_DEVICES && export CUDA_VISIBLE_DEVICES={igpu} && {program_command}"',1,num_threads,False,0,delay)
rpm.AddProfile(rp)

rp = RunProfile()
rp.name = "48GPUs (1)"
rp.manager_command = manager_command
rp.RemoveAll()
for host in hosts[:6]:
    for igpu in range(0,8):
        rp.AddCommand(f'ssh -f {host} "unset CUDA_VISIBLE_DEVICES && export CUDA_VISIBLE_DEVICES={igpu} && {program_command}"',1,num_threads,False,0,delay)
rpm.AddProfile(rp)

rp = RunProfile()
rp.name = "40GPUs (1)"
rp.manager_command = manager_command
rp.RemoveAll()
for host in hosts[1:6]:
    for igpu in range(0,8):
        rp.AddCommand(f'ssh -f {host} "unset CUDA_VISIBLE_DEVICES && export CUDA_VISIBLE_DEVICES={igpu} && {program_command}"',1,num_threads,False,0,delay)
rpm.AddProfile(rp)

rp = RunProfile()
rp.name = "48GPUs (2)"
rp.manager_command = manager_command
rp.RemoveAll()
for host in hosts[6:]:
    for igpu in range(0,8):
        rp.AddCommand(f'ssh -f {host} "unset CUDA_VISIBLE_DEVICES && export CUDA_VISIBLE_DEVICES={igpu} && {program_command}"',1,num_threads,False,0,delay)
rpm.AddProfile(rp)

rp = RunProfile()
rp.name = "32GPUs (1)"
rp.manager_command = manager_command
rp.RemoveAll()
for host in hosts[:4]:
    for igpu in range(0,8):
        rp.AddCommand(f'ssh -f {host} "unset CUDA_VISIBLE_DEVICES && export CUDA_VISIBLE_DEVICES={igpu} && {program_command}"',1,num_threads,False,0,delay)
rpm.AddProfile(rp)

rp = RunProfile()
rp.name = "32GPUs (2)"
rp.manager_command = manager_command
rp.RemoveAll()
for host in hosts[4:8]:
    for igpu in range(0,8):
        rp.AddCommand(f'ssh -f {host} "unset CUDA_VISIBLE_DEVICES && export CUDA_VISIBLE_DEVICES={igpu} && {program_command}"',1,num_threads,False,0,delay)
rpm.AddProfile(rp)

rp = RunProfile()
rp.name = "32GPUs (3)"
rp.manager_command = manager_command
rp.RemoveAll()
for host in hosts[8:]:
    for igpu in range(0,8):
        rp.AddCommand(f'ssh -f {host} "unset CUDA_VISIBLE_DEVICES && export CUDA_VISIBLE_DEVICES={igpu} && {program_command}"',1,num_threads,False,0,delay)
rpm.AddProfile(rp)

rpm.WriteRunProfilesToDisk("/tmp/rp.txt",[0,1,2,3,4,5,6,7])
