#!/usr/bin/env python3

import argparse
import urllib.parse
import re
import os
import socket

def sendFtpCommand(command, sock):
    '''
    Encode and sends a specified FTP command through a socket.
    Parameters:
        command: A string containing the FTP command.
        sock: Socket through which the command will be sent.
    Return:
        None
    '''
    # Properly format FTP command with ending
    command = command + '\r\n'
    # Encode and send message through socket
    sock.send(command.encode())
def receiveResponse(sock):
    '''
    Receives and prints response from the server. Mainly for testing purposes. Needed to remove print statament for proper assignment functionality. 
    Parameters:
        sock: Socket messaged is being received from.
    Return:
        None
    '''
    # Receives response from socket
    response = sock.recv(4096)
    # Prints and decodes response
    #print(response.decode())
def ftpLogin(user, passW, sock):
    '''
    Logs into FTP server using the login provided in the FTP link and the provided socket.
    Parameters:
        user: A string containing the FTP username.
        passW: A string containg the FTP password.
        sock: The socket used to connect to the FTP server.
    Return:
        None
    '''
    # Sends username to FTP server for login
    sendFtpCommand(f'USER {user}', sock)
    # Receives response requesting a password
    receiveResponse(sock)
    # Sends password to FTP server
    sendFtpCommand(f'PASS {passW}', sock)
    # Receives login confirmation
    receiveResponse(sock)
def makeDir(dir, sock):
    '''
    Makes a directory on the FTP server
    Parameters:
        dir: A string containing the directory being made
        sock: Socket to send command through
    Return:
        None
    '''
    # Sends command to make directory
    sendFtpCommand(f'MKD {dir}', sock)
    # Receives confirmation response for directory being made
    receiveResponse(sock)
def removeDir(dir, sock):
    '''
    Removes a directory from FTP server
    Parameters:
        dir: A string containing directory to be removed
        sock: Socket to send command through
    Return:
        None
    '''
    # Send FTP command to remove directory
    sendFtpCommand(f'RMD {dir}', sock)
    # Receive reesponse confirming directory removal
    receiveResponse(sock)
def listDir(host, dir, sock):
    '''
    List contents of a directory on FTP server
    Parameters:
        host: String containing FTP hostname
        dir: String containing directory to be listed
        sock: Control socket to send request through
    Return:
        None
    '''
    # Pattern to remove port from PASV response
    pattern = r'\((.*?)\)'
    # Create new socket to send data through
    dirSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Send command to open new data channel
    sendFtpCommand('PASV', sock)
    # Receive response from PASV containing data channel IP address and port
    response = sock.recv(4096).decode()
    # Remove port and IP address from response
    portData = re.findall(pattern, response)
    # Turn IP address parts and port into list
    portData = portData[0].split(',')
    # Calculate port
    port = int(portData[4]) * 256 + int(portData[5])
    # Connect new socket
    dirSocket.connect((host, port))
    
    # Send FTP requesting directory contents
    sendFtpCommand(f'LIST {dir}', sock)
    # Receive response from control socket
    receiveResponse(sock)
    # Receive response from socket created for list request
    response = dirSocket.recv(4096)
    print(response.decode())
    # Close list socket
    dirSocket.close()
    # Receive response from 
    receiveResponse(sock)
def localToFtpUpload(localPath, host, dir, sock):
    '''
    Copies a local file to the FTP server
    Parameters:
        - localPath: String containing local path for file
        - host: String containing hostname
        - dir: String containing FTP directory to copy file to
        - sock: Control socket to send request
    '''
    # Pattern to remove port from PASV response
    pattern = r'\((.*?)\)'
    # Create new socket to send data through
    dirSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Send command to open new data channel
    sendFtpCommand('PASV', sock)
    # Receive response from PASV containing data channel IP address and port
    response = sock.recv(4096).decode()
    # Remove port and IP address from response
    portData = re.findall(pattern, response)
    # Turn IP address parts and port into list
    portData = portData[0].split(',')
    # Calculate port
    port = int(portData[4]) * 256 + int(portData[5])
    # Connect new socket
    dirSocket.connect((host, port))

    # Send command to store
    sendFtpCommand(f'STOR {dir}', sock)
    # Receive STOR response
    receiveResponse(sock)
    # Open local file
    with open(localPath, 'rb') as locFile:
        # Read and send file contents
        filedata = locFile.read(4096)
        while filedata:
            dirSocket.send(filedata)
            filedata = locFile.read(4096)

    # Close socket for data channel
    dirSocket.close()
    # Receive transfer confirmation response
    receiveResponse(sock)
def removeFtpFile(dir, sock):
    '''
    Remove file from FTP server
    Parameters:
        - dir: String containing file to be deleted
        - sock: String containg socket to send request
    '''
    # Send FTP command to delete file
    sendFtpCommand(f'DELE {dir}', sock)
    # Receive deletion confirmation from socket
    receiveResponse(sock)
def downloadFtpToLocal(localPath, host, dir, sock):
    '''
    Downloand file from FTP server to local machine
    Paramters:
        - localPat: String containing local path to store file
        - host: String containing hostname for FTP server
        - dir: String containing directory to get file from on FTP server
        - sock: Socket to send request through
    Return:
        None
    '''
    # Pattern to remove port from PASV response
    pattern = r'\((.*?)\)'
    # Create new socket to send data through
    dirSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Send command to open new data channel
    sendFtpCommand('PASV', sock)
    # Receive response from PASV containing data channel IP address and port
    response = sock.recv(4096).decode()
    # Remove port and IP address from response
    portData = re.findall(pattern, response)
    # Turn IP address parts and port into list
    portData = portData[0].split(',')
    # Calculate port
    port = int(portData[4]) * 256 + int(portData[5])
    # Connect new socket
    dirSocket.connect((host, port))

    sendFtpCommand(f'RETR {dir}', sock)
    receiveResponse(sock)

    #localPath = os.path.join(localPath, os.path.basename(dir))
    print(localPath)

    with open(localPath, 'wb') as locfile:
        filedata = dirSocket.recv(4096)
        while filedata:
            locfile.write(filedata)
            filedata = dirSocket.recv(4096)
    dirSocket.close()
    receiveResponse(sock)

def main():
    # Initialize argument parser
    pargs = argparse.ArgumentParser()

    # Define command line arguments
    pargs.add_argument('operation', type = str)
    pargs.add_argument('param1', type = str)
    pargs.add_argument('param2', nargs='?', default=None, type=str)

    # Parse command line arguments
    parsed_args = pargs.parse_args()

    # Set operation and port to be used
    ftpOperation = parsed_args.operation
    defaultPort = 21
    url = ""

    if "ftp" in parsed_args.param1:
        url = urllib.parse.urlparse(parsed_args.param1)
    elif "ftp" in parsed_args.param2:
        url = urllib.parse.urlparse(parsed_args.param2)

    # If the URL has a different port, change port to that
    if url.port != None:
        defaultPort = url.port

    # Create socket to connect to FTP server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connect to FTP server
    sock.connect((url.hostname, defaultPort))
    # Get server response
    receiveResponse(sock)
    # Login to FTP server
    ftpLogin(url.username, url.password, sock)

    # Get directory provided from FTP URL
    directory = url.path

    # List directory
    if ftpOperation == 'ls':
        listDir(url.hostname, directory, sock)
    # Make a directory
    if ftpOperation == 'mkdir':
        makeDir(directory, sock)
    # Remove a file
    if ftpOperation == 'rm':
        removeFtpFile(directory, sock)
    # Remove a directory
    if ftpOperation == 'rmdir':
        removeDir(directory, sock)
    # Copy a file
    if ftpOperation == 'cp':
        # Check which argument has the FTP URL
        if "ftp" in parsed_args.param2:
            # Upload and copy file to FTP server
            localToFtpUpload(parsed_args.param1, url.hostname, directory, sock)
        elif "ftp" in parsed_args.param1:
            # Download and copy file from FTP server
            downloadFtpToLocal(parsed_args.param2, url.hostname, directory, sock)
    # Move a file
    if ftpOperation == 'mv':
        # Check which argument has the FTP URL
        if "ftp" in parsed_args.param1:
            # Download file from FTP server to local machine and delete file from server.
            downloadFtpToLocal(parsed_args.param2, url.hostname, directory, sock)
            removeFtpFile(directory, sock)
        elif "ftp" in parsed_args.param2:
            # Upload file from local machine to FTP server then delete file from machine.
            localToFtpUpload(parsed_args.param1, url.hostname, directory, sock)
            os.remove(parsed_args.param1)

main()