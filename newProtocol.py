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
    data, addr = clientSock.recvfrom(1024)              # Receive the message
    if len(data) > 0:                                   # if the message is not empty
        rcvd = data.decode()                            # decode the message
    return rcvd                                         # return the message



def udp_send(message:str, clientSock:socket.socket, iadr:str, port:int)->None:
    """
    Send a message to the server

    Args:
        - message (str): message to be sent
        - clientSock (socket.socket): UDP socket
        - iadr (str): IP address of the server
        - port (int): port number of the server

    """
    packet = message.encode()                                       # encode the message
    clientSock.sendto(packet, (iadr, port))                         # send the message



def send_intent(intentMessage:str, clientSock:socket.socket, receiverIP:str, receiverPort:int)->str:
    """
    Send an intent message to the server
    
    Args:
        - intentMessage: intent message to be sent
        - clientSock: UDP socket
        - receiverIP: IP address of the server
        - receiverPort: port number of the server
    
    Returns:
        - str: ID of the transaction
    """
    # Send intent message
    udp_send(intentMessage, clientSock, receiverIP, receiverPort)   # send intent message
    start = time()                                                  # start timer
    tries = 0                                                       # number of tries of waiting
    while(True):
        try:
            TxnID = udp_receive(clientSock)                         # receive the transaction ID
            end = time()                                            # end time of getting the transaction ID
            print(f"Time elapsed: {end-start}")
            return TxnID                                            # return the transaction ID
        except socket.timeout:                                      # if the server does not respond, try again
            if tries >=3:                                           # if the number of tries is greater than 3, exit
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
    intentMessage  =f"ID{uniqueID}"                                             # intent message format
    TxnID = send_intent(intentMessage, clientSock, receiverIP, receiverPort)    # send intent message using send_intent function

    if TxnID == "Existing alive transaction":     # if the server already has an alive transaction, exit
        print(TxnID)
        exit()
        
    else:
        write_file(f"txnID.txt", TxnID)           # write the transaction ID to txnID.txt
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
        url = f"http://3.0.248.41:5000/get_data?student_id={uniqueID}"      # URL of the server 1
    if vpc == 2:
        url = f"http://54.169.121.89:5000/get_data?student_id={uniqueID}"   # URL of the server 2
    return dl_file(f"{uniqueID}.txt", url)                                  # return the downloaded the file
    


def start_UDP(senderPort:int)->socket.socket:
    """
    Create a UDP socket and bind it to the specified port

    Args:
        senderPort (int): port number of the sender

    Returns:
        socket.socket: UDP socket
    """
    clientSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)   # Create a UDP socket
    clientSock.bind(('',senderPort))                                # Bind the socket to the port
    clientSock.settimeout(5)                                        # Set default to 5 seconds
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
    # compute the number of packets needed to send the payload in a certain time depending on the processing time
    numofPackets = expectedTime/procTime        
    # chunkSize is the size of the payload divided by the number of packets
    chunkSize = int(payloadSize/numofPackets)   
    return chunkSize


def adjustChunkSize(adjusted:bool, isAdjusting:bool, procTimes:"list[float]", ProjectStart:float, remPayload:int, chunkSize:int, minWrongSize:int, prevChunkSize)->int:
    
    """
    Adjust the chunk size based on the processing time of the packets

    Args:
        - adjusted (bool): whether the chunk size was already adjusted
        - isAdjusting (bool): whether the chunk size is allowed to be
        - procTimes (list[float]): list of processing times
        - ProjectStart (float): start time of the project
        - remPayload (int): remaining bytes of the payload
        - chunkSize (int): number of bytes of the message to include in a packet
        - expectedTime (int): expected time
        - minWrongSize (int): minimum size of the chunk
        - prevChunkSize (int): previous chunk size

    Returns:
        - int: adjusted chunk size
        - bool: whether the chunk size was adjusted
        - int: previous chunk size
        - bool: whether the chunk size is allowed to be adjusted
    """
    aveProcTime = sum(procTimes)/len(procTimes)     # Average processing time so far
    timeLeft = 95 - (time() - ProjectStart)         # Time left to 95 seconds
    packets_left = remPayload/chunkSize             # Number of packets left to send
    neededTime = packets_left * aveProcTime         # Time needed to send all remaining packets
    allowance = timeLeft - neededTime               # Time left after sending all remaining packets

    isAllowanceSmall = allowance < aveProcTime  # Check if the allowance is smaller than the timeout
    isAllowanceBig = allowance > 2* aveProcTime # Check if the allowance is bigger than twice the timeout
    
    if (isAllowanceSmall and adjusted == False) or isAllowanceBig:
        """
        Adjust the chunk size only if the allowance is smaller than the timeout 
        IF the chunk size has not been adjusted yet

        If the chunk size has been adjusted already, 
        and the allowance is bigger than twice the timeout, 
        when we can still risk adjusting
        """
        adjusted = True                 # Set adjusted flag to True
        prevChunkSize = chunkSize       # Update the previous chunk size
        if chunkSize+1 >= minWrongSize:         # If we had hit the limit, stop adjusting
            isAdjusting = False                 # Set isAdjusting flag to False
        else:
            chunkSize+=1                        # Increase the chunk size by 1 otherwise
    return chunkSize, adjusted, prevChunkSize, isAdjusting



def startTransaction(receiverIP, receiverPort, senderID,senderPort, payloadName):
    """
    Start a new transaction

    Args:
        - receiverIP (str): IP address of the receiver
        - receiverPort (int): port number of the receiver
        - senderID (str): unique ID of the sender
        - senderPort (int): port number of the sender
        - payloadName (str): name of the payload

    """
    
    # Initialize UDP connection
    clientSock = start_UDP(senderPort)

    # Read from file named "{uniqueID}.txt" and store to message
    message = read_file(payloadName)            # Read from file
    if message == None:                         # If the file is not found, exit
        print("File not found.")            
        exit()

    """
    Send Intent Message
    """
    TxnID = getTxnID(clientSock, receiverIP, receiverPort, senderID)        # Get the Transaction ID from server
    printToFile(f"captures/{TxnID}","Txn: " + TxnID)                        # Print to file
    ProjectStart = time()                                                   # Start the timer for the whole payload sending


    """
    Send Packets
    """
    sequence_number = 0
    idx = 0                         # Message index
    chunkSize = 1                   # Anticipate accepted increment size
    prevChunkSize = 1               # Previous accepted increment size   

    isAdjusting = False             # Whether the sender is measuring the transmission time
    minWrongSize = 99999            # Minimum wrong size

    procTimes = []                  # List of processing times               
    adjusted = False                # Whether the chunk size has been adjusted or not


    # Send the message in chunks of chunkSize bytes
    while idx < len(message):
        """
        Sending Section
        """
        
        # Determine data parameters: submessage, isLast, sequence number, etc.
        submessage = message[idx:idx+chunkSize]                                     # Slice the message to be sent per packet
        sequence_number = 0 if sequence_number == 10000000 else sequence_number     # Reset the sequence number if it reaches 10000000
        isLast = 0 if idx+chunkSize < len(message) else 1                           # Set isLast to 1 if it is the last packet

        # Create the packet to be sent
        packet = f"ID{senderID}SN{str(sequence_number).zfill(7)}TXN{TxnID}LAST{isLast}{submessage}"

        printToFile(f"captures/{TxnID}",f"                                  PACKET {sequence_number}")                      # Printing for logging
        printToFile(f"captures/{TxnID}","~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        printToFile(f"captures/{TxnID}",f"Sqnc:\t\t{sequence_number}")
        printToFile(f"captures/{TxnID}",f"Size:\t\t{chunkSize}")
        printToFile(f"captures/{TxnID}","Message:\t" + submessage)

        startTime = time()      # Mark the time of sending the packet (for measuring processing time)  


        udp_send(packet, clientSock, receiverIP, receiverPort)              # Send the packet to the server


        idx+=chunkSize                      # Increment the index
        sequence_number += 1                # Increment the sequence number
        remPayload = len(message) - idx     # Remaining payload



        """
        Receiving Loop
        """
        while(True):
            try:
                ack = udp_receive(clientSock)                   # Receive the ACK from the server
                endTime = time()                                # Mark the time of receiving the ACK
                diff = endTime-startTime                        # Calculate the processing time
                procTimes.append(diff)                          # Add the processing time to the list
                
                """ 
                Experimental packet: 
                    - For measuring processing time
                    - Important in estimating the chunk/message size in a packet
                    - Only for the first packet
                """
                if sequence_number-1 == 0:
                    isAdjusting = True                                          # Allow adjustment of packet sizes after this
                    clientSock.settimeout(diff+1)                               # Set the socket timeout to the processing time (+1 to avoid false positives)
                    prevChunkSize = chunkSize                                   # Set the previous chunk size to the current one
                    chunkSize = estimate_chunk_size(len(message), diff, 77)     # Update the current one to the estimated chunk size
                    break

                if isAdjusting:
                    chunkSize,adjusted,prevChunkSize, isAdjusting = adjustChunkSize(adjusted,       # Adjust the chunk size depending on a number of factors
                                                                                    isAdjusting, 
                                                                                    procTimes, 
                                                                                    ProjectStart, 
                                                                                    remPayload, 
                                                                                    chunkSize, 
                                                                                    minWrongSize, 
                                                                                    prevChunkSize)
                
                break


            except socket.timeout:                  # If the socket times out, send the packet again or wait
                endTime = time()
                printToFile(f"captures/{TxnID}",    "~~~~Timed out waiting for server~~~~")     
                
                # Chunk Size too Big, decrease
                if isAdjusting:
                    printToFile(f"captures/{TxnID}",    "\nMEASURING: \tCHUNK SIZE TOO BIG\n")
                    isAdjusting = False
                    minWrongSize = min(chunkSize, minWrongSize)         # Update minimum wrong size
                    idx-=chunkSize                                      # Decrement the index to send previous packet
                    sequence_number -= 1                                # Decrement sequence number to send previous packet
                    chunkSize = prevChunkSize                           # Reset the chunk size to the previous one
                    break


        aveProcTime = sum(procTimes)/len(procTimes)                                         # Average processing time so far
        remBytes = max(0,remPayload)                                                        # Remaining bytes
        remPkts = max(0,(remPayload//chunkSize)+1)                                          # Remaining packets
        totalTime = round(endTime - ProjectStart, 2)                                        # Total time so far
        
        
        timeLeft95 = 95 - (time() - ProjectStart)       # Time left to 95 seconds
        timeLeft120 = 120 - (time() - ProjectStart)     # Time left to 120 seconds      
        packets_left = remPayload/chunkSize             # Number of packets left to send
        neededTime = packets_left * aveProcTime         # Time needed to send all remaining packets
        allowance95 = timeLeft95 - neededTime           # Time left to 95 after sending all remaining packets
        allowance120 = timeLeft120 - neededTime         # Time left to 120 after sending all remaining packets
        succeed95 = allowance95 > 0                      # Whether the time left is enough to send all remaining packets under 95
        succeed120 = allowance120 > 0                    # Whether the time left is enough to send all remaining packets under 120

        printToFile(f"captures/{TxnID}",    f"TxnID:\t\t{TxnID}")                   # Just for logging
        printToFile(f"captures/{TxnID}",    f"Proc Time: \t{aveProcTime} seconds")
        printToFile(f"captures/{TxnID}",    f"ACK: \t\t{ack}")
        printToFile(f"captures/{TxnID}",    f"Remain Bytes: \t{remBytes} bytes")
        printToFile(f"captures/{TxnID}",    f"Remain Pckts: \t{remPkts} packets")
        printToFile(f"captures/{TxnID}",    f"Elapsed:\t{totalTime} seconds")
        printToFile(f"captures/{TxnID}",    f"Succeed 120: \t{succeed120}")
        printToFile(f"captures/{TxnID}",    f"Extra to 120: \t{allowance120}")
        printToFile(f"captures/{TxnID}",    f"Succeed 95: \t{succeed95}")
        printToFile(f"captures/{TxnID}",    f"Extra to 95: \t{allowance95}")
        printToFile(f"captures/{TxnID}",    f"--------------------------------------------------------------------------------")


    # Print Final Transaction Metrics

    aveProcTime = sum(procTimes)/len(procTimes)                 # Final average processing time
    payloadSize = len(message)                                  # Payload size
    totalTime = time() - ProjectStart                           # Total time it took
    
    printToFile(f"captures/{TxnID}")
    printToFile(f"captures/{TxnID}",    f"\nTOTAL TIME: \t{totalTime}")         # Total time it took
    printToFile(f"captures/{TxnID}",    f"Ave Proc Time: \t{aveProcTime}")      # Average processing time
    printToFile(f"captures/{TxnID}",    f"TxnID: \t\t{TxnID}")                  # Transaction ID
    printToFile(f"captures/{TxnID}",    f"Final Size: \t{chunkSize}")           # Final chunk size
    printToFile(f"captures/{TxnID}",    f"Payload Size: \t{payloadSize}")       # Payload size
    
    printToFile(f"test")
    printToFile(f"test",    f"TxnID: \t\t{TxnID}")                  # Transaction ID
    printToFile(f"test",    f"\nTOTAL TIME: \t{totalTime}")         # Total time it took
    printToFile(f"test",    f"Ave Proc Time: \t{aveProcTime}")      # Average processing time
    printToFile(f"test",    f"Final Size: \t{chunkSize}")           # Final chunk size
    printToFile(f"test",    f"Payload Size: \t{payloadSize}")       # Payload size