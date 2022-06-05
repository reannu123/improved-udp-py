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
        file = requests.get(url)
        open(filename, "wb").write(file.content)
        return True
    except:
        print("Error downloading payload")
        return False
        
# Save prints to a file
def printToFile(filename:str, message:str = '', printToScreen:bool = True) -> None:
    """ Print message to specified file

    Args:
        - filename (str): name of the file to print to
        - message (str, optional): message to print. Defaults to "".
        - printToScreen (bool, optional): whether or not to print to screen. Defaults to True.
    """
    if printToScreen:
        print(message)
    with open(f"{filename}.txt", 'a') as f:
        print(message,file=f)


def read_file(filename:str) -> Optional[str]:
    """ Read a file

    Args:
        - filename (str): name of the file to read

    Returns:
        - str: the contents of the file 
        - None: if the file does not exist
    """
    try:
        with open(filename, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return None


def write_file(filename:str, message:str) -> None:
    """ Write a message to a file

    Args:
        - filename (str): name of the file to write to
        - message (str): message to write

    """
    with open(filename, 'w') as f:
        f.write(str(message))


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
    
    os.system(f"touch pcaps/{filename}.pcap")
    os.system(f"chmod o=rw pcaps/{filename}.pcap")
    os.system(f"sudo tshark -a duration:{duration} -w pcaps/{filename}.pcap")
    return filename