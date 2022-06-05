from tools import *

"""
Run tshark capture repeatedly for a specified duration

"""
def main():
    while(True):
        if read_file("capture.txt") == "Go":
            print("Capturing...")
            filename = run_tshark(120)
            write_file("capture.txt", "Stop")
            txnId = read_file("txnID.txt")
            os.system(f"mv pcaps/{filename}.pcap pcaps/{txnId}.pcap")
            print(f"Captured {txnId}\n")

main()
