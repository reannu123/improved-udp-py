from newProtocol import startTransaction
import argparse


def get_args()->argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", help="File name")             # Add filename argument
    parser.add_argument("-a", help="IP address")            # Add IP address argument
    parser.add_argument("-s", help="Receiver port number")  # Add receiver port number argument
    parser.add_argument("-c", help="Sender port number")    # Add sender port number argument
    parser.add_argument("-i", help="Unique ID")             # Add unique ID argument
    args = parser.parse_args()
    
    if args.a is None:                  # If the IP address is not specified, set a default
        # VPC 1 "10.0.7.141"
        # VPC 2 "10.0.1.175"
        args.a = "10.0.1.175"
    if args.s is None:                  # If the receiver port number is not specified, set a default
        args.s = 9000
    if args.c is None:                  # If the sender port number is not specified, set a default
        args.c = 6706
    if args.i is None:                  # If the unique ID is not specified, set a default
        args.i = "c3563823"
    if args.f is None:                  # If the file name is not specified, set a default
        args.f = f"{args.i}.txt"

    return args

def main(): 
    args = get_args()                                           # Get the arguments
    startTransaction(args.a, int(args.s), args.i, int(args.c), args.f)    # Start the transaction



main()      # Run the main function