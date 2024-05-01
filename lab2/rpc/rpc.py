import constRPC
import threading
import time

from context import lab_channel


class DBList:
    def __init__(self, basic_list):
        self.value = list(basic_list)

    def append(self, data):
        self.value = self.value + [data]
        return self


class Client:
    def __init__(self):
        self.chan = lab_channel.Channel()
        self.client = self.chan.join('client')
        self.server = None

    def run(self):
        self.chan.bind(self.client)
        self.server = self.chan.subgroup('server')

    def stop(self):
        self.chan.leave('client')

    def append(self, data, db_list, callback = None):
        background = AsyncAppend(data, db_list, self.chan, callback, self.error)
        background.start()
        self.working()
        background.join()
        print("Client waited until background work was done")
        
    def working(self):
        print("Client working")
        print("Client doing stuff in the foreground")
        print("Client doing more stuff")
        print("Client doing some more stuff")
        print("Client doing more things")
        
    def error(self, msg):
        print("Error: "+msg)
 
class AsyncAppend(threading.Thread):
    def __init__(self, data, db_list, chan:lab_channel.Channel, callback = None, error = None):
        threading.Thread.__init__(self)
        self.data = data
        self.db_list = db_list
        self.chan = chan
        self.server = self.chan.subgroup('server')
        self.timeout = 3
        self.callback = callback
        self.error = error
        
    def run(self):
        self.startAppend()
        
    def startAppend(self):
        assert isinstance(self.db_list, DBList)
        msglst = (constRPC.APPEND, self.data, self.db_list)  # message payload
        self.chan.send_to(self.server, msglst)
        msgack = self.chan.receive_from(self.server, self.timeout) # wait for ACK
        if msgack == None:
            if self.error:
                self.error("No ACK received")
            return
        msgrcv = self.chan.receive_from(self.server) # wait for response
        if self.callback:
            self.callback(msgrcv[1])

class Server:
    def __init__(self):
        self.chan = lab_channel.Channel()
        self.server = self.chan.join('server')
        self.timeout = 3

    @staticmethod
    def append(data, db_list):
        assert isinstance(db_list, DBList)  # - Make sure we have a list
        return db_list.append(data)

    def run(self):
        self.chan.bind(self.server)
        while True:
            msgreq = self.chan.receive_from_any(self.timeout)  # wait for any request
            if msgreq is not None:
                client = msgreq[0]  # see who is the caller
                msgrpc = msgreq[1]  # fetch call & parameters
                if constRPC.APPEND == msgrpc[0]:  # check what is being requested
                    #time.sleep(5) #too long to send ack
                    connEst = self.sendAck(client)
                    if connEst:
                        time.sleep(10)
                        result = self.append(msgrpc[1], msgrpc[2])  # do local call
                        self.chan.send_to({client}, result)  # return response
                    else:
                        print("Client unavailable, continuing...")
                else:
                    pass  # unsupported request, simply ignore
                
    def sendAck(self, client):
        if self.chan.exists(client):
            self.chan.send_to({client}, (constRPC.ACK, "append"))
            return True
        else:
            return False
