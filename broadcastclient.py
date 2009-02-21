from multiprocessing import Queue, Process
from threading import Thread, Lock
import socket

def client(outgoing_queue, incoming_queue):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('', 9000))
    file_like = sock.makefile("rb")
    
    lock = Lock()
    
    def write(sock):
        while True:
            message = outgoing_queue.get()
            sock.send(message)
        
    def read(sock):
        while True:
            line = file_like.readline()
            if not line:    
                raise EOFError
            incoming_queue.put(line)
    
    Thread(target=write, args=(sock,)).start()
    t = Thread(target=read, args=(sock,))
    t.start()
    t.join()
 
if __name__ == '__main__':
    pass

#if __name__ == '__main__':
#    incoming_queue = Queue()
#    outgoing_queue = Queue()
#    client(incoming_queue, outgoing_queue)
