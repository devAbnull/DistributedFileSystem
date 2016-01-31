import socket, select, thread, mutex, sys
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
print "IP: ", IP_Address

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

#Function to handle connections to server
def handleClient(connection, address):
    global port, ID, IP_Address, MAX_DATA_LENGTH
    print 'Connected by ', address
    data = connection.recv(MAX_DATA_LENGTH)#Get data
    keepRunning = True
    if(data == "KILL_SERVICE\n") :
        setOnline(False)#Turn server off
        keepRunning = False#Return false to stop this thread
    elif(data == SECURITY_PASS):#Return requested info to client
        connection.sendall(OK_MESSAGE)    
    else:
        #do nothing
        1+1
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



try: 
    if(len(sys.argv) < 2) : #Get port number from command line
        port = DEFAULT_PORT
    else : 
        port = int(sys.argv[1])
        if(len(sys.argv) > 2 ):
            SERVER_FILE = sys.argv[2]
            if(len(sys.argv) > 3):
                NUM_THREADS = int(sys.argv[3])
                if(len(sys.argv) > 4):
                    QUEUE_SIZE = int(sys.argv[4])            
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
        