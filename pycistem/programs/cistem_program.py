import asyncio
import logging
import secrets
import socket
import string
import struct
import subprocess
import time
from dataclasses import astuple, fields
from pathlib import Path
from time import sleep

import psutil


def get_ip_addresses(family):
    for interface, snics in psutil.net_if_addrs().items():
        for snic in snics:
            if snic.family == family:
                yield (interface, snic.address)

HOST = ",".join([a[1] for a in get_ip_addresses(socket.AF_INET)])


from pycistem.config import config

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


from pycistem.programs._cistem_constants import *


def _encode_parameters(parameters):
    # creates a cisTEM compatible buffer from the parameters class
    buffer = b""
    buffer += int(1).to_bytes(4,"little")
    buffer += len(fields(parameters)).to_bytes(4,"little")
    parameterstuple = astuple(parameters)
    for i,argument in enumerate(fields(parameters)):
        if argument.type == float:
            buffer += int(3).to_bytes(1,"little")
            buffer += struct.pack("<f", parameterstuple[i])
        if argument.type == bool:
            buffer += int(4).to_bytes(1,"little")
            buffer += parameterstuple[i].to_bytes(1,"little")
        if argument.type == str:
            buffer += int(1).to_bytes(1,"little")
            bb = parameterstuple[i].encode("utf-8")
            buffer += len(bb).to_bytes(4,"little")
            buffer += bb
        if argument.type == int:
            buffer += int(2).to_bytes(1,"little")
            buffer += struct.pack("<i", parameterstuple[i])
    return buffer


async def handle_manager(reader, writer, identity, port):
    # Handles initial connection from the executable and directs them to the leader
    addr = writer.get_extra_info("peername")
    #logger.info(f"{addr} connected to manager")
    writer.write(socket_please_identify)
    await writer.drain()
    data = await reader.readexactly(16)
    if data != socket_sending_identification:
        log.error(f"{addr!r} {data} is not {socket_sending_identification}")
        writer.close()
        return
    data = await reader.readexactly(16)
    message= data.decode()
    if message != identity:
        log.error(f"{addr!r} {message} is not {identity}: wrong process connected")
        writer.close()
        return
    writer.write(socket_you_are_a_worker)
    host = HOST.encode("utf-8")
    writer.write(len(host).to_bytes(4,"little"))
    writer.write(host)
    port = str(port).encode("utf-8")
    writer.write(len(port).to_bytes(4,"little"))
    writer.write(port)
    await writer.drain()
    time.sleep(1)
    #logger.info(f"{addr} connected")
    writer.close()

async def handle_leader(reader, writer, buffers, signal_handlers,results):
    log_str = ""
    # Handles connections from the executable asking for work

    addr = writer.get_extra_info("peername")

    writer.write(socket_you_are_connected)
    await writer.drain()
    data = await reader.readexactly(16)
    if data != socket_send_next_job:
        log.error(f"{addr!r} did not request next job, instead sent {data}")
        writer.close()
        return
    data = await reader.readexactly(8)
    #logger.info(f"{addr} sent {data} as dummy result")
    while len(buffers) > 0:
        print(f"Working on parameter set {len(buffers)}")
        parameter_index, buffer = buffers.pop(0)
        log.debug(f"Working on parameter set {parameter_index}")
        writer.write(socket_ready_to_send_single_job)
        writer.write(len(buffer).to_bytes(8,"little"))
        writer.write(buffer)
        await writer.drain()

        # check length of signal_handlers
        if len(signal_handlers) > 0:
            cont = True
            while cont:
                data = await reader.readexactly(16)
                result = None
                if data != socket_job_result_queue:
                    cont = False
                else:
                    await signal_handlers[data](reader,writer,log)
                    log_str += "J"
                    continue
                if data in signal_handlers:
                    #logger.info(f"{addr} sent {data} and I know what to do with it")
                    result = await signal_handlers[data](reader,writer,log)
                    results.append((parameter_index,result))
                    log_str += "R"
                else:
                    log.error(f"{addr} sent {data} and I don't know what to do with it, really {log_str}")

                    #logger.error(f"{buffer}")
                    break
        cont = True
        while cont:
            if socket_send_next_job not in signal_handlers:
                data = await reader.readexactly(16)
                if data != socket_send_next_job:
                    if data == socket_job_result_queue:
                        res = await signal_handlers[data](reader,writer,log)
                        log_str += "j"
                        continue
                    else:
                        log.error(f"{addr!r} did not request next job, instead sent {data}")
                data = await reader.readexactly(8)
                log_str += "N"
                cont = False
                #logger.info(f"{addr} sent {data} after requesting next results")
            else:
                cont = False
    log.debug(f"{addr} finished, sending time to die")
    writer.write(socket_time_to_die)
    await writer.drain()
    data = await reader.read(16)
    #logger.info(f"{addr} sent {data}")
    data = await reader.read(16)
    #logger.info(f"{addr} sent {data}")
    data = await reader.read(16)
    #logger.info(f"{addr} sent {data}")
    
    writer.close()


async def run(executable: str,parameters,signal_handlers={},num_procs=1,num_threads=1, cmd_prefix="", cmd_suffix="", save_output=False, save_output_path="",sleep_time=0.1):
    results = []
    buffers = []
    # Set HOST to curretn ip address
    #'127.0.0.1'  # Standard loopback interface address (localhost)

    # Create secret to identify workers
    alphabet = string.ascii_letters + string.digits
    identity = "".join(secrets.choice(alphabet) for i in range(16))
    buffers = [(i,_encode_parameters(parameter)) for i, parameter in enumerate(parameters)]
    log.debug(f"Secret is {identity}")

    # Start the leader
    start_port = 3000
    leader_started = False
    while not leader_started:
        try:
            server_leader = await asyncio.start_server(
                lambda r,w : handle_leader(r,w, buffers,signal_handlers,results), "", start_port, family=socket.AF_INET)
            leader_started = True
            start_port += 1
        except OSError:
            log.debug(f"Port {start_port} already in use, trying next port")
            start_port += 1
            if start_port > 4000:
                msg = "No ports available"
                raise OSError(msg)
    port_leader = server_leader.sockets[0].getsockname()[1]
    addrs = ", ".join(str(sock.getsockname()) for sock in server_leader.sockets)
    log.debug(f"Serving leader on {addrs}")

    # Start the manager
    manager_started = False
    while not manager_started:
        try:
            server_manager = await asyncio.start_server(
                lambda r,w : handle_manager(r,w,identity,port_leader), "",start_port, family=socket.AF_INET)
            manager_started = True
        except OSError:
            log.debug(f"Port {start_port} already in use, trying next port")
            start_port += 1
            if start_port > 4000:
                msg = "No ports available"
                raise OSError(msg)
    port_manager = server_manager.sockets[0].getsockname()[1]
    addrs = ", ".join(str(sock.getsockname()) for sock in server_manager.sockets)
    log.debug(f"Serving manager on {addrs}")


    # Starting workers
    cmd = str(Path(config["CISTEM_PATH"]) / executable)
    cmd += f" {HOST} {port_manager} {identity} {num_threads}"

    # Test if cmd_prefix is iterable
    if type(num_procs) == int and type(cmd_prefix) == str:
        cmd_prefix = [cmd_prefix for i in range(num_procs)]

    if type(num_procs) == int and type(cmd_suffix) == str:
        cmd_suffix = [cmd_suffix for i in range(num_procs)]



    launch_futures = []
    if type(num_procs) == int:
        tasks = [cmd_prefix[i] + cmd +cmd_suffix[i] for i in range(num_procs)]
    elif type(num_procs) == RunProfile:
        tasks = []
        num_procs.SubstituteExecutableName(executable)
        for rc in num_procs.run_commands:
            for _i in range(rc.number_of_copies):
                tasks.append(rc.command_to_run)

    for task in tasks:
        launch_futures.append(await asyncio.create_subprocess_shell(
        task,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE))
        sleep(sleep_time)

    logging.debug(f"Launched {num_procs} processes")

    result_futures = [
            future.communicate()
            for future in launch_futures
        ]
    try:
        proc_results = await asyncio.gather(*result_futures, return_exceptions=False)
    except Exception as ex:
        print("Caught error executing task", ex)
        raise
    if save_output:
        for i, result in enumerate(proc_results):
            with open(save_output_path + f"_{i}.txt", "w") as f:
                f.write(result[0].decode("utf-8"))
            if len(result[1]) > 0:
                with open(save_output_path + f"_{i}_error.txt", "w") as f:
                    f.write(result[1].decode("utf-8"))
    return(results)

