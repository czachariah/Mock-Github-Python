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

    print("[C]: Server address and port number have been added to the config.txt file.\n")


def create():
    if len(sys.argv) != 3:
        print("[C]: ERROR: Please make sure to include the project name for the argument.\n")
        return

    addressAndPort = list()
    try:
        configFD = open("config.txt", "r")
        for line in configFD:
            line = line.replace("\r", "").replace("\n", "")
            addressAndPort.append(line)
    except IOError:
        print("[C]: ERROR: Must first run the configure command before trying to connect with the server.\n")
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
        print("[C]: Connected to the server.\n")
    except:
        print("[C]: There was a problem connecting to the server. Please try again.\n")
        s.close()
        return

    # let the server know which command the client wants to use
    s.send("create".encode('utf-8'))

    # reply from the server that tells the client that it is ready to go
    data_from_server = s.recv(1024)
    if data_from_server != "create":
        print("[C]: ERROR: An issue occurred when using the 'create' command. Please try again.\n")
        s.close()
        return

    # send the server the project name
    s.send(sys.argv[2].encode('utf-8'))

    # get response from the server
    data_from_server = s.recv(1024)
    if data_from_server == "FOUND":
        print("[C]: There is already a project named '" + str(sys.argv[2]) + "' in the server.\n")
    if data_from_server == "ERROR":
        print("[C]: There was an error making the new project in the server. Please try again\n")
    if data_from_server == "DONE":
        print("[C]: The new project directory for: '" + str(sys.argv[2]) + "' has been made.\n")
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
        print("[C]: ERROR: Please make sure to include the project name and the file name for the arguments.\n")
        return
        # check if the file is in the directory already
    parentPath = os.path.dirname(os.path.abspath(__file__))
    filePath = os.path.join(parentPath, str(sys.argv[2]), str(sys.argv[3]))
    try:
        f = open(filePath, "r")
        f.close()
        print("[C]: Please make sure that the file is removed from the project directory.\n")
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
        print("[C]: ERROR opening the Manifest.txt file. Please try again.\n")
        return
    file.close()

    if filePath in dataList:
        index = dataList.index(filePath)
        dataList.pop(index)
        dataList.pop(index)
        dataList.pop(index)
    else:
        print("[C]: The file (" + str(sys.argv[3]) + ") was not found in the Manifest.txt in the project (" + str(sys.argv[2]) + ") directory.\n")
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
    print("[C]: Manifest updated.\n")
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
        print("[C]: ERROR opening the Manifest.txt file. Please try again.\n")
        return
    file.close()

    if filePath in dataList:
        index = dataList.index(filePath)
        if dataList[index+2] == totalHash:
            print("[C]: This file already exists in the Manifest.txt. and is up-to-date\n")
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
    print("[C]: Manifest updated.\n")
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
        print("[C]: Connected to the server.\n")
    except:
        print("[C]: There was a problem connecting to the server. Please try again.")
        s.close()
        return

    # let the server know which command the client wants to use
    s.send("update".encode('utf-8'))

    # reply from the server that tells the client that it is ready to go
    data_from_server = s.recv(1024)
    if data_from_server != "update":
        print("[C]: ERROR: An issue occurred when using the 'update' command. Please try again.")
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
                os.remove(serverManifestPath)
                s.close()
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
                os.remove(serverManifestPath)
                s.close()
                return
            file.close()

            # make an Update.txt file
            UpdatePath = os.path.join(parentPath, str(sys.argv[2]), "Update.txt")
            if os.path.exists(UpdatePath):
                os.remove(UpdatePath)
            updateList = list()

            try:
                f = open(UpdatePath, "a+")
                serverManifestVersion = int(manifestServerList.pop(0))
                clientManifestVersion = int(manifestList.pop(0))
                if clientManifestVersion == serverManifestVersion:
                    while manifestList:
                        if manifestList[0] in manifestServerList:
                            index = manifestServerList.index(manifestList[0])
                            serverHash = manifestServerList[index + 2]

                            blockSize = 65536
                            hasher = hashlib.sha1()
                            with open(manifestList[0], 'rb') as afile:
                                buf = afile.read(blockSize)
                                while len(buf) > 0:
                                    hasher.update(buf)
                                    buf = afile.read(blockSize)
                            liveHash = hasher.hexdigest()

                            if liveHash == serverHash:
                                # print("[C]: Up To Date.")
                                manifestList.pop(0)
                                manifestList.pop(0)
                                manifestList.pop(0)
                            else:
                                # print("[C]: U : " + str(manifestList[0]))
                                updateList.append(str("U"))
                                updateList.append(str(manifestList[0]))
                                manifestList.pop(0)
                                manifestList.pop(0)
                                manifestList.pop(0)
                        else:
                            # print("[C]: U : " + str(manifestList[0]))
                            updateList.append(str("U"))
                            updateList.append(str(manifestList[0]))
                            manifestList.pop(0)
                            manifestList.pop(0)
                            manifestList.pop(0)
                else:
                    while manifestList:
                        if manifestList[0] in manifestServerList:
                            index = manifestServerList.index(manifestList[0])
                            clientFileVersion = int(manifestList[1])
                            serverFileVersion = int(manifestServerList[index + 1])
                            if clientFileVersion == serverFileVersion:
                                blockSize = 65536
                                hasher = hashlib.sha1()
                                with open(manifestList[0], 'rb') as afile:
                                    buf = afile.read(blockSize)
                                    while len(buf) > 0:
                                        hasher.update(buf)
                                        buf = afile.read(blockSize)
                                liveHash = hasher.hexdigest()
                                if liveHash == manifestList[2]:
                                    # print("Up To Date.")
                                    manifestList.pop(0)
                                    manifestList.pop(0)
                                    manifestList.pop(0)
                                    manifestServerList.pop(index)
                                    manifestServerList.pop(index)
                                    manifestServerList.pop(index)
                                else:
                                    print("[C]: CONFLICT : " + manifestList[0])
                                    print("[C]: The file(s) above show some conflict. Please resolve this first and then Update again.\n")
                                    f.close()
                                    s.close()
                                    os.remove(UpdatePath)
                                    os.remove(serverManifestPath)
                                    return
                            else:
                                blockSize = 65536
                                hasher = hashlib.sha1()
                                with open(manifestList[0], 'rb') as afile:
                                    buf = afile.read(blockSize)
                                    while len(buf) > 0:
                                        hasher.update(buf)
                                        buf = afile.read(blockSize)
                                liveHash = hasher.hexdigest()

                                if liveHash == manifestList[2]:
                                    # print("[C]: M : " + str(manifestList[0]))
                                    updateList.append(str("M"))
                                    updateList.append(str(manifestList[0]))
                                    manifestList.pop(0)
                                    manifestList.pop(0)
                                    manifestList.pop(0)
                                    manifestServerList.pop(index)
                                    manifestServerList.pop(index)
                                    manifestServerList.pop(index)
                                else:
                                    print("[C]: CONFLICT : " + manifestList[0])
                                    print("[C]: The file(s) above show some conflict. Please resolve this first and then Update again.\n")
                                    f.close()
                                    s.close()
                                    os.remove(UpdatePath)
                                    os.remove(serverManifestPath)
                                    return
                        else:
                            # print("[C]: D : " + str(manifestList[0]))
                            updateList.append(str("D"))
                            updateList.append(str(manifestList[0]))
                            manifestList.pop(0)
                            manifestList.pop(0)
                            manifestList.pop(0)
                    while manifestServerList:
                        # print("[C]: A : " + str(manifestServerList[0]))
                        updateList.append(str("A"))
                        updateList.append(str(manifestServerList[0]))
                        manifestServerList.pop(0)
                        manifestServerList.pop(0)
                        manifestServerList.pop(0)
                if not updateList:
                    print("[C]: Up To Date.\n")
                    f.close()
                    os.remove(serverManifestPath)
                else:
                    while updateList:
                        print("[C]: " + str(updateList[0]) + " , " + str(updateList[1]))
                        f.write(str(updateList[0]) + " , " + str(updateList[1]) + "\n")
                        updateList.pop(0)
                        updateList.pop(0)
                    print("")
                    f.close()
                    os.remove(serverManifestPath)
            except:
                print("[C]: ERROR opening the Update.txt file. Please try again.\n")
                os.remove(serverManifestPath)
                s.close()
                return
        except IOError:
            print("[S]: ERROR: There was an issue creating the Manifest_Server.txt file. Please try again.\n")
            s.send("ERROR".encode('utf-8'))
            s.close()
            return
    else:
        print("[C]: The project directory was not found on the server side. Please try again.\n")
        s.close()
        return

    # close the socket
    s.close()
    return


def upgrade():
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
        print("[C]: Connected to the server.\n")
    except:
        print("[C]: There was a problem connecting to the server. Please try again.")
        s.close()
        return

    # let the server know which command the client wants to use
    s.send("upgrade".encode('utf-8'))

    # reply from the server that tells the client that it is ready to go
    data_from_server = s.recv(1024)

    if data_from_server != "upgrade":
        print("[C]: ERROR: An issue occurred when using the 'upgrade' command. Please try again.")
        s.close()
        return

    # send the server the project name
    s.send(sys.argv[2].encode('utf-8'))

    # get response from the server
    data_from_server = s.recv(1024)

    if data_from_server == "FOUND":
        parentPath = os.path.dirname(os.path.abspath(__file__))
        updatePath = os.path.join(parentPath, str(sys.argv[2]), "Update.txt")

        if not os.path.exists(updatePath):
            print("[C]: Please do an update before trying to do an upgrade.\n")
            return

        print("found")
        s.close()
        return
    else:
        print("[C]: The server repository did not contain the project: " + str(sys.argv[2]) + "\n")
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
        upgrade()
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


'''

    dirPath = list()
    mainFile = "o"
    for x in updatePath.split("/"):
        dirPath.append(x)
    for x in dirPath:
        if "." in x:
            mainFile = x
            dirPath.pop(dirPath.index(x))
            break
    path = ""
    while dirPath:
        path = path + str(dirPath.pop(0)) + "/"
    print(path)
    open(path+"random.txt", "w")
    print(mainFile)
'''