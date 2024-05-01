import rpc
import logging

from context import lab_logging

lab_logging.setup(stream_level=logging.INFO)

cl = rpc.Client()
cl.run()

def printResult(result):
  print("Result: {}".format(result.value))

base_list = rpc.DBList({'foo'})
cl.append('bar', base_list, printResult)

cl.stop()
