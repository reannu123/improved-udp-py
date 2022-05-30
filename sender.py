# Create a transport protocol on top of UDP that reads from a file and sends the contents of the file to the client.
import socket
import random
import hashlib

def compute_checksum(packet):
    return hashlib.md5(packet.encode('utf-8')).hexdigest()


UDP_IP_ADDRESS = "209.97.169.245"
UDP_PORT_NO = 6789
uniqueID = "c3563823"

# Initialize UDP connection
serverSock = socket.socket(
    socket.AF_INET,
    socket.SOCK_DGRAM)

# Read from file named "message.txt" and store to message
with open(f"{uniqueID}.txt", "r") as f:
    message = f.read()


# Create packet and MD5 checksum
packet = f"ID{uniqueID}".encode()
MD5 = compute_checksum(packet.decode())

# Send Intent message to client
serverSock.sendto(packet, (UDP_IP_ADDRESS,UDP_PORT_NO))


