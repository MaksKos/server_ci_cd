# pylint: disable=missing-docstring

# import collections
# import threading
# import socket
# import queue
# from io import StringIO
from unittest import TestCase, mock

import server

HOST = 'localhost'    # The remote host
server.HOST = HOST

class TestServer(TestCase):

    def setUp(self) -> None:
        self.n_work = 4
        self.n_top = 2

    @mock.patch('server.Master')
    @mock.patch('server.Worker')
    @mock.patch('server.queue')
    @mock.patch('server.threading.Lock')
    def test_main(self,  mock_threads: mock, mock_que, mock_work, mock_mast):

        server.main(self.n_work, self.n_top)
        self.assertEqual(mock_work.call_count, self.n_work)
        self.assertEqual(mock_mast.call_count, 1)

        que = mock_que.Queue()
        args_work = mock.call(que, self.n_top, mock_threads())
        args_mast = mock.call(que)
        self.assertEqual(mock_work.call_args, args_work)
        self.assertEqual(mock_mast.call_args, args_mast)

        self.assertEqual(mock_work().start.call_count, self.n_work)
        self.assertEqual(mock_mast().start.call_count, 1)
        self.assertEqual(mock_work().join.call_count, self.n_work)
        self.assertEqual(mock_mast().join.call_count, 1)

    # def test_master(self):
    #     server.PORT = 6000
    #     que = queue.Queue()
    #     master = server.Master(que)
    #     master.setDaemon(True)
    #     master.start()
    #     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    #         sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #         sock.connect((HOST, server.PORT))
    #     master._is_run = False
    #     master.join()
    #     self.assertTrue(isinstance(que.get(), socket.socket))

    # @mock.patch('server.requests')
    # def test_worker(self, req):

    #     server.PORT = 5000

    #     Text = collections.namedtuple('Text', 'text')

    #     req.get.side_effect = Text('a the a a the f g g'), Text(' t t t  t')

    #     urls = ['url1', 'url2']

    #     answer = []
    #     # make a simple client
    #     lock = threading.Lock()
    #     que = queue.Queue()
    #     master = server.Master(que)
    #     worker = server.Worker(que, self.n_top, lock)
    #     master.setDaemon(True)
    #     worker.setDaemon(True)
    #     master.start()
    #     worker.start()
    #     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    #         sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #         sock.connect((HOST, server.PORT))
    #         for url in urls:
    #             sock.sendall(url.encode())
    #             data = sock.recv(4096)
    #             answer.append(data.decode())

    #     worker._is_run = False
    #     master._is_run = False
    #     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    #         sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #         sock.connect((server.HOST, server.PORT))
    #     worker.join()
    #     master.join()
    #     self.assertEqual(server.Worker.count, 2)
    #     self.assertEqual(answer, ['{"a": 3, "the": 2}', '{"t": 4}'])
    #     self.assertEqual(req.get.call_args_list,
    #                      [mock.call(urls[0], allow_redirects=server.REDIRECT),
    #                       mock.call(urls[1], allow_redirects=server.REDIRECT)]
    #                      )
