# This is the client program.
# Author: Chris Zachariah - chriszachariah3@gmail.com

import socket
import sys
import os
import hashlib


def configure():
    if len(sys.argv) != 4:
        print("[C]: ERROR: Please make sure to include the HostName/IPAddress and PortNumber of the server.")
        return

    serverAdd = socket.gethostbyname(sys.argv[2])
    serverPort = int(sys.argv[3])
    if serverPort <= 1023:
        print("[C]: ERROR: Need to make sure that the port number is strictly greater thn 1023. Please try again.\n")
        return

    # try to find a RESOLVED.txt, delete it if it exists and then make a new one to write and append to
    dir_name = os.path.dirname(os.path.abspath(__file__))
    configFile = os.path.join(dir_name, "config" + "." + "txt")
    if os.path.exists(configFile):
        os.remove(configFile)
    cfd = open("config.txt", "a+")

    cfd.write(serverAdd + "\n")
    cfd.write(str(serverPort) + "\n")
    cfd.close()

    print("[C]: Server address and port number have been added to the config.txt file.")


def create():
    if len(sys.argv) != 3:
        print("[C]: ERROR: Please make sure to include the project name for the argument.")
        return

    addressAndPort = list()
    try:
        configFD = open("config.txt", "r")
        for line in configFD:
            line = line.replace("\r", "").replace("\n", "")
            addressAndPort.append(line)
    except IOError:
        print("[C]: ERROR: Must first run the configure command before trying to connect with the server.")
        return

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("[C]: Socket created to connect to server.")
    except socket.error as err:
        print('[C]: Socket Open Error: {} \n'.format(err))
        return

    try:
        # get the host name and the port number ready to be ready to connect to the server
        addr = socket.gethostbyname(addressAndPort[0])

        # now connect to the server
        server_binding = (addr, int(addressAndPort[1]))
        s.connect(server_binding)
        print("[C]: Connected to the server.")
    except:
        print("[C]: There was a problem connecting to the server. Please try again.")
        s.close()
        return

    # let the server know which command the client wants to use
    s.send("create".encode('utf-8'))

    # reply from the server that tells the client that it is ready to go
    data_from_server = s.recv(1024)
    if data_from_server != "create":
        print("[C]: ERROR: An issue occurred when using the 'create' command. Please try again.")
        s.close()
        return

    # send the server the project name
    s.send(sys.argv[2].encode('utf-8'))

    # get response from the server
    data_from_server = s.recv(1024)
    if data_from_server == "FOUND":
        print("[C]: There is already a project named '" + str(sys.argv[2]) + "' in the server.")
    if data_from_server == "ERROR":
        print("[C]: There was an error making the new project in the server. Please try again")
    if data_from_server == "DONE":
        print("[C]: The new project directory for: '" + str(sys.argv[2]) + "' has been made.")

        # create a local version of the new project as well with a Manifest.txt inside
        parentPath = os.path.dirname(os.path.abspath(__file__))
        newProJPath = os.path.join(parentPath, str(sys.argv[2]))
        os.mkdir(newProJPath)
        manifestPath = os.path.join(parentPath, str(sys.argv[2]), "Manifest.txt")
        try:
            f = open(manifestPath, "w+")
            f.write("0\n")
            f.close()
            s.send("DONE".encode('utf-8'))
        except IOError:
            print("[S]: ERROR: There was a problem making the Manifest.txt file in the new project. Please try again.\n")
            s.send("ERROR".encode('utf-8'))
            os.rmdir(newProJPath)
            s.close()
            return
    # close the socket
    s.close()
    return


def remove():
    if len(sys.argv) != 4:
        print("[C]: ERROR: Please make sure to include the project name and the file name for the arguments.")
        return
        # check if the file is in the directory already
    parentPath = os.path.dirname(os.path.abspath(__file__))
    filePath = os.path.join(parentPath, str(sys.argv[2]), str(sys.argv[3]))
    try:
        f = open(filePath, "r")
        f.close()
        print("[C]: Please make sure that the file is removed from the project directory.")
        return
    except IOError:
        print("[C]: Starting to update Manifest ... ")

    manifestPath = os.path.join(parentPath, str(sys.argv[2]), "Manifest.txt")

    # separate the lines into words and store each word into a list
    dataList = list()
    try:
        file = open(manifestPath, "r")
        for line in file:
            for word in line.replace("\n", "").split(" , "):
                dataList.append(word)
    except IOError:
        print("[C]: ERROR opening the Manifest.txt file. Please try again.")
        return
    file.close()

    if filePath in dataList:
        index = dataList.index(filePath)
        dataList.pop(index)
        dataList.pop(index)
        dataList.pop(index)
    else:
        print("[C]: The file (" + str(sys.argv[3]) + ") was not found in the Manifest.txt in the project (" + str(sys.argv[2]) + ") directory.")
        return

    # write into the Manifest
    os.remove(manifestPath)
    f = open(manifestPath, "a+")
    f.write(str(dataList.pop(0)) + "\n")
    count = 1
    for x in dataList:
        if count != 3:
            f.write(x + " , ")
            count = count + 1
        else:
            f.write(x + "\n")
            count = 1
    f.close()
    print("[C]: Manifest updated.")
    return


def add():
    if len(sys.argv) != 4:
        print("[C]: ERROR: Please make sure to include the project name and the file name for the arguments.")
        return

    # check if the file is in the directory already
    parentPath = os.path.dirname(os.path.abspath(__file__))
    filePath = os.path.join(parentPath, str(sys.argv[2]), str(sys.argv[3]))
    try:
        f = open(filePath, "r")
        f.close()
        print("[C]: Starting to update Manifest ... ")
    except IOError:
        print("[C]: ERROR: There was a problem opening the file. Please try running the command again.\n")
        return

    # using SHA1 hashing here
    blockSize = 65536
    hasher = hashlib.sha1()
    with open(filePath, 'rb') as afile:
        buf = afile.read(blockSize)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(blockSize)
    totalHash = hasher.hexdigest()

    manifestPath = os.path.join(parentPath, str(sys.argv[2]), "Manifest.txt")

    # separate the lines into words and store each word into a list
    dataList = list()
    try:
        file = open(manifestPath, "r")
        for line in file:
            for word in line.replace("\n", "").split(" , "):
                dataList.append(word)
    except IOError:
        print("[C]: ERROR opening the Manifest.txt file. Please try again.")
        return
    file.close()

    if filePath in dataList:
        index = dataList.index(filePath)
        if dataList[index+2] == totalHash:
            print("[C]: This file already exists in the Manifest.txt. and is up-to-date")
            return
        else:
            dataList[index + 2] = totalHash
            oldV = int(dataList[index + 1])
            newV = oldV + 1
            dataList[index + 1] = str(newV)

    else:
        dataList.append(filePath)
        dataList.append(str(0))
        dataList.append(totalHash)

    # write into the Manifest
    os.remove(manifestPath)
    f = open(manifestPath, "a+")
    f.write(str(dataList.pop(0)) + "\n")
    count = 1
    for x in dataList:
        if count != 3:
            f.write(x + " , ")
            count = count + 1
        else:
            f.write(x + "\n")
            count = 1
    f.close()
    print("[C]: Manifest updated.")
    return


def update():
    if len(sys.argv) != 3:
        print("[C]: ERROR: Please make sure to include the project name for the argument.")
        return

    addressAndPort = list()
    try:
        configFD = open("config.txt", "r")
        for line in configFD:
            line = line.replace("\r", "").replace("\n", "")
            addressAndPort.append(line)
    except IOError:
        print("[C]: ERROR: Must first run the configure command before trying to connect with the server.")
        return

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("[C]: Socket created to connect to server.")
    except socket.error as err:
        print('[C]: Socket Open Error: {} \n'.format(err))
        return

    try:
        # get the host name and the port number ready to be ready to connect to the server
        addr = socket.gethostbyname(addressAndPort[0])

        # now connect to the server
        server_binding = (addr, int(addressAndPort[1]))
        s.connect(server_binding)
        print("[C]: Connected to the server.")
    except:
        print("[C]: There was a problem connecting to the server. Please try again.")
        s.close()
        return

    # let the server know which command the client wants to use
    s.send("update".encode('utf-8'))

    # reply from the server that tells the client that it is ready to go
    data_from_server = s.recv(1024)
    if data_from_server != "update":
        print("[C]: ERROR: An issue occurred when using the 'create' command. Please try again.")
        s.close()
        return

    # send the server the project name
    s.send(sys.argv[2].encode('utf-8'))

    # get response from the server
    data_from_server = s.recv(1024)

    if data_from_server == "FOUND":
        print("[C]: Waiting for the Manifest.txt contents from the server ...")
        parentPath = os.path.dirname(os.path.abspath(__file__))
        serverManifestPath = os.path.join(parentPath, str(sys.argv[2]), "Manifest_Server.txt")
        try:
            f = open(serverManifestPath, "w+")
            s.send("WAITING".encode('utf-8'))
            signal = s.recv(1024)
            if signal == "ERROR":
                print("[C]: Server had problems opening the Manifest.txt. Please try again.\n")
                s.close()
                return
            else:
                s.send("READY".encode('utf-8'))
            while True:
                data = s.recv(1024)
                if not data:
                    break
                f.write(data)
            f.close()
            s.send("DONE".encode('utf-8'))
            print("[C]: The contents have been received. Now doing comparisons ...")

            ManifestPath = os.path.join(parentPath, str(sys.argv[2]), "Manifest.txt")
            # put all the contents of the Manifest into a list
            manifestList = list()
            try:
                file = open(ManifestPath, "r")
                for line in file:
                    for word in line.replace("\n", "").split(" , "):
                        manifestList.append(word)
            except IOError:
                print("[C]: ERROR opening the Manifest.txt file. Please try again.")
                return
            file.close()

            # put all the contents of the Manifest_Server into a list
            manifestServerList = list()
            try:
                file = open(serverManifestPath, "r")
                for line in file:
                    for word in line.replace("\n", "").split(" , "):
                        manifestServerList.append(word)
            except IOError:
                print("[C]: ERROR opening the Manifest_Server.txt file. Please try again.")
                return
            file.close()

            # make an Update.txt file
            UpdatePath = os.path.join(parentPath, str(sys.argv[2]), "Update.txt")
            if os.path.exists(UpdatePath):
                os.remove(UpdatePath)
            try:
                f = open(UpdatePath, "a+")
                updateList = list()
                # gets rid of the Manifest version number in the list
                manifestServerList.pop(0)
                manifestList.pop(0)
                while manifestServerList:
                    if manifestServerList[0] in manifestList:
                        index = manifestList.index(manifestServerList[0])
                        if str(manifestServerList[1]) == str(manifestList[index + 1]):
                            if str(manifestServerList[2]) != str(manifestList[index + 2]):
                                print("A" + str(manifestServerList[0]))
                                updateList.append(str("A"))
                                updateList.append(str(manifestServerList.pop(0)))
                                updateList.append(str(manifestServerList.pop(0)))
                                updateList.append(str(manifestServerList.pop(0)))
                                manifestList.pop(index)
                                manifestList.pop(index)
                                manifestList.pop(index)
                        else:
                            print("A" + str(manifestServerList[0]))
                            updateList.append(str("A"))
                            updateList.append(str(manifestServerList.pop(0)))
                            updateList.append(str(manifestServerList.pop(0)))
                            updateList.append(str(manifestServerList.pop(0)))
                            manifestList.pop(index)
                            manifestList.pop(index)
                            manifestList.pop(index)
                    else:
                        print("A" + str(manifestServerList[0]))
                        updateList.append(str("A"))
                        updateList.append(str(manifestServerList.pop(0)))
                        updateList.append(str(manifestServerList.pop(0)))
                        updateList.append(str(manifestServerList.pop(0)))
                # now go throgh the client manifest list and find files that the server does not have (these need to be uploaded)

                # then write all the contents of the updateList into the Update.txt file
            except:
                print("[C]: ERROR opening the Update.txt file. Please try again.")
                return
        except IOError:
            print("[S]: ERROR: There was a problem making the Manifest_Server.txt file in the project. Please try again.\n")
            s.send("ERROR".encode('utf-8'))
            s.close()
            return
    else:
        print("[C]: The project directory was not found on the server side. Please try again or resolve the issue manually.\n")
        s.close()
        return

    # close the socket
    s.close()
    return


def client():
    if len(sys.argv) < 2:
        print("[C]: ERROR: Not enough arguments given. Please try again.")
        print("[C]: Closing client program.")
        exit()
    if sys.argv[1] == "configure":
        configure()
    elif sys.argv[1] == "checkout":
        print("[C]: checkout")
    elif sys.argv[1] == "update":
        update()
    elif sys.argv[1] == "upgrade":
        print("[C]: upgrade")
    elif sys.argv[1] == "commit":
        print("[C]: commit")
    elif sys.argv[1] == "push":
        print("[C]: push")
    elif sys.argv[1] == "create":
        create()
    elif sys.argv[1] == "destroy":
        print("[C]: destroy")
    elif sys.argv[1] == "add":
        add()
    elif sys.argv[1] == "remove":
        remove()
    elif sys.argv[1] == "currentversion":
        print("[C]: currentversion")
    elif sys.argv[1] == "history":
        print("[C]: history")
    elif sys.argv[1] == "rollback":
        print("[C]: rollback")
    else:
        print("[C]: ERROR: Invalid command used. Please try again.")
    print("[C]: Closing client program.")
    exit()


if __name__ == '__main__':
    client()
