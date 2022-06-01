# Create a transport protocol on top of UDP that reads from a file and sends the contents of the file to the client.
import socket
import argparse
from time import sleep


def udp_receive(serverSock):
    rcvd = ''
    data, addr = serverSock.recvfrom(1024)
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
    parser.add_argument("-s", help="Sender port number")
    parser.add_argument("-c", help="Receiver port number")
    parser.add_argument("-i", help="Unique ID")
    args = parser.parse_args()

    if args.a is None:
        args.a = "209.97.169.245"
    if args.s is None:
        args.s = 6789
    if args.c is None:
        args.c = 6789
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


def send_intent(intentMessage, clientSock, UDP_IP_ADDRESS, UDP_PORT_NO):
    # Receive TxnID (accept message from server)
    while(True):
        try:
            udp_send(intentMessage, clientSock, UDP_IP_ADDRESS, UDP_PORT_NO)
            TxnID = udp_receive(clientSock)
            return TxnID
        except socket.timeout:
            print("Timed out waiting for server")


def main():
    args = get_args()

    #! Set variables from args (UNCOMMENT FOR TESTING)
    UDP_IP_ADDRESS = args.a
    UDP_PORT_NO = int(args.s)
    uniqueID = args.i
    senderPort = int(args.c)
    fileName = args.f


    # Initialize UDP connection
    clientSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    clientSock.bind(('',senderPort))
    clientSock.settimeout(1)

    # Read from file named "{uniqueID}.txt" and store to message
    message = read_file(fileName)


    """
    Send Intent Message
    """
    # Send Intent message to server
    intentMessage  =f"ID{uniqueID}"
    TxnID = send_intent(intentMessage, clientSock, UDP_IP_ADDRESS, UDP_PORT_NO)
    print("TxnID: "+TxnID)


    """
    Send Packets
    # """
    # sequence_number = 0
    # i = 0
    # increment = 50
    # while i < len(message):
    #     # Determine data parameters: submessage, isLast, seqNum
    #     submessage = message[i:i+increment]
    #     sequence_number = 0 if sequence_number == 10000000 else sequence_number
    #     isLast = 0 if i+increment < len(message) else 1
        
    #     # Begin sending message 
    #     data = f"ID{uniqueID}SN{str(sequence_number).zfill(7)}TXN{TxnID}LAST{isLast}{submessage}"
    #     udp_send(data, clientSock, UDP_IP_ADDRESS, UDP_PORT_NO)
    #     sleep(0.1)
    #     """
    #     Receive ACK
    #     """
    #     # Receive ACK
    #     while(True):
    #         try:
    #             ack = udp_receive(clientSock)
    #             break
    #         except socket.timeout:
    #             print("Timed out waiting for server")
        
    #     print(ack)
    #     sequence_number += 1
    #     i+=increment
        







main()