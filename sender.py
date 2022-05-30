# Create a transport protocol on top of UDP that reads from a file and sends the contents of the file to the client.
from fileinput import filename
import socket
import argparse



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
    serverSock.sendto(packet, (iadr, port))


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
    uniqueID = "CS143145"
    senderPort = 6789
    fileName = f"{uniqueID}.txt"


    # Initialize UDP connection
    clientSock = socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM)
    clientSock.bind(('',senderPort))


    # Read from file named "{uniqueID}.txt" and store to message
    message = ''
    try:
        with open(fileName, "r") as f:
            message = f.read()
    except:
        pass
        # print("File not found")


    # Send Intent message to server
    intentMessage  =f"ID{uniqueID}"
    udp_send(intentMessage, clientSock, UDP_IP_ADDRESS, UDP_PORT_NO, True)
    # Receive TxnID (accept message from server)
    TxnID = udp_receive(clientSock)

    # TODO - Loop this for every chunk of the packet
    # Begin sending message 
    sequence_number = str(0).zfill(7)
    submessage = "YU"
    isLast = 0
    data = f"ID{uniqueID}SN{sequence_number}TXN{TxnID}LAST{isLast}{submessage}"
    udp_send(data, clientSock, UDP_IP_ADDRESS, UDP_PORT_NO, False)

    #! Testing only
    received = udp_receive(clientSock)
    print(received)







main()