from pycistem.programs._cistem_constants import *
import socket

# Connect to localhost on port 3000
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("localhost", 3000))

# Send the data
s.sendall(socket_remote_control)
