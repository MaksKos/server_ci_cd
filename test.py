# pylint: disable=missing-docstring

import socket
import queue
import collections
from io import StringIO
from unittest import TestCase, mock
import client
import server

HOST = 'localhost'    # The remote host
PORT = 8080       # The same port as used by the server


class TestClient(TestCase):

    def setUp(self) -> None:
        self.n_url = 3
        self.urls = "url1\nurl2\nurl3\n"
        self.file = StringIO()
        self.file.write(self.urls)
        self.file.seek(0)

    @mock.patch('client.threading')
    def test_main_thread(self, mock_thr):
        n_thread = 5
        with mock.patch('client.open') as file:
            client.main(n_thread, 'url.txt')
            self.assertEqual(mock_thr.Lock.call_count, 1)
            self.assertEqual(mock_thr.Thread.call_count, n_thread)

            args = mock.call(target=client.thread_socket,
                             args=(file().__enter__(), mock_thr.Lock()))

            self.assertEqual(mock_thr.Thread.call_args, args)
            self.assertEqual(mock_thr.Thread().start.call_count, n_thread)
            self.assertEqual(mock_thr.Thread().join.call_count, n_thread)

    @mock.patch('client.threading')
    def test_main_file(self, _):
        n_thread = 5
        file_name = 'url.txt'
        call_file = mock.call(file_name)
        with mock.patch('client.open') as file:
            client.main(n_thread, file_name)
            self.assertEqual(file.call_count, 1)
            self.assertEqual(file.call_args, call_file)

    @mock.patch('client.socket.socket')
    @mock.patch('client.print')
    def test_thread_socket(self, mock_print, mock_sock):
        sock_param = mock.call(socket.AF_INET, socket.SOCK_STREAM)
        sock_s = mock_sock().__enter__()
        lock = mock.Mock()
        sock_s.recv.side_effect = [(val+'\n').encode()
                                   for val in self.urls.split('\n')]
        send = [mock.call((val+'\n').encode())
                for val in self.urls.split()]
        echo = [mock.call('{}: {}'.format(val+"\n", val+"\n"))
                for val in self.urls.split()]
        
        client.thread_socket(self.file, lock)

        self.assertEqual(mock_sock.call_args, sock_param)
        self.assertEqual(sock_s.connect.call_count, 1)
        self.assertEqual(sock_s.setsockopt.call_count, 1)
        self.assertEqual(sock_s.connect.call_args, mock.call((HOST, PORT)))

        self.assertEqual(lock.acquire.call_count, self.n_url+1)
        self.assertEqual(lock.release.call_count, self.n_url+1)

        self.assertEqual(sock_s.sendall.call_count, self.n_url)
        self.assertEqual(sock_s.recv.call_count, self.n_url)
        self.assertEqual(sock_s.sendall.call_args_list, send)

        self.assertEqual(mock_print.call_count, self.n_url)
        self.assertEqual(mock_print.call_args_list, echo)


class TestServer(TestCase):

    def setUp(self) -> None:
        self.n_work = 4
        self.n_top = 2

    @mock.patch('server.Master')
    @mock.patch('server.Worker')
    @mock.patch('server.queue')
    def test_main(self, mock_que, mock_work, mock_mast):
        server.main(self.n_work, self.n_top)
        self.assertEqual(mock_work.call_count, self.n_work)
        self.assertEqual(mock_mast.call_count, 1)
        que = mock_que.Queue()
        args_work = mock.call(que, self.n_top)
        args_mast = mock.call(que)
        self.assertEqual(mock_work.call_args, args_work)
        self.assertEqual(mock_mast.call_args, args_mast)

        self.assertEqual(mock_work().start.call_count, self.n_work)
        self.assertEqual(mock_mast().start.call_count, 1)
        self.assertEqual(mock_work().join.call_count, self.n_work)
        self.assertEqual(mock_mast().join.call_count, 1)

    def test_master(self):
        que = queue.Queue()
        master = server.Master(que)
        master.setDaemon(True)
        master.start()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.connect((server.HOST, server.PORT))
        master._is_run = False
        master.join()
        self.assertTrue(isinstance(que.get(), socket.socket))

    @mock.patch('server.requests')
    def test_worker(self, req):

        Text = collections.namedtuple('Text', 'text')

        req.get.side_effect = Text('a the a a the f g g'), Text(' t t t  t')

        urls = ['url1', 'url2']

        answer = []

        que = queue.Queue()
        master = server.Master(que)
        worker = server.Worker(que, self.n_top)
        master.setDaemon(True)
        worker.setDaemon(True)
        master.start()
        worker.start()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.connect((server.HOST, server.PORT))
            for url in urls:
                sock.sendall(url.encode())
                data = sock.recv(4096)
                answer.append(data.decode())

        worker._is_run = False
        master._is_run = False
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.connect((server.HOST, server.PORT))
        worker.join()
        master.join()
        self.assertEqual(server.Worker.count, 2)
        self.assertEqual(answer, ['{"a": 3, "the": 2}', '{"t": 4}'])
        self.assertEqual(req.get.call_args_list,
                         [mock.call(urls[0], allow_redirects=False),
                          mock.call(urls[1], allow_redirects=False)]
                         )
