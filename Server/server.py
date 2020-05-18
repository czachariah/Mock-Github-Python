# This is the server program.
# Author: Chris Zachariah - chriszachariah3@gmail.com

import socket
import sys
from _thread import *
import threading

lock = threading.Lock()

def server():
        if len(sys.argv) != 2:
                print("[S]: Please make sure to the port number in the arguments.\n")
                exit()

        portNum = int(sys.argv[1])
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_binding = ('', portNum)
        s.bind(server_binding)
        print("[S]: Socket created and bound to port: " + sys.argv[1])

        # put the socket into listening mode
        s.listen(8)
        print("[S]: Socket is listening ... \n")

        # a forever loop until client wants to exit
        while True:
                # establish connection with client
                c, addr = s.accept()

                # lock acquired by client
                lock.acquire()
                print('[S]: Connected to: ', addr[0], ' : ', addr[1], '\n')

                # Start a new thread and return its identifier
                start_new_thread(serverAction, c)
        s.close()


def serverAction(c):
        data = c.recv(1024)
        print("[S]: From client: " + data)

        c.send(data + "received")

        lock.release()

        c.close()
        print("[S]: Client connection dealt with and terminated.\n")


if __name__ == "__main__":
        server()
