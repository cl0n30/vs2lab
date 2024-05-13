import pickle
import sys
import time

import zmq

import countConst

id = sys.argv[1]

me = "mapper" + id
address_pull = "tcp://" + countConst.SPLITSRC + ":" + countConst.SPLITPORT  # task src

address_push1 = "tcp://" + countConst.REDUCESRC + ":" + countConst.REDUCEPORT1 # reducer 1
address_push2 = "tcp://" + countConst.REDUCESRC + ":" + countConst.REDUCEPORT2 # reducer 2

context = zmq.Context()
pull_socket = context.socket(zmq.PULL)  # create a pull socket
push_socket1 = context.socket(zmq.PUSH)
push_socket2 = context.socket(zmq.PUSH)

pull_socket.connect(address_pull)  # connect to task source
push_socket1.connect(address_push1)
push_socket2.connect(address_push2)

def splitSentence(s:str, removePunctuation = True):
  words = []
  s = s.strip()
  if removePunctuation:
    s = s.replace(",", "").replace(".", "")
  for word in s.split(" "):
    words.append(word)
  return words

def sendToReducer(words:list[str]):
  for word in words:
    reducer = (len(word) % 2) + 1
    print("send to reducer {}".format(reducer))
    if reducer == 1:
      push_socket1.send(pickle.dumps((reducer, word)))
    else:
      push_socket2.send(pickle.dumps((reducer, word)))
  
time.sleep(1) 

print("{} started".format(me))

while True:
    work = pickle.loads(pull_socket.recv())  # receive sentence from a source
    print("{} received sentence from {}".format(me, work[0]))
    words = splitSentence(work[1])
    sendToReducer(words)
    
  
