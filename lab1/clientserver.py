"""
Client and server using classes
"""

import logging
import socket

import const_cs
from context import lab_logging

lab_logging.setup(stream_level=logging.INFO)  # init loging channels for the lab

# pylint: disable=logging-not-lazy, line-too-long

class Server:
    """ The server """
    _logger = logging.getLogger("vs2lab.lab1.clientserver.Server")
    _serving = True

    def __init__(self, dictSize=1):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # prevents errors due to "addresses in use"
        self.sock.bind((const_cs.HOST, const_cs.PORT))
        self.sock.settimeout(3)  # time out in order not to block forever
        self._logger.info("Server bound to socket " + str(self.sock))
        self.api = TelephoneApiServer(dictSize=dictSize)

    def serve(self):
        """ Serve echo """
        self.sock.listen(1)
        while self._serving:  # as long as _serving (checked after connections or socket timeouts)
            try:
                # pylint: disable=unused-variable
                (connection, address) = self.sock.accept()  # returns new socket and address of client
                self._logger.info(f"Client connected on socket {self.sock}")
                while True:  # forever
                    self._logger.info("Receiving data on socket")
                    data = connection.recv(1024)  # receive data from client
                    if not data:
                        break  # stop if client stopped
                    data_out = self.api.handleRequest(data.decode('ascii'))
                    self._logger.info(f"Sending response {data_out}")
                    connection.send(data_out.encode('ascii')) 
                connection.close()  # close the connection
                self._logger.info("Connection closed")
            except socket.timeout:
                pass  # ignore timeouts
        self.sock.close()
        self._logger.info("Server down.")

class TelephoneApiServer:
    _logger = logging.getLogger("vs2lab.a1_layers.clientserver.TelephoneApiServer")

    _names = {"user0": "+490"}
    _commands = ["get", "getall"]
    
    def __init__(self, dictSize=1):
        for i in range(dictSize):
            self._names.update({f"user{i}": f"+49{i}"})

    def getCommandAndArgs(self, msg:str):
        split = msg.split("#")
        args = []
        if len(split) > 1:
            args = split[1].split(",")
        return (split[0], args)

    def handleRequest(self, req:str):
        command, args = self.getCommandAndArgs(req)          
        match command:                
            case "get":
                return self.getNumber(args[0])
            case "getall":
                return self.getAllNumbers()
            case _:
                return self.echo(command)
            
    def echo(self, msg):
        return msg+"*"

    def getNumber(self, name):
        number = self._names.get(name)
        if (number == None):
            return "No number"
        return number
    
    def getAllNumbers(self):
        numbers = ""
        for i, name in enumerate(self._names):
            if (i == len(self._names)-1):
                numbers+=f"{name}:{self._names.get(name)}"
            else:
                numbers+=f"{name}:{self._names.get(name)};"
        return numbers

class Client:
    """ The client """
    logger = logging.getLogger("vs2lab.a1_layers.clientserver.Client")

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((const_cs.HOST, const_cs.PORT))
        self.logger.info("Client connected to socket " + str(self.sock))

    def call(self, msg_in="Hello, world"):
        """ Call server """
        self.sock.send(msg_in.encode('ascii'))  # send encoded string as data
        data = self.sock.recv(1024)  # receive the response
        msg_out = data.decode('ascii')
        print(msg_out)  # print the result
        self.sock.close()  # close the connection
        self.logger.info("Client down.")
        return msg_out

    def sendRequest(self, req:str):
        self.sock.send(req.encode('ascii'))
        self.logger.info(f"Request sent {req}")
        res = self.sock.recv(1024)
        data = res.decode('ascii')
        self.logger.info(f"Response received {data}")
        return data

    def close(self):
        """ Close socket """
        self.sock.close()
        self.logger.info("Client down")
        return

class TelephoneApi:
    _logger = logging.getLogger("vs2lab.a1_layers.clientserver.TelephoneApi")

    def __init__(self):
        self.client = Client()
    
    def get(self, name):
        request = f"get#{name}"
        telephone_out = self.client.sendRequest(request)
        return telephone_out
    
    def getAll(self): 
        request = "getall#"
        names = self.client.sendRequest(request)
        return names.split(";")
    
    def disconnect(self):
        self.client.close()
