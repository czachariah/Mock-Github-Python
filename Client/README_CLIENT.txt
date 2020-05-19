This is the README for the client program.
Author: Chris Zachariah

Running the client:
python client.py <command> <args>

Commands:
1) python client.py configure <IP/Hostname> <port#>

    This command must be used before running any other commands that connect to the server.
    The program will take the IP/Hostname and the port number of the server and store the
    info inside a config.txt file. This file will then be used by other commands to get the
    info to connect to the server.

    THIS COMMAND DOES NOT ATTEMPT TO CONNECT TO THE SERVER. It will simply store the info provided.
    If there are problems connecting to the server, either run the other commands again, or re-configure
    the the file by updating the info.

2) python client.py create <projectName>

    This command will connect to the server (using the config.txt file info ) to create a new project directory with an
    empty Manifest.txt file inside. If that process is successful, the same will be done on the client side. If both
    sides are successful then both the client and server will have a new project folder with an empty Manifest.txt inside.

    If one or both sides fail to create this new project, then the whole process is terminated and any work that
    has been completed on both sides is undone.

3) python client.py add <projectName> <fileName/filePath>

    The file must be made and added inside the project directory before calling this method. Once this method is called, it will
    check to make sure that the file exists and can be found within the project directory (given the file name or file
    path). A hash of the contents of the file will be taken using SHA1.

    If all the steps above are successful, then the Manifest.txt file will be updated within the project. A new entry
    (filePath , versionNumber , hash , hasServerSeen) will be added. The version number will be 1 if this is the file time
    the file is going to be entered. The hasServerSeen is a boolean (Y or N) that tells the server there have been changes
    that it needs to record (will be used in other commands).

    If the file being added is an update. Then the client will redo the hash and update the version number inside the
    Manifest.txt file. It will also set the hasServerSeen to 'N'.

4) python client.py remove <projectName> <fileName/filePath>

    The file must be removed from the project directory before calling this method. Once this method is called, it will
    check to make sure that the file has been removed and then update the Manifest by removing the entry for the given file.