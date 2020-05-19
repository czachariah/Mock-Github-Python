# This is the server program.
# Author: Chris Zachariah - chriszachariah3@gmail.com

import socket
import sys
from _thread import *
import threading
import os

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
        print('[S]: Connected to: ' + str(addr[0]) + ' : ' + str(addr[1]))

        # Start a new thread and return its identifier
        start_new_thread(serverAction, (c,))
    s.close()


def serverAction(c):
    action = c.recv(1024)

    if action == "create":
        # send the command back to the client to let it know that it ready to receive command specific info
        c.send("create".encode('utf-8'))

        # get the new project name
        data = c.recv(1024)

        # check the current directory for the project folder
        isFound = os.path.isdir(data)

        if isFound:
            c.send("FOUND".encode('utf-8'))
            print("[S]: Another directory with the same name (" + str(data) + ") has been found.")
        else:
            parentPath = os.path.dirname(os.path.abspath(__file__))
            newProJPath = os.path.join(parentPath, data)
            os.mkdir(newProJPath)
            manifestPath = os.path.join(parentPath, data, "Manifest.txt")
            try:
                f = open(manifestPath, "w+")
                f.write("0\n")
                f.close()
            except IOError:
                print("[S]: There was an error creating the Manifest.txt for the new project.")
                c.send("ERROR".encode('utf-8'))
                lock.release()
                c.close()
                print("[S]: Client connection dealt with and terminated.\n")
                return

            print("[S]: New project: '" + data + "' created.")
            c.send("DONE".encode('utf-8'))

            lastData = c.recv(1024)
            if lastData == "ERROR":
                os.remove(manifestPath)
                os.rmdir(newProJPath)
    elif action == "update":
        # send the command back to the client to let it know that it ready to receive command specific info
        c.send("update".encode('utf-8'))

        # get the new project name
        data = c.recv(1024)

        # check the current directory for the project folder
        isFound = os.path.isdir(data)

        if isFound:
            print("[S]: The project directory has been found.")
            c.send("FOUND".encode('utf-8'))


        else:
            print("[S]: The project directory has not been found.")
            c.send("ERROR".encode('utf-8'))
            lock.release()
            c.close()
            print("[S]: Client connection dealt with and terminated.\n")
            return
    else:
        print("???")

    lock.release()
    c.close()
    print("[S]: Client connection dealt with and terminated.\n")


if __name__ == "__main__":
    server()
