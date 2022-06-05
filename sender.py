# Create a transport protocol on top of UDP that reads from a file and sends the contents of the file to the client.
from newProtocol import *
from tools import *
import argparse


def get_args()->argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", help="File name")
    parser.add_argument("-a", help="IP address")
    parser.add_argument("-s", help="Receiver port number")
    parser.add_argument("-c", help="Sender port number")
    parser.add_argument("-i", help="Unique ID")
    args = parser.parse_args()
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
    dl_payload("c3563823")
    startTransaction(args.a, args.s, args.i, args.c, args.f)

main()