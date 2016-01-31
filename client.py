'''
Author: Eoin Murphy

File: Client side system to access files. Should be separated into the interface and the proxt
'''

import os, socket, sys, MessageType
CLIENT_PATH = "Client\\"
DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 9999
SECURITY_PASS = "A secure string"
OK_MESSAGE = "All clear, connection correctly doodled"
DEBUG = False
FILE_PATH = 'Client/'
username = ''

#Used for debugging, information is printed if in debug mode
def log(info) :
    global DEBUG
    if(DEBUG) : 
        print('Log::\t' + info + '\n')

def queryServer(path, name, socket):
    packet = str(MessageType.QUERY) + '\n' + path + '\n' + name
    log('Checking server for file: ' + name + ' in path: ' + path)
    socket.sendall(packet)
    reply = socket.recv(1024)
    print reply

def query() :
    filepath = raw_input("\nEnter filepath to check: ")
    filename = raw_input("\nEnter filename to check: ")
    return (filepath, filename)

def checkConnection(socket) :    
    global username
    socket.sendall(SECURITY_PASS + '\n' + username)
    reply = socket.recv(1024)
    log('Received ' + reply)
    con = reply == OK_MESSAGE
    return con
    
def connectToServer(host, port) :
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host,port))
    s.settimeout(2.0)
    connection = checkConnection(s)
    if(connection) :
        print("Connection established!")
    else : 
        print("Connection failed...")
        s = None
    return s
    
def killServer(socket):
    socket.sendall("KILL_SERVICE\n")
    log('Server shutdown!')

def openFile(filepath, filename, socket):
    global FILE_PATH
    packet = str(MessageType.OPEN_FILE) + '\n' + filepath + '\n' + filename
    socket.sendall(packet)
    reply = socket.recv(1024)
    if(reply == str(MessageType.FILE_FOUND)):
        localpath = FILE_PATH + filepath + '/' + filename
        f = open(localpath, 'w')
        log('File found, beginning download...')
        openConn = True
        while (openConn):
            data = socket.recv(1024)
            f.write(str(data))
            log(data)
            openConn = len(data) == 1024
        log('Transmission complete, closing file...')
        f.close()
    else:
        print 'File could not be found. Please try a different file.'

def writeFile(filepath, filename, socket):
    global FILE_PATH
    packet = str(MessageType.WRITE_FILE) + '\n' + filepath + '\n' + filename
    socket.sendall(packet)
    localpath = FILE_PATH + filepath + '/' + filename
    f = open(localpath, 'r')
    log('File found, beginning upload...')
    moreData = True    
    data = f.read(1024)
    while (moreData):
        socket.sendall(str(data))
        data = f.read(1024)
        moreData = data != ''
    log('Transmission complete, closing file...')
    f.close()

def connectionLoop(host, port) : 
    sock = connectToServer(host, port)
    running = sock != None
    while (running) :
        response = raw_input("Select option:\n1) Query server\n2) Open File\n3) Write file\n4) Kill server\nx) Close Connection\n\n")
        if(response == "x" or response == "X"):
            running = False
        else :
            if(response == "1") :
                filepath, filename = query()
                queryServer(filepath, filename, sock)
            elif(response == '2'):
                filepath, filename = query()
                openFile(filepath, filename, sock)
            elif(response == '3'):
                filepath, filename = query()
                writeFile(filepath, filename, sock)
            else :
                if(response == "4") : 
                    killServer(sock)
                    running = False
                else : 
                    print "You said: " , response, "\n"
    print "Closing connection...."
    sock.close()
    
def openConnection() :
    userIn = raw_input("\nEnter the port number: ")
    if type(userIn) == int:
        port = int(port)
        try:
            host = raw_input("\nEnter the IP address of the host: ")
            socket.inet_aton(host)
            connectionLoop(host, port)
        except socket.error:
        # Not legal
            print "Invalid IP address"
    else:
        print("\nPort number must be an integer")

def main() :
    global DEFAULT_HOST, DEFAULT_PORT, DEBUG, FILE_PATH, username
    programRunning = True
    username = sys.argv[1]
    FILE_PATH = FILE_PATH + username + '/'
    if(len(sys.argv) > 2) :
        DEBUG = sys.argv[2] > 0
    log('User: ' + username + ' logged in, files stored at: '+ FILE_PATH)
    while(programRunning) :
        query = raw_input("Select option:\n1) Open connection\n2) Default connection\nx) Exit Program\n\n")
        if(query == "x" or query == "X"):
            programRunning = False
        else :
            if(query == "1") :
                openConnection()
            else :
                if(query == "2") :
                    connectionLoop(DEFAULT_HOST, DEFAULT_PORT)
                else :
                    print "You said: " , query, "\n"    
main()