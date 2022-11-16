from pycistem.core import *

hosts= [
    "prague",
    "helsinki",
    "budapest",
    "palermo",
    "istanbul",
    "kyiv",
    "bucharest",
    "warsaw",
    "barcelona",
    "milano",
    "manchester",
    "sofia"
]

manager_command = "/groups/cryoadmin/software/CISTEM/2.0.0-alpha-70-d11eb1e/$command"
program_command = "/groups/elferich/cistem_binaries/$command"
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
rpm.WriteRunProfilesToDisk("/tmp/rr.txt",[0])