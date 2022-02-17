import struct
from dataclasses import astuple, fields
import socket
import time
import subprocess
import asyncio
import logging
from rich.logging import RichHandler
import secrets
import string
from pathlib import Path

from ..config import config

FORMAT = "%(message)s"
logging.basicConfig(
    level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)


from ._cistem_constants import *

def _encode_parameters(parameters):
    buffer = b''
    buffer += int(1).to_bytes(4,'little')
    buffer += len(fields(parameters)).to_bytes(4,'little')
    parameterstuple = astuple(parameters)
    for i,argument in enumerate(fields(parameters)):
        if argument.type == float:
            buffer += int(3).to_bytes(1,'little')
            buffer += struct.pack('<f', parameterstuple[i])
        if argument.type == bool:
            buffer += int(4).to_bytes(1,'little')
            buffer += parameterstuple[i].to_bytes(1,'little')
        if argument.type == str:
            buffer += int(1).to_bytes(1,'little')
            bb = parameterstuple[i].encode('utf-8')
            buffer += len(bb).to_bytes(4,'little')
            buffer += bb
        if argument.type == int:
            buffer += int(2).to_bytes(1,'little')
            buffer += struct.pack('<i', parameterstuple[i])
    return buffer

    
async def handle_manager(reader, writer, identity):
    logger = logging.getLogger("cisTEM Manager")
    addr = writer.get_extra_info('peername')
    #logger.info(f"{addr} connected to manager")
    writer.write(socket_please_identify)
    await writer.drain()
    data = await reader.read(16)
    if data != socket_sending_identification:
        logger.error(f"{addr!r} {data} is not {socket_sending_identification}")
        writer.close()
        return
    data = await reader.read(16)
    message= data.decode()
    if message != identity:
        logger.error(f"{addr!r} {message} is not {identity}: wrong process connected")
        writer.close()
        return
    writer.write(socket_you_are_a_worker)
    host = "localhost".encode('utf-8')
    writer.write(len(host).to_bytes(4,'little'))
    writer.write(host)
    port = "9397".encode('utf-8')
    writer.write(len(port).to_bytes(4,'little'))
    writer.write(port)
    await writer.drain()
    time.sleep(1)
    #logger.info(f"{addr} connected")
    writer.close()

async def handle_leader(reader, writer, buffers, signal_handlers,results):
    
    
    logger = logging.getLogger("cisTEM Leader")
    addr = writer.get_extra_info('peername')
    
    writer.write(socket_you_are_connected)
    await writer.drain()
    data = await reader.read(16)
    if data != socket_send_next_job:
        logger.error(f"{addr!r} did not request next job, instead sent {data}")
        writer.close()
        return
    data = await reader.read(8)
    #logger.info(f"{addr} sent {data} as dummy result")
    while len(buffers) > 0:
        my_parameter_i, buffer = buffers.pop(0)
        logger.info(f"Working on parameter set {my_parameter_i}")
        writer.write(socket_ready_to_send_single_job)
        writer.write(len(buffer).to_bytes(8,'little'))
        writer.write(buffer)
        await writer.drain()
        data = await reader.read(16)
        result = None
        if data in signal_handlers:
            #logger.info(f"{addr} sent {data} and I know what to do with it")
            result = await signal_handlers[data](reader,writer,logger)
            results.append(result)
        else:
            logger.error(f"{addr} sent {data} and I don't know what to do with it")
        data = await reader.read(16)
        if data != socket_send_next_job:
            logger.error(f"{addr!r} did not request next job, instead sent {data}")
            break
        data = await reader.read(16)
        #logger.info(f"{addr} sent {data} after requesting next results")
    logger.info(f"{addr} finished sending time to die")
    writer.write(socket_time_to_die)
    await writer.drain()
    data = await reader.read(16)
    #logger.info(f"{addr} sent {data}")
    data = await reader.read(16)
    #logger.info(f"{addr} sent {data}")
    data = await reader.read(16)
    #logger.info(f"{addr} sent {data}")
    writer.close()

def exec_program(cmd):
    logger = logging.getLogger("Launcher")
    logger.info(f"Launching {cmd}")
    res = subprocess.run(cmd,shell=True,capture_output=True)

async def run(executable,parameters,signal_handlers={},num_procs=1):
    loop = asyncio.get_event_loop()
    results = []
    buffers = []
    logger = logging.getLogger("cisTEM Program")
    HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
    PORT = 9399        # Port to listen on (non-privileged ports are > 1023)
    PORT_LEADER = 9397

    alphabet = string.ascii_letters + string.digits
    identity = ''.join(secrets.choice(alphabet) for i in range(16))
    buffers = [(i,_encode_parameters(parameter)) for i, parameter in enumerate(parameters)]

    logger.info(f"Secret is {identity}")

    server_manager = await asyncio.start_server(
        lambda r,w : handle_manager(r,w,identity), HOST, PORT)

    addrs = ', '.join(str(sock.getsockname()) for sock in server_manager.sockets)
    logger.info(f'Serving manager on {addrs}')

    server_leader = await asyncio.start_server(
        lambda r,w : handle_leader(r,w, buffers,signal_handlers,results), HOST, PORT_LEADER)

    addrs = ', '.join(str(sock.getsockname()) for sock in server_leader.sockets)
    logger.info(f'Serving leader on {addrs}')

    cmd = Path(config["CISTEM_PATH"]) / executable
    cmd = str(cmd)
    cmd += f' {HOST} {PORT} "{identity}" 1'
    #with concurrent.futures.ThreadPoolExecutor(max_workers=num_procs) as executor:
    #    futures = [
    #        loop.run_in_executor(executor, exec_program, cmd)
    #        for task in range(num_procs)
    #    ]
    #    logging.info(f"Launched {num_procs} processes")
    #try:
    #    results = await asyncio.gather(*futures, return_exceptions=False)
    #except Exception as ex:
    #    print("Caught error executing task", ex)
    #    raise
    
    futures_1 = [
            await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)
            for task in range(num_procs)
        ]
    logging.info(f"Launched {num_procs} processes")
    #proc = await asyncio.create_subprocess_shell(
    #    cmd,
    #    stdout=asyncio.subprocess.PIPE,
    #    stderr=asyncio.subprocess.PIPE)
    futures_2 = [
            future.communicate()
            for future in futures_1
        ]
    try:
        proc_results = await asyncio.gather(*futures_2, return_exceptions=False)
    except Exception as ex:
        print("Caught error executing task", ex)
        raise
    #logger.info(f'[{cmd!r} exited with {proc.returncode}]')
    #if stdout:
    #    logger.info(f'[stdout]\n')
    #if stderr:
    #    logger.error(f'[stderr]\n{stderr.decode()}')
    print(len(results))
    return(results)
    
   