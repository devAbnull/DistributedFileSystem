'''
Author: Eoin Murphy

Example File Server that controls access to the files on its system

Clients should contact a directory server to find the correct address of this system and then contact this 
for transfer of files.
'''
import socket, select, thread, mutex, sys, MessageType, os
from threading import Thread, Lock
from Queue import Queue

online = True
shutdownLock = Lock()#Lock for online, used to shutdown server
IP_Address = socket.gethostbyname(socket.getfqdn())
DEFAULT_PORT = 9999 #Default port
NUM_THREADS = 20 #Default Worker Threads
MAX_DATA_LENGTH = 1024
SERVER_FILE = "Server/"
QUEUE_SIZE = NUM_THREADS*3 #Default size for queue, based on number of threads
SECURITY_PASS = "A secure string"
OK_MESSAGE = "All clear, connection correctly doodled"
DEBUG = False
FILE_PATH = 'Server/'

#Simple function to stop any Worker that runs it
def stopWorker():
    return False
    
#Function to change the value of 'online', hides locking mechanism
def setOnline(value) :
    global shutdownLock, online
    shutdownLock.acquire()#Get lock
    try:#Do work with variable
        online = value
    finally:#Always release the lock
        shutdownLock.release()
        
#Function returning the value of 'online', hides the locking mechanism  
def readOnline():
    global shutdownLock, online
    shutdownLock.acquire()#Get lock
    result = True#Default value
    try:#Do work with variable
        result = online
    finally:#Always release the lock
        shutdownLock.release()
    return result

#Used for debugging, information is printed if in debug mode
def log(info) :
    global DEBUG
    if(DEBUG) : 
        print('Log::\t' + info + '\n')

#Check the client has sent an authentic security pass, of the required format
def passSecurity(packet):
    passed = False
    name = 'ERROR'
    data = packet.split('\n')
    if(len(data) > 1) :
        passed = data[0] == SECURITY_PASS
        name = data[1]
    return (passed, name)

#Function for opening files, downloads file to client and allows the client to modify file
def openFile(path, packet, conn):
    directory = path + packet[1] + '/'
    fileName = packet[2]
    fullPath = directory + fileName
    log('Client opening file: ' + fullPath )
    if os.path.isfile(fullPath):
        log('File found, transmission beginning...')
        reply = str(MessageType.FILE_FOUND)
        conn.sendall(reply)
        f = open(fullPath)
        data = f.read(1024)
        while( data != '' ):
            conn.sendall(data)
            data = f.read(1024) 
        log('File successfully transmitted.')
        f.close()
    else:
        reply = str(MessageType.FILE_NOT_FOUND)
        conn.sendall(reply)

#Function to creat the necessary directories if none exist
def handleDir(directory) :
    if not os.path.exists(directory):
        os.makedirs(directory)

#Function to receive uploads of files and write them to the server
def receiveFile(path, packet, conn):
    directory = path + packet[1] + '/'
    fileName = packet[2]
    fullPath = directory + fileName
    log('Client uploading file: ' + fileName + ' in directory ' + directory)
    handleDir(directory)
    f = open(fullPath, 'w')
    log('File found, beginning download...')
    openConn = True
    while (openConn):
        data = conn.recv(1024)
        f.write(data)
        openConn = len(data) == 1024
    log('Transfer complete, closing file...')
    f.close()


#Function to handle queries about the existence of files
def queryDirectory(path, packet, conn):
    directory = path + packet[1] + '/'
    fileName = packet[2]
    fullPath = directory + fileName
    reply = str(MessageType.FILE_FOUND)
    log('Client querying directory: ' + directory + ' for file: ' + fileName)
    if os.path.exists(path):
        if (not (os.path.isfile(fullPath))) :
            reply = str(MessageType.FILE_NOT_FOUND)
    else :
        reply = str(MessageType.DIRECTORY_NOT_FOUND)
    log(reply)
    conn.sendall(reply)

#Function to handle connections to server
def handleClient(connection, address):
    global port, ID, IP_Address, MAX_DATA_LENGTH, FILE_PATH
    print 'Connected by ', address    
    data = connection.recv(MAX_DATA_LENGTH)#Get data
    keepRunning = True

    connectionOpen, username = passSecurity(data)
    if(connectionOpen):#Return requested info to client
        log('Client: ' + username + ' has successfully passed security check')
        connection.sendall(OK_MESSAGE)    
        localPath = FILE_PATH + username + '/' 
        while connectionOpen:
            data = connection.recv(MAX_DATA_LENGTH)#Get data
            log('Packet received: ' + data)
            if(not data) :
                connectionOpen = False
            elif(data == 'KILL_SERVICE\n') :
                log("Server shutdown initiated")
                setOnline(False)#Turn server off
                keepRunning = False#Return false to stop this thread
            else:
                info = data.split('\n')
                header = data[0]
                log('Header: ' + header)
                header = int(header)
                if(header == MessageType.OPEN_FILE):
                    openFile(localPath, info, connection)
                elif(header == MessageType.WRITE_FILE):
                    receiveFile(localPath, info, connection)
                elif(header == MessageType.QUERY):
                    queryDirectory(localPath, info, connection)

    log('Connection closed, freeing thread...')
    return keepRunning

class Worker(Thread):
    def __init__(self, queue):
        self.tasks = queue#Link to the queue
        self.on = True
        Thread.__init__(self)
        self.start()#Start thread
        
    def run(self):
        while self.on:
            func, args, kargs = self.tasks.get()#Get task from pool
            self.on = func(*args, **kargs)#Perform task and use return value
    
class ThreadPool: #Thread pool class
    def __init__(self, n, size):
        self.queue = Queue(size)#Queue for threads to read tasks from
        self.num = n#Number of threads
        self.threads = []#List of threads
        for i in range(0, n):#Start each thread and add to the list
            self.threads.append(Worker(self.queue))
    def addTask(self, func, *args, **kargs):
        self.queue.put((func, args, kargs))#Add task to queue, supplying arguments
    
    def endThreads(self):
        for i in range(0, self.num):
            self.addTask(stopWorker)#Make sure all threads finish
        for i in range(0, self.num):
            self.threads[i].join()#Join all the threads            
#        self.queue.join()


def main(): 
    global DEBUG, NUM_THREADS, QUEUE_SIZE, DEFAULT_PORT, IP_Address, SERVER_FILE, FILE_PATH
    try: 
        port = DEFAULT_PORT
        FILE_PATH = FILE_PATH + sys.argv[1] + '/'
        if(len(sys.argv) > 2) : #Get port number from command line
            DEBUG = sys.argv[2] > 0
            if(len(sys.argv) > 3) :
                port = int(sys.argv[3])
                if(len(sys.argv) > 4 ):
                    SERVER_FILE = sys.argv[4]
                    if(len(sys.argv) > 5):
                        NUM_THREADS = int(sys.argv[5])
                        if(len(sys.argv) > 6):
                            QUEUE_SIZE = in5(sys.argv[6])           
        log('IP: ' + IP_Address)
        log('Server files locatted at: ' + FILE_PATH)
        HOST = '' #Start on localhost
        pool = ThreadPool(NUM_THREADS, QUEUE_SIZE)   #Create Thread pool with queue size stated
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((HOST, port))
        try: 
            s.listen(1)#Start listening
            list = [s] #List of sockets
            while readOnline():
                read, _, _ = select.select(list, [], [], 0.1)#Set timeout to 0.1 for non-blocking socket
                for sock in read:
                    if(sock is s):#Server socket 
                        c, a = sock.accept()#Get info and pass to thread pool
                        pool.addTask(handleClient, c,a)
            pool.endThreads()#Finish threads    
            s.close()#Close sockets
            print "Server shutting down..."
        except Exception, e:
            print e
        finally:
            s.close()
    except Exception, e:
        print e

main()