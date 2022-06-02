
import os
from datetime import datetime

# Run tshark for 125 seconds and save the output to a file
def run_tshark():
    # set filename to the current date time
    file_name = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
    os.system(f"touch {file_name}.pcap")
    os.system(f"chmod o=rw {file_name}.pcap")
    os.system(f"sudo tshark -a duration:125 -w {file_name}.pcap")

run_tshark()