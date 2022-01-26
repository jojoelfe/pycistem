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

    logger.info("Pointed executable to leader, closing the connection")
    writer.close()

async def handle_leader(reader, writer, buffer, signal_handlers,results):
    logger = logging.getLogger("cisTEM Leader")
    addr = writer.get_extra_info('peername')

    writer.write(socket_you_are_connected)
    await writer.drain()
    data = await reader.read(16)
    if data != socket_send_next_job:
        logger.error(f"{addr!r} did not request next job")
        writer.close()
        return
    data = await reader.read(8)
    logger.info(f"{addr} sent {data} as dummy result")
    writer.write(socket_ready_to_send_single_job)
    writer.write(len(buffer).to_bytes(8,'little'))
    writer.write(buffer)
    await writer.drain()
    data = await reader.read(16)
    result = None
    if data in signal_handlers:
        logger.info(f"{addr} sent {data} and I know what to do with it")
        result = await signal_handlers[data](reader,writer,logger)
        results.append(result)
    writer.write(socket_time_to_die)
    await writer.drain()
    data = await reader.read(16)
    logger.info(f"{addr} sent {data}")
    data = await reader.read(16)
    logger.info(f"{addr} sent {data}")
    data = await reader.read(16)
    logger.info(f"{addr} sent {data}")
    writer.close()

async def run(executable,parameters,signal_handlers={}):
    results = []
    logger = logging.getLogger("cisTEM Program")
    HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
    PORT = 9399        # Port to listen on (non-privileged ports are > 1023)
    PORT_LEADER = 9397

    alphabet = string.ascii_letters + string.digits
    identity = ''.join(secrets.choice(alphabet) for i in range(16))
    buffer = _encode_parameters(parameters)

    logger.info(f"Secret is {identity}")

    server_manager = await asyncio.start_server(
        lambda r,w : handle_manager(r,w,identity), HOST, PORT)

    addrs = ', '.join(str(sock.getsockname()) for sock in server_manager.sockets)
    logger.info(f'Serving manager on {addrs}')

    server_leader = await asyncio.start_server(
        lambda r,w : handle_leader(r,w, buffer,signal_handlers,results), HOST, PORT_LEADER)

    addrs = ', '.join(str(sock.getsockname()) for sock in server_leader.sockets)
    logger.info(f'Serving leader on {addrs}')

    logger.info(f'Launching executable')

    cmd = Path(config["CISTEM_PATH"]) / executable
    cmd = str(cmd)
    cmd += f' {HOST} {PORT} "{identity}" 1'
    
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await proc.communicate()

    logger.info(f'[{cmd!r} exited with {proc.returncode}]')
    if stdout:
        logger.info(f'[stdout]\n')
    if stderr:
        logger.error(f'[stderr]\n{stderr.decode()}')
    return(results)
    
    #async with server:
    #    await server.serve_forever()
    
    
def baba():    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        p = subprocess.Popen("/groups/elferich/cisTEM/build/tilt_series_assemble_Intel-gpu-debug/src/applyctf localhost 9399 2121212122121212 1", stdout=subprocess.PIPE, shell=True)
                ## Talk with date command i.e. read data from stdout and stderr. Store this info in tuple ##
                ## Interact with process: Send data to stdin. Read data from stdout and stderr, until end-of-file is reached.  ##
                ## Wait for process to terminate. The optional input argument should be a string to be sent to the child process, ##
                ## or None, if no data should be sent to the child.
                # send you are worker
        conn, addr = s.accept()
        with conn:
            print('Connected by', addr)
            # Request identity
            conn.sendall(socket_please_identify,socket.MSG_WAITALL)
            #conn.sendall(b'2121212122121212',socket.MSG_WAITALL)
            
            # Should receieve gC2CeZWNb2GPv5qh (Sending identityt)
            
            code = conn.recv(16,socket.MSG_WAITALL)
            # Should receieve the 16-byte code given as a third argument to the executable 
            jobid = conn.recv(16,socket.MSG_WAITALL)
            print(code)
            print(id)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s2:
                s2.bind((HOST, 9397))
                s2.listen()
        
                conn.sendall(socket_you_are_a_worker,socket.MSG_WAITALL)
                bb = "localhost".encode('utf-8')
                conn.sendall(len(bb).to_bytes(4,'little'),socket.MSG_WAITALL)
                conn.sendall(bb,socket.MSG_WAITALL)
                bb = "9397".encode('utf-8')
                conn.sendall(len(bb).to_bytes(4,'little'),socket.MSG_WAITALL)
                conn.sendall(bb,socket.MSG_WAITALL)
                conn2, addr2 = s2.accept()
                with conn2:
                    print('Connected by', addr2)
                    conn2.sendall(socket_you_are_connected,socket.MSG_WAITALL)
                    print(conn2.recv(16,socket.MSG_WAITALL))
                    print(conn2.recv(8,socket.MSG_WAITALL))
                    # Sending code to prepare for recieval of job information
                    conn2.sendall(socket_ready_to_send_single_job,socket.MSG_WAITALL)

                    #Next send 8 bytes indicating how long the job package will be
                    conn2.sendall(len(buffer).to_bytes(8,'little'))
                    conn2.sendall(buffer)
                    print(conn2.recv(16,socket.MSG_WAITALL))


    (output, err) = p.communicate()
