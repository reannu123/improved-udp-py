import os
from datetime import datetime
from time import sleep, time

# Run tshark for 125 seconds and save the output to a file
def run_tshark():
    # set filename to the current date time
    file_name = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
    os.system(f"touch pcaps/{file_name}.pcap")
    os.system(f"chmod o=rw pcaps/{file_name}.pcap")
    os.system(f"sudo tshark -a duration:120 -w pcaps/{file_name}.pcap")
    txnId = read_file("txnID.txt")
    os.system(f"mv pcaps/{file_name}.pcap pcaps/{txnId}.pcap")

def read_file(file_name):
    try:
        with open(file_name, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return None

def write_file(file_name, message):
    with open(file_name, 'w') as f:
        f.write(message)

while(True):
    start = time()
    if read_file("capture.txt") == "Go":
        print("Capturing...")
        run_tshark()
        write_file("capture.txt", "Stop")
        end = time()
        txnId = read_file("txnID.txt")
        print(f"Captured {txnId}")
        print(end-start)
        print()

    


