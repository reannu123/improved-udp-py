import socket
from time import time
from tools import *


def udp_receive(clientSock: socket.socket)->str:
    """
    Receive a message from the server

    Args:
        - clientSock (socket.socket): UDP socket

    Returns:
        str: Message received from the server
    """
    rcvd = ''
    data, addr = clientSock.recvfrom(1024)
    if len(data) > 0:
        rcvd = data.decode()
    return rcvd



def udp_send(message:str, clientSock:socket.socket, iadr:str, port:str)->None:
    """
    Send a message to the server

    Args:
        - message (str): message to be sent
        - clientSock (socket.socket): UDP socket
        - iadr (str): IP address of the server
        - port (str): port number of the server

    """
    packet = message.encode()
    clientSock.sendto(packet, (iadr, port))



def send_intent(intentMessage:str, clientSock:socket.socket, receiverIP:str, receiverPort:int)->str:
    """
    Send an intent message to the server
    
    Args:
        - intentMessage: intent message to be sent
        - clientSock: UDP socket
        - receiverIP: IP address of the server
        - receiverPort: port number of the server
    
    Returns:
        - int: ID of the transaction
    """
    # Send intent message
    udp_send(intentMessage, clientSock, receiverIP, receiverPort)
    start = time()
    tries = 0
    while(True):
        try:
            TxnID = udp_receive(clientSock)
            end = time()
            print(f"Time elapsed: {end-start}")
            return TxnID
        except socket.timeout:
            if tries >=3:
                print("Server is not responding")
                exit()
            print(f"Timed out waiting for server. Waiting for {clientSock.gettimeout()*(3-tries)} seconds")
            tries += 1



def getTxnID(clientSock:socket.socket, receiverIP:str, receiverPort:int, uniqueID:str)->str:
    """ Get the Transaction ID from the server by sending an intent. The transaction ID
    will also be stored in txnID.txt

    Args:
        - clientSock (socket.socket): UDP socket
        - receiverIP (str): IP address of the server
        - receiverPort (int): port number of the server
        - uniqueID (str): unique ID of the sender

    Returns:
        - str: Transaction ID
    """
    intentMessage  =f"ID{uniqueID}"
    TxnID = send_intent(intentMessage, clientSock, receiverIP, receiverPort)

    if TxnID == "Existing alive transaction":
        print(TxnID)
        exit()
        
    else:
        write_file(f"txnID.txt", TxnID)
    return TxnID



def dl_payload(uniqueID:str, vpc:int = 2)->bool:
    """ Download the payload from the server based in given unique ID

    Args:
        - uniqueID (str): the unique ID of the sender
        - vpc (int): which vpc to connect to

    Returns:
        - bool: return True if the payload is successfully downloaded, False otherwise
    """
    if vpc == 1:
        url = f"http://3.0.248.41:5000/get_data?student_id={uniqueID}"
    if vpc == 2:
        url = f"http://54.169.121.89:5000/get_data?student_id={uniqueID}"
    return dl_file(f"{uniqueID}.txt", url)
    



def willSucceed(timerStart:float, target:float, remPayload:int, chunkSize:int, procTime:float)->bool:
    """
    Check whether it is possible to succeed sending the remaining payload in
    the specified time based on the current chunk size and processing time

    Args:
        - timerStart (float): start time of sending the payload
        - target (float): the target duration of the transmission
        - remPayload (int): remaining bytes of the payload
        - chunkSize (int): number of bytes in a chunk
        - procTime (float): processing time of a valid packet

    Returns:
        - bool: True if it is possible to achieve sending all packets within the target duration, 
        False otherwise
    """
    timeLeft = target - (time() - timerStart)
    packets_left = remPayload/chunkSize
    neededTime = packets_left * procTime
    if timeLeft > neededTime:
        return True, neededTime, timeLeft
    return False, neededTime, timeLeft



def start_UDP(senderPort:int)->socket.socket:
    """
    Create a UDP socket and bind it to the specified port

    Args:
        senderPort (int): port number of the sender

    Returns:
        socket.socket: UDP socket
    """
    clientSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    clientSock.bind(('',senderPort))
    clientSock.settimeout(5)
    return clientSock



def estimate_chunk_size (payloadSize:int, procTime:float, expectedTime:int)->int:
    """
    Estimate the required size of the chunk based on the payload size, processing time and expected time

    Args:
        - payloadSize: size of the payload
        - procTime: processing time of a valid packet
        - expectedTime: expected time

    Returns: 
        - int: size of the chunk
    """
    numofPackets = expectedTime/procTime
    chunkSize = int(payloadSize/numofPackets)
    return chunkSize



def startTransaction(receiverIP, receiverPort, senderID,senderPort, payloadName):
    

    # Initialize UDP connection
    clientSock = start_UDP(senderPort)

    # Read from file named "{uniqueID}.txt" and store to message
    message = read_file(payloadName)
    if message == None:
        print("File not found.")
        exit()

    """
    Send Intent Message
    """
    TxnID = getTxnID(clientSock, receiverIP, receiverPort, senderID)
    printToFile("captures/"+TxnID,"Txn: " + TxnID)
    ProjectStart = time()


    """
    Send Packets
    """
    sequence_number = 0
    idx = 0                       # Message index
    chunkSize = 1                 # Anticipate accepted increment size
    queueSize = 1                 # Anticipate queue size
    queue = 0
    
    iChunkSize = chunkSize
    isMeasuring = False

    packetSizes = [1 for i in range(1,75)]
    packetSizeIdx = 0
    minWrongSize = 99999

    timeOuts = []
    startTime = 0
    adjusted = False
    while idx < len(message):
        """
        Sending Loop
        """
        

        while queue<queueSize:
            # Determine data parameters: submessage, isLast, seqNum
            submessage = message[idx:idx+chunkSize]
            sequence_number = 0 if sequence_number == 10000000 else sequence_number
            isLast = 0 if idx+chunkSize < len(message) else 1
            printToFile("captures/"+TxnID,f"                                  PACKET {sequence_number}")
            printToFile("captures/"+TxnID,"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            # Begin sending message 
            data = f"ID{senderID}SN{str(sequence_number).zfill(7)}TXN{TxnID}LAST{isLast}{submessage}"
            printToFile("captures/"+TxnID,f"Sqnc:\t\t{sequence_number}")
            printToFile("captures/"+TxnID,f"Size:\t\t{chunkSize}")
            printToFile("captures/"+TxnID,"Message:\t" + submessage)
            startTime = time()
            udp_send(data, clientSock, receiverIP, receiverPort)
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
                        chunkSize = estimate_chunk_size(len(message), diff, 77)
                        queueSize = 1
                        break
                    
                    """
                    Increase Packet size if okay
                    """
                    remPayload = len(message) - idx
                    will95, need95, remain95 = willSucceed(ProjectStart, 95,remPayload, chunkSize, sum(timeOuts)/len(timeOuts))
                    will120, need120, remain120 = willSucceed(ProjectStart, 120,remPayload, chunkSize, sum(timeOuts)/len(timeOuts))

                    # Anticipation for 95 seconds
                    if remain95-need95 < clientSock.gettimeout() and isMeasuring and adjusted == False:
                        print(adjusted)
                        adjusted = True
                        iChunkSize = chunkSize
                        chunkSize+=1

                    if not will120:
                        if isMeasuring:
                            printToFile("captures/"+TxnID,"\nMEASURING: \tChunk size fine\n")
                            iChunkSize = chunkSize
                            newChunkSize = chunkSize + packetSizes[packetSizeIdx]
                            while newChunkSize >= minWrongSize:
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
                    printToFile("captures/"+TxnID,"~~~~Timed out waiting for server~~~~")
                    if sequence_number == 1:
                        chunkSize = chunkSize//2
                    # Chunk Size too Big, decrease
                    if isMeasuring:
                        printToFile("captures/"+TxnID,"\nMEASURING: \tCHUNK SIZE TOO BIG\n")
                        isMeasuring = False
                        idx-=chunkSize       # resend previous packet
                        sequence_number -= 1
                        packetSizeIdx = 0

                        if sequence_number == 1:
                            chunkSize -= chunkSize//6
                        else:
                            chunkSize = (chunkSize+iChunkSize)//2
                        
                        break

            printToFile("captures/"+TxnID,f"Proc Time: \t{round(endTime-startTime,2)} seconds")
            printToFile("captures/"+TxnID,"ACK:\t\t" + ack)
            remPayload = len(message) - idx
            printToFile("captures/"+TxnID,f"Elapsed:\t{round(endTime - ProjectStart,2)} seconds")
            printToFile("captures/"+TxnID,"Remain Bytes: \t" + str(max(0,remPayload)) + " bytes")
            printToFile("captures/"+TxnID,"Remain Pckts: \t" + str(max(0,(remPayload//chunkSize)+1)) + " packets")

            succeed120 = willSucceed(ProjectStart, 119,remPayload, chunkSize, sum(timeOuts)/len(timeOuts))
            succeed95 = willSucceed(ProjectStart, 94,remPayload, chunkSize, sum(timeOuts)/len(timeOuts))
            printToFile("captures/"+TxnID,"Succeed 120: \t" + str(succeed120))
            printToFile("captures/"+TxnID,"Succeed 95: \t" + str(succeed95))
            printToFile("captures/"+TxnID,"TxnID:\t\t" + TxnID)

            received += 1
            queue = 0
            printToFile("captures/"+TxnID,"--------------------------------------------------------------------------------")

    # Print Final Transaction Metrics
    printToFile("captures/"+TxnID)
    printToFile("test/tests","TxnID: \t\t"+TxnID)
    printToFile("captures/"+TxnID,"TOTAL TIME: \t"+str(time()-ProjectStart))
    printToFile("captures/"+TxnID,"Ave Proc Time: \t" + str(sum(timeOuts)/len(timeOuts)))
    printToFile("test/tests","Ave Proc Time: \t" + str(sum(timeOuts)/len(timeOuts)))
    printToFile("captures/"+TxnID,"TxnID: \t\t"+TxnID)
    printToFile("captures/"+TxnID,"Final Size: \t"+str(chunkSize))
    printToFile("test/tests","Final Size: \t"+str(chunkSize))
    printToFile("captures/"+TxnID,"Payload Size: \t"+str(len(message)))
    printToFile("test/tests","Payload Size: \t"+str(len(message)))
    printToFile("test/tests","Perfect Time: \t"+str((len(message)/chunkSize)*sum(timeOuts)/len(timeOuts)))
    printToFile("test/tests","TOTAL TIME: \t"+str(time()-ProjectStart))
    printToFile("test/tests","")