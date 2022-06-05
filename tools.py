import os
from typing import Optional
import requests

# Send a POST request to the server
def dl_file(filename:str, url:str="")->bool:
    """ Download file from the specified url

    Args:
        - filename (str): filename of the file to be saved
        - url (str, optional): the url from where to download. Defaults to "".

    Returns:
        - bool: True if the file was downloaded successfully, False otherwise
    """
    try:
        file = requests.get(url)                                # Download the file
        open(filename, "wb").write(file.content)                # Write the file to the specified filename
        return True                                            # Return True if the file was downloaded successfully
    except:
        print("Error downloading payload")
        return False                                           # Return False if the file was not downloaded successfully
        
# Save prints to a file
def printToFile(filename:str, message:str = '', printToScreen:bool = True) -> None:
    """ Print message to specified file

    Args:
        - filename (str): name of the file to print to
        - message (str, optional): message to print. Defaults to "".
        - printToScreen (bool, optional): whether or not to print to screen. Defaults to True.
    """
    if printToScreen:                                                       # If printToScreen is True
        print(message)                                                      # Print the message to the screen
    try:
        with open(f"{filename}.txt", 'a') as f:                             # Open the file
            print(message,file=f)                                           # Print the message to the file
    except FileNotFoundError:                                           # If the file does not exist
        print("Error writing to file. Directory may not exist")                                  # Print an error message

# Read a file
def read_file(filename:str) -> Optional[str]:
    """ Read a file

    Args:
        - filename (str): name of the file to read

    Returns:
        - str: the contents of the file 
        - None: if the file does not exist
    """
    try:
        with open(filename, 'r') as f:          # Open the file
            return f.read()                     # Read the file and return
    except FileNotFoundError:                   # If the file does not exist, return None
        return None

# write a file
def write_file(filename:str, message:str) -> None:
    """ Write a message to a file

    Args:
        - filename (str): name of the file to write to
        - message (str): message to write

    """
    with open(filename, 'w') as f:          # Open the file
        f.write(str(message))               # Write the message


# Run tshark for specified duration seconds and save the output to a file
def run_tshark(duration:int, filename:str="tempFileName") -> str:
    """
    Run tshark for a specified duration
    
    Args:
        - saveFileName (str): name of the file to save the output to
        - duration (int): duration of the capture in seconds
    
    Returns:
        - str: the name of the file that the output was saved to
    """
    
    os.system(f"touch pcaps/{filename}.pcap")                                   # Create a file to save the output to
    os.system(f"chmod o=rw pcaps/{filename}.pcap")                              # adjust permissions
    os.system(f"sudo tshark -a duration:{duration} -w pcaps/{filename}.pcap")   # Run tshark with set duration
    return filename