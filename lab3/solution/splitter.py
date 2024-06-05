import pickle
import time

import zmq

import countConst

me = "split"

f = open("words.txt", "r")

src = countConst.SPLITSRC 
prt = countConst.SPLITPORT

context = zmq.Context()
push_socket = context.socket(zmq.PUSH)  # create a push socket

address = "tcp://" + src + ":" + prt  # how and where to connect
push_socket.bind(address)  # bind socket to address

time.sleep(1) # wait to allow all clients to connect

for line in f:
  push_socket.send(pickle.dumps((me, line)))  # send workload to worker
