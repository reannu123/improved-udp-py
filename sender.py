# Create a transport protocol on top of UDP that reads from a file and sends the contents of the file to the client.
import socket
import argparse
from time import time



def udp_receive(clientSock):
    rcvd = ''
    data, addr = clientSock.recvfrom(1024)
    if len(data) > 0:
        rcvd = data.decode()
    return rcvd


def udp_send(message, clientSock, iadr, port):
    packet = message.encode()
    clientSock.sendto(packet, (iadr, port))


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", help="File name")
    parser.add_argument("-a", help="IP address")
    parser.add_argument("-s", help="Receiver port number")
    parser.add_argument("-c", help="Sender port number")
    parser.add_argument("-i", help="Unique ID")
    args = parser.parse_args()

    if args.a is None:
        # 209.97.169.245
        # 10.0.7.141
        args.a = "10.0.7.141"
    if args.s is None:
        args.s = 9000
    if args.c is None:
        args.c = 6706
    if args.i is None:
        args.i = "c3563823"
    if args.f is None:
        args.f = f"{args.i}.txt"

    return args


def read_file(file_name):
    try:
        with open(file_name, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return None


def write_file(file_name, message):
    with open(file_name, 'w') as f:
        f.write(message)

def send_intent(intentMessage, clientSock, UDP_IP_ADDRESS, UDP_PORT_NO):
    # Receive TxnID (accept message from server)
    while(True):
        try:
            udp_send(intentMessage, clientSock, UDP_IP_ADDRESS, UDP_PORT_NO)
            # Measure the time it takes to receive the TxnID
            TxnID = udp_receive(clientSock)
            return TxnID
        except socket.timeout:
            print("Timed out waiting for server")


def send_packets(uniqueID,TxnID,message, clientSock, UDP_IP_ADDRESS, UDP_PORT_NO):
    sequence_number = 0
    idx = 0                         # Message index
    chunkSize = 1                   # Initial Chunk size
    
    while idx < len(message):
        """
        Sending Packets
        """
        # Determine data parameters: submessage, isLast, seqNum
        submessage = message[idx:idx+chunkSize]
        sequence_number = 0 if sequence_number == 10000000 else sequence_number
        isLast = 0 if idx+chunkSize < len(message) else 1

        # Begin sending message 
        data = f"ID{uniqueID}SN{str(sequence_number).zfill(7)}TXN{TxnID}LAST{isLast}{submessage}"
        startTime = time()
        udp_send(data, clientSock, UDP_IP_ADDRESS, UDP_PORT_NO)
        idx+=chunkSize
        sequence_number += 1


        """
        Receive ACK
        """
        # Receiving Loop
        while(True):
            try:
                ack = udp_receive(clientSock)
                endTime = time()
                diff = endTime-startTime
                if sequence_number == 1:
                    clientSock.settimeout(diff+1)
                    chunkSize = estimate_chunk_size(len(message), diff)
                    break
            except socket.timeout:
                print("Timed out waiting for server")
                if sequence_number > 1:
                    chunkSize -=1


def estimate_chunk_size (file_size, timeout):
    expectedTime = 85
    numofPackets = int(expectedTime/timeout)
    chunkSize = int(file_size/numofPackets)
    # Calculate the chunk size
    return chunkSize


def main():
    args = get_args()

    # Set variables from args
    UDP_IP_ADDRESS = args.a
    UDP_PORT_NO = int(args.s)
    uniqueID = args.i
    senderPort = int(args.c)
    fileName = args.f


    # Initialize UDP connection
    clientSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    clientSock.bind(('',senderPort))
    clientSock.settimeout(5)

    # Read from file named "{uniqueID}.txt" and store to message
    message = read_file(fileName)


    """
    Send Intent Message
    """
    # Send Intent message to server
    intentMessage  =f"ID{uniqueID}"
    TxnID = send_intent(intentMessage, clientSock, UDP_IP_ADDRESS, UDP_PORT_NO)
    if TxnID == "Existing alive transaction":
        return
    else:
        write_file(f"txnID.txt", TxnID)


    """
    Send Packets
    """
    
    send_packets(uniqueID,TxnID,message, clientSock, UDP_IP_ADDRESS, UDP_PORT_NO)





main()