"""
Simple client server unit test
"""

import logging
import threading
import unittest

import clientserver
from context import lab_logging

lab_logging.setup(stream_level=logging.INFO)


class TestEchoService(unittest.TestCase):
    """The test"""
    _server = clientserver.Server()  # create single server in class variable
    _server_thread = threading.Thread(target=_server.serve)  # define thread for running server

    @classmethod
    def setUpClass(cls):
        cls._server_thread.start()  # start server loop in a thread (called only once)

    def setUp(self):
        super().setUp()
        self.client = clientserver.Client()  # create new client for each test

    def test_srv_get(self):  # each test_* function is a test
        """Test simple call"""
        msg = self.client.call("Hello VS2Lab")
        self.assertEqual(msg, 'Hello VS2Lab*')

    def tearDown(self):
        self.client.close()  # terminate client after each test

    @classmethod
    def tearDownClass(cls):
        cls._server._serving = False  # break out of server loop. pylint: disable=protected-access
        cls._server_thread.join()  # wait for server thread to terminate
        
class TestTelephoneService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._server = clientserver.Server(10)
        cls._server_thread = threading.Thread(target=cls._server.serve)
        cls._server_thread.start()
        
    def setUp(self):
        super().setUp()
        self.api = clientserver.TelephoneApi()
        
    def test_api_get(self):
        name = "user0"
        number = self.api.get(name)
        self.assertEqual(number, "+490")
        
    def test_api_get2(self):
        name = "user9"
        number = self.api.get(name)
        self.assertEqual(number, "+499")
        
    def test_api_getAll(self):
        numbers = self.api.getAll()
        print(numbers)
        self.assertEqual(10, len(numbers))
        
    def tearDown(self):
        self.api.disconnect()
        
    @classmethod
    def tearDownClass(cls):
        cls._server._serving = False
        cls._server_thread.join()
        
class TestServerApi(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.api = clientserver.TelephoneApiServer(2)
        
    def test_getNumber(self):
        name = "user0"
        expected = "+490"
        self.assertEqual(expected, self.api.getNumber(name))
        
    def test_api_get_none(self):
        name = "nonexistant"
        self.assertEqual("No number", self.api.getNumber(name))
        
    def test_getAllNumbers(self):
        expected = "user0:+490;user1:+491"
        self.assertEqual(expected, self.api.getAllNumbers())
        
    def test_echo(self):
        expected = "Hello World*"
        self.assertEqual(expected, self.api.echo("Hello World"))
        
    def tearDown(self):
        return super().tearDown()

if __name__ == '__main__':
    unittest.main()
