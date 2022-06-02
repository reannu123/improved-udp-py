# Create a transport protocol on top of UDP that reads from a file and sends the contents of the file to the client.
import socket
import argparse
from time import sleep,time
import hashlib

def compute_checksum(packet):
    return hashlib.md5(packet.encode('utf-8')).hexdigest()


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


# Function for estimating the size based on procTime and payloadSize
def estimate_chunk_size (payloadSize, procTime):
    expectedTime = 100
    numofPackets = int(expectedTime/procTime)
    chunkSize = int(payloadSize/numofPackets)
    return chunkSize


def send_intent(intentMessage, clientSock, UDP_IP_ADDRESS, UDP_PORT_NO):
    # Receive TxnID (accept message from server)
    while(True):
        try:
            udp_send(intentMessage, clientSock, UDP_IP_ADDRESS, UDP_PORT_NO)
            # Measure the time it takes to receive the ACK
            start = time()
            TxnID = udp_receive(clientSock)
            end = time()
            print(f"Time elapsed: {end-start}")
            return TxnID
        except socket.timeout:
            print("Timed out waiting for server")

# Function for checking whether it is possible to to succeed
def willSucceed(ProjectStart, timeOut,remPayload, chunkSize, procTime):
    timeLeft = timeOut - (time() - ProjectStart)
    packets_left = remPayload/chunkSize
    neededTime = packets_left * procTime
    if timeLeft > neededTime:
        return True
    return False


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
    ProjectStart = time()
    print("TxnID: "+TxnID)
    print()
    if TxnID == "Existing alive transaction":
        TxnID = read_file(f"txnID.txt")
        return
    else:
        write_file(f"txnID.txt", TxnID)



    """
    Send Packets
    """
    sequence_number = 0
    idx = 0                       # Message index
    chunkSize = 20               # Anticipate accepted increment size
    queueSize = 1               # Anticipate queue size
    queue = 0
    
    iChunkSize = chunkSize
    isMeasuring = False
    increaseFlag = False
    decreaseFlag = False
    packetSizes = [1,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30,32,34,36,38,40,42,44,46,48,50,52,54,56,58,60,62,64,66,68,70,72,74,76]
    packetSizes = [i for i in range(1,75)]
    # packetSizes = [1,2,4,8,16,32,64,128]
    packetSizeIdx = 0
    minWrongSize = 99999

    timeOuts = []
    startTime = 0
    while idx < len(message):
        """
        Sending Loop
        """
        

        while queue<queueSize:
            # Determine data parameters: submessage, isLast, seqNum
            submessage = message[idx:idx+chunkSize]
            sequence_number = 0 if sequence_number == 10000000 else sequence_number
            isLast = 0 if idx+chunkSize < len(message) else 1
            print(f"                                  PACKET {sequence_number}                      ")
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            # Begin sending message 
            data = f"ID{uniqueID}SN{str(sequence_number).zfill(7)}TXN{TxnID}LAST{isLast}{submessage}"
            print(f"Sqnc:\t\t{sequence_number}")
            print(f"Size:\t\t{chunkSize}")
            print("Message:\t" + submessage)
            startTime = time()
            udp_send(data, clientSock, UDP_IP_ADDRESS, UDP_PORT_NO)
            queue+=1
            idx+=chunkSize
            sequence_number += 1


        """
        Receive ACK
        """
        received = 0
        receiveSize = queueSize
        while received < receiveSize:
            # Receiving Loop
            while(True):
                try:
                    ack = udp_receive(clientSock)
                    endTime = time()
                    diff = endTime-startTime
                    timeOuts.append(diff)
                    
                    """ 
                    Experimental packet: 
                        -begin measuring
                        -set timeout from experiment
                        -set Chunksize to default
                        -set queue size to default
                    """
                    if sequence_number == 1:
                        isMeasuring = True
                        clientSock.settimeout(diff+1)
                        iChunkSize = chunkSize
                        chunkSize = estimate_chunk_size(len(message), diff)
                        queueSize = 1
                        break
                    
                    """
                    Increase Packet size if okay (and was not decreased)
                    """
                    # Chunk size okay, can increase
                    if isMeasuring:
                        print("\nMEASURING: \tChunk size fine\n")
                        iChunkSize = chunkSize
                        newChunkSize = chunkSize + packetSizes[packetSizeIdx]
                        while newChunkSize >=minWrongSize:
                            if packetSizeIdx == 0:
                                newChunkSize = chunkSize
                                isMeasuring = False
                                break
                            packetSizeIdx-=1
                            newChunkSize = chunkSize + packetSizes[packetSizeIdx]
                        chunkSize = newChunkSize
                        packetSizeIdx += 1
                    break

                except socket.timeout:
                    endTime = time()
                    print("~~~~Timed out waiting for server~~~~")
                    if sequence_number == 1:
                        chunkSize = chunkSize//2
                    # Chunk Size too Big, decrease
                    if isMeasuring:
                        minWrongSize = min(minWrongSize, chunkSize)
                        if packetSizeIdx == 1:
                            isMeasuring = False
                        print("\nMEASURING: \tCHUNK SIZE TOO BIG\n")
                        idx-=chunkSize*queueSize        # resend previous packet
                        sequence_number -= queueSize
                        packetSizeIdx = 0
                        decreaseFlag = True
                        if sequence_number == 1:
                            chunkSize -= chunkSize//5
                        else:
                            chunkSize = (chunkSize+iChunkSize)//2
                        
                        break

            print(f"Proc Time: \t{round(endTime-startTime,2)} seconds")
            print("ACK:\t\t" + ack[21:])
            print(f"Elapsed:\t{round(startTime - ProjectStart,2)} seconds")
            remPayload = len(message) - idx
            print("Remain: \t" + str(max(0,remPayload)) + " bytes")
            print("Succeed 120: \t" + str(willSucceed(ProjectStart, 120,remPayload, chunkSize, sum(timeOuts)/len(timeOuts))))
            print("Succeed 95: \t" + str(willSucceed(ProjectStart, 95,remPayload, chunkSize, sum(timeOuts)/len(timeOuts))))
            received += 1
            queue = 0
            print("--------------------------------------------------------------------------------")

    # Print Final Transaction Metrics
    print()
    print("TOTAL TIME: \t"+str(time()-ProjectStart))
    print("Ave Proc Time: \t" + str(sum(timeOuts)/len(timeOuts)))
    print("TxnID: \t\t"+TxnID)
    print("Max Size: \t"+str(chunkSize))
    print("Payload Size: \t"+str(len(message)))





main()