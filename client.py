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

def query(socket) :
    filepath = raw_input("\nEnter filepath to check: ")
    filename = raw_input("\nEnter filename to check: ")
    #
    queryServer(filepath, filename, sock

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


def connectionLoop(host, port) : 
    sock = connectToServer(host, port)
    running = sock != None
    while (running) :
        response = raw_input("Select option:\n1) Query server\n2) Open File\n3) Write file\n4) Kill server\nx) Close Connection\n\n")
        if(response == "x" or response == "X"):
            running = False
        else :
            if(response == "1") :
                query(sock)
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