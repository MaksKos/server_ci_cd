# pylint: disable=missing-docstring, unused-variable

import socket
import argparse
import threading
import queue
import re
import json
import collections
import requests

HOST = '0.0.0.0'
PORT = 3000
SIZE = 4096
REDIRECT = True


class Worker(threading.Thread):

    count = 0

    def __init__(self, que, n_top, lock) -> None:
        self.que = que
        self.size = n_top
        self.lock = lock
        self._is_run = True
        super().__init__()

    def url_stat(self, url):
        req = requests.get(url, timeout=60, allow_redirects=REDIRECT).text
        text = re.sub('<[^>]*>', '', req).split()
        count = collections.Counter(text)
        to_json = dict(count.most_common(self.size))
        return json.dumps(to_json)

    def run(self) -> None:
        while self._is_run:
            new_sock = self.que.get()
            with new_sock as sock:
                try:
                    while True:
                        data = sock.recv(4096)
                        if data:
                            try:
                                url = data.decode()
                                res = "Result: " + self.url_stat(url)
                            except requests.exceptions.RequestException as req_err:
                                # print(req_err)
                                sock.sendall(f"URL errro\n {req_err}".encode())
                                continue

                            sock.sendall(res.encode())

                            self.lock.acquire()
                            self.__class__.count += 1
                            # print(f'{self.count} urls have done: {url}')
                            self.lock.release()
                        else:
                            self.que.task_done()
                            break

                except socket.error as error:
                    print(error.strerror)
                    continue


class Master(threading.Thread):

    def __init__(self, que) -> None:
        self.que = que
        self._is_run = True
        super().__init__()

    def run(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
            server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_sock.bind((HOST, PORT))
            server_sock.listen(5)
            while self._is_run:
                try:
                    client_sock, addr = server_sock.accept()
                except socket.error as error:
                    print(error.strerror)
                    continue
                print("client connected", client_sock)
                self.que.put(client_sock)


def main(workers: int, n_top: int):
    que = queue.Queue()
    lock = threading.Lock()
    threads = [Worker(que, n_top, lock) for _ in range(workers)]
    threads.append(Master(que))
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    que.join()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-w')
    parser.add_argument('-k')
    args = parser.parse_args()
    print(f"{args.w=}, {args.k=}")
    main(int(args.w), int(args.k))
