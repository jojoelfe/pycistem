
host_gpu_info = {
    "kyiv": 8,
    "warsaw": 8,
}

def generate_local_gpu_prefix(num_gpus):
    for gpu in range(num_gpus):
        yield f'CUDA_VISIBLE_DEVICES={gpu} '

def generate_gpu_prefix(host_gpu_info):
    for host in host_gpu_info:
        for gpu in range(host_gpu_info[host]):
            yield f'ssh {host} "CUDA_VISIBLE_DEVICES={gpu} '

def generate_num_procs(host_gpu_info):
    return sum(host_gpu_info.values())
