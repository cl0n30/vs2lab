import pickle
import sys
import time

import zmq

import countConst

id = sys.argv[1]
me = "reducer" + id

address_pull = ""
if id == "1":
  address_pull = "tcp://" + countConst.REDUCESRC + ":" + countConst.REDUCEPORT1
else: 
  address_pull = "tcp://" + countConst.REDUCESRC + ":" + countConst.REDUCEPORT2

context = zmq.Context()
pull_socket = context.socket(zmq.PULL)  # create a pull socket

pull_socket.bind(address_pull)  # connect to task source 1

wordsCount = {}

def countWord(word:str):
  if word in wordsCount:
    count = wordsCount.get(word)
    wordsCount.update({word: count+1})
  else:
    wordsCount[word] = 1
  print("{}: {}".format(word, wordsCount[word]))

time.sleep(1) 

print("{} started".format(me))

while True:
    word = pickle.loads(pull_socket.recv())  # receive word from a source
    #print("{} received word {} for reducer {}".format(me, word[1], word[0]))
    if (str(word[0]) == id):
      countWord(word[1])
    
