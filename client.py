import os, socket, sys
CLIENT_PATH = "Client\\"
DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 9999
SECURITY_PASS = "A secure string"
OK_MESSAGE = "All clear, connection correctly doodled"
DEBUG = False
FILE_PATH = 'Client/'

#Used for debugging, information is printed if in debug mode
def log(info) :
    global DEBUG
    if(DEBUG) : 
        print('Log::\t' + info + '\n')

def queryServer() :
    filepath = raw_input("\nEnter filepath to check: ")
    filename = raw_input("\nEnter filename to check: ")
    if os.path.exists(filepath):
        print "\n", filepath, "\nIs a directory"
        if os.path.isfile(filename + "\\" + filepath) :
            print "File found successfully\n"
        else :
            print "\nThe file: ", filename , " could not be found"
    else :
        print "No such directory exists"


def checkConnection(socket) :    
    socket.sendall(SECURITY_PASS)
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
        query = raw_input("Select option:\n1) Query server\n2) Open File\n3) Write file\n4) Kill server\nx) Close Connection\n\n")
        if(query == "x" or query == "X"):
            running = False
        else :
            if(query == "1") :
                queryServer()
            else :
                if(query == "4") : 
                    killServer(sock)
                    running = False
                else : 
                    print "You said: " , query, "\n"
    print "Closing connection...."
    sock.close()
    
def openConnection() :
    port = raw_input("\nEnter the port number: ")
    if type(user_input) == int:
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
    global DEFAULT_HOST, DEFAULT_PORT, DEBUG
    programRunning = True
    if(len(sys.argv) > 1) :
        DEBUG = sys.argv[1] > 0
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