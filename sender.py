# Create a transport protocol on top of UDP that reads from a file and sends the contents of the file to the client.
import socket
from newProtocol import *
from tools import *
import argparse
from time import sleep,time


def get_args()->argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", help="File name")
    parser.add_argument("-a", help="IP address")
    parser.add_argument("-s", help="Receiver port number")
    parser.add_argument("-c", help="Sender port number")
    parser.add_argument("-i", help="Unique ID")
    args = parser.parse_args()
    print(args.a)
    print(args.s)
    if args.a is None:
        # Test server "209.97.169.245"
        # VPC 2 "10.0.1.175"
        args.a = "10.0.1.175"
    if args.s is None:
        args.s = 9000
    if args.c is None:
        args.c = 6706
    if args.i is None:
        args.i = "c3563823"
    if args.f is None:
        args.f = f"{args.i}.txt"

    return args

def main():
    args = get_args()
    startTransaction(args.a, args.s, args.i, args.c, args.f)

main()
# timeLimit = 122
# while(True):
#     if read_file("capture.txt") =="Stop":
#         dl_payload("http://54.169.121.89:5000/get_data?student_id=c3563823")
#         write_file("capture.txt", "Go")
#         start = time()
#         sleep(1)
#         print("\n\n\n\nNew payload downloaded")
#         main()
#         end = time()
#         while(end-start<timeLimit):
#             sleep(timeLimit-(end-start))
#             end = time()
#             print(end-start)
#             pass