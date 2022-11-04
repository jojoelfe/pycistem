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
    # creates a cisTEM compatible buffer from the parameters class
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
    # Handles initial connection from the executable and directs them to the leader
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
    # Handles connections from the executable asking for work
    
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
        parameter_index, buffer = buffers.pop(0)
        logger.info(f"Working on parameter set {parameter_index}")
        writer.write(socket_ready_to_send_single_job)
        writer.write(len(buffer).to_bytes(8,'little'))
        writer.write(buffer)
        await writer.drain()
        
        # check length of signal_handlers
        if len(signal_handlers) > 0:
            data = await reader.read(16)
            result = None
            logger.info(f"Waiting for signal handler")
            if data in signal_handlers:
                #logger.info(f"{addr} sent {data} and I know what to do with it")
                result = await signal_handlers[data](reader,writer,logger)
                results.append((parameter_index,result))
            else:
                logger.error(f"{addr} sent {data} and I don't know what to do with it, really")
                #logger.error(f"{buffer}")
                break
        data = await reader.read(16)
        if data != socket_send_next_job:
            logger.error(f"{addr!r} did not request next job, instead sent {data}")
            break
        data = await reader.read(16)
        #logger.info(f"{addr} sent {data} after requesting next results")
    logger.info(f"{addr} finished, sending time to die")
    writer.write(socket_time_to_die)
    await writer.drain()
    data = await reader.read(16)
    #logger.info(f"{addr} sent {data}")
    data = await reader.read(16)
    #logger.info(f"{addr} sent {data}")
    data = await reader.read(16)
    #logger.info(f"{addr} sent {data}")
    writer.close()


async def run(executable,parameters,signal_handlers={},num_procs=1,num_threads=1):
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
    cmd += f' {HOST} {PORT} "{identity}" {num_threads}'
    
    
    launch_futures = [
            await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)
            for task in range(num_procs)
        ]
    logging.info(f"Launched {num_procs} processes")
    
    result_futures = [
            future.communicate()
            for future in launch_futures
        ]
    try:
        proc_results = await asyncio.gather(*result_futures, return_exceptions=False)
    except Exception as ex:
        print("Caught error executing task", ex)
        raise
    return(results)
    
   