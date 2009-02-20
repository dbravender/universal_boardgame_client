""" A small demonstration of a chat server in Python.  I'll probably
use this to implement the dots-and-boxes game server in the future.

Danny Yoo (dyoo@hkn.eecs.berkekey.edu)
"""

from threading import *
from Queue import Queue
import SocketServer


class MessageRoom(Thread):
    """This class simulates a room full of people, where messages
shout()ed out will broadcast to everyone else in the room.

TODO: add more documentation!
"""
    def __init__(self):
        Thread.__init__(self)
        self._message_queue = Queue()
        self._listeners = []
        self._listeners_lock = RLock()
        self._shutdown = 0
        self._events = Queue()


    def shout(self, listener, msg):
        """Shout out a message to all listeners."""
        self._message_queue.put((listener, msg))
        self._events.put("message added")
        

    def addListener(self, listener):
        """Adds a callable 'listener' to our list of active listeners."""
        self._listeners_lock.acquire()
        try:
            self._listeners.append(listener)
        finally:
            self._listeners_lock.release()


    def removeListener(self, listener):
        """Removes a callable 'listener' from our list of active listeners."""
        self._listeners_lock.acquire()
        try:
            self._listeners.remove(listener)
        finally:
            self._listeners_lock.release()


    def run(self):
        """Runs forever, listening to both shutdown and message shouting."""
        while 1:
            self._waitForShutdownOrNewMessages()
            if self._shutdown:
                break
            if self._message_queue.qsize():
                self._broadcastNewMessage()


    def shutdown(self):
        """Shutdown the chatroom."""
        self._shutdown = 1
        self._events.put("shutdown requested")


    def _waitForShutdownOrNewMessages(self):
        return self._events.get()


    def _broadcastNewMessage(self):
        try:
            (listener, msg) = self._message_queue.get_nowait()
        except Empty:
            return
        self._listeners_lock.acquire()
        try:
            listeners_copy = self._listeners[:]
            try:
                listeners_copy.remove(listener)
            except:
                pass
        finally:
            self._listeners_lock.release()
        for listener in listeners_copy:
            self._tryToSendMessageToListener(msg, listener)


    def _tryToSendMessageToListener(self, msg, listener):
        try:
            ## Fixme: we should somehow a timeout here.  If a message
            ## can't get through within a certain period of time, we
            ## should assume the listener is just delinquent, and toss
            ## them out of the listeners list.  Very rough, but
            ## necessary if we don't want to deadlock waiting for any
            ## particular listener.
            listener(msg)
        except:
            self.removeListener(listener)



######################################################################
## TODO: I may want to move this off to a different module...

## FIXME: by default, the server only supports 40 people.  Make this
## larger.
            
class ChatThreadedServer(SocketServer.ThreadingMixIn,
                         SocketServer.TCPServer):
    allow_reuse_address = 1

    def __init__(self, server_address, request_handler_class):
        SocketServer.TCPServer.__init__(self,
                                        server_address,
                                        request_handler_class)
        self._chat_room = MessageRoom()
        self._chat_room.setDaemon(1)
        self._chat_room.start()

    def shutdown(self):
        self._chat_room.shutdown()


class ChatRequestHandler(SocketServer.StreamRequestHandler):
    def handle(self):
        server = self.server
        while 1:
            ## fixme: add notification of server shutdown
            line = self.rfile.readline()
            if not line:
                break
            if line:
                server._chat_room.shout(self._writeMsg, line)


    def setup(self):
        SocketServer.StreamRequestHandler.setup(self)
        self.server._chat_room.addListener(self._writeMsg)
        print "%s connected." % (self.client_address,)


    def finish(self):
        self.server._chat_room.removeListener(self._writeMsg)
        SocketServer.StreamRequestHandler.finish(self)
        print "%s disconnected." % (self.client_address,)


    def _writeMsg(self, msg):
        self.wfile.write(msg)

if __name__ == '__main__':
    import sys
    port = int(sys.argv[1])
    server = ChatThreadedServer(('localhost', port),
                                ChatRequestHandler)
    try:
        print "Server starting.  Now waiting."
        server.serve_forever()
    except:
        server.shutdown()
        print "Shutting down... waiting for all clients to close."
