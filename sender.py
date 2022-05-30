# Create a transport protocol on top of UDP that reads from a file and sends the contents of the file to the client.
from fileinput import filename
import socket
import hashlib
import argparse

def compute_checksum(packet):
    return hashlib.md5(packet.encode('utf-8')).hexdigest()


def udp_receive(serverSock):
    rcvd = ''
    while(True):
        data, addr = serverSock.recvfrom(1024)
        if len(data) > 0:
            rcvd = data.decode()
            break
    return rcvd


def udp_send(message, serverSock, iadr, port, isIntent = False):
    packet = message.encode()
    MD5 = compute_checksum(packet.decode())

    # Send Intent message to server
    if isIntent:
        serverSock.sendto(packet, (iadr, port))
        return
    # Include MD5 checksum in packet
    packet = f"{packet.decode()}{MD5}".encode()
    serverSock.sendto(packet, (iadr,port))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f")       # Argument for file name
    parser.add_argument("-a")       # Argument for IP address
    parser.add_argument("-s")       # Argument for receiver port number
    parser.add_argument("-c")       # Argument for sender port number
    parser.add_argument("-i")       # Argument for unique ID
    args = parser.parse_args()

    #! Set variables from args (UNCOMMENT FOR TESTING)
    # UDP_IP_ADDRESS = args.a
    # UDP_PORT_NO = int(args.s)
    # uniqueID = args.i
    # senderPort = int(args.c)
    # fileName = args.f

    UDP_IP_ADDRESS = "209.97.169.245"
    UDP_PORT_NO = 6789
    uniqueID = "c3563823"
    senderPort = 6789
    fileName = f"{uniqueID}.txt"


    # Initialize UDP connection
    clientSock = socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM)
    clientSock.bind(('',senderPort))


    # Read from file named "{uniqueID}.txt" and store to message
    message = ''
    with open(fileName, "r") as f:
        message = f.read()


    # Create packet and MD5 checksum
    intentMessage  =f"ID{uniqueID}"

    
    # Send Intent message to server
    udp_send(intentMessage, clientSock, UDP_IP_ADDRESS, UDP_PORT_NO, True)
    # Receive TxnID (accept message from server)
    TxnID = udp_receive(clientSock)

    #! FOR TESTING ONLY
    # Receive response from client 
    print(TxnID)







main()