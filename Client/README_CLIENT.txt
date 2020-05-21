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

5) python client.py update <projectName>

    The client will first ask the server to send over the contents of the Manifest.txt of the project that is in the
    repository. If the server does not have the project in its repository, then an error is thrown. If the server finds
    the project directory, then the contents of the Manifest.txt is forwarded to the client. The client will then use
    the contents in the server's Manifest to check it against the client's Manifest.

    If the Manifest versions are the same, there are 2 possibilities for an UPLOAD.
    1) There is a file in the client Manifest that is not found on the server Manifest. This means that the client has
    a new file to upload to the server
    2) There is file found in both the Manifests, but the server's hash and the client's live hash are different. This
    means that the client needs to Upload this new version of the file to the server. The program will print out in the
    standard output for files that need to be uploaded. This is not recorded in the Update.txt file that is created.

    If the Manifest versions are not the same, there are different possibilities for files that are MODIFIED, ADDED or
    need to be DELETED.
    1) There is file found on both the client and server manifests, but the file versions are different and the
    live hash of the file is the same as it is in its (client's) Manifest. This means that the file was modified in the
    server and the client will need to update its copy later. This will be noted in the Update.txt file.
    2) There is file found on both the client and server manifests, but the file versions are different and the
    live hash of the file is NOT THE same as it is in its (client's) Manifest. This means that there is a conflict that
    needs to be addressed by the user manually before doing the update.
    3) There is file found on both the client and server manifests, but the file versions are the same and the
    live hash of the file is NOT THE same as it is in its (client's) Manifest. This means that there is a conflict that
    needs to be addressed by the user manually before doing the update.
    4) There is a file that is only found in the server's Manifest. This means that another client added this new file
    to the server and the client needs to download it later. This will be noted in the Updated.txt file.
    5) There is a file that is only found in the client's Manifest. This means that the file is no longer needed and will
    be noted as a file to delete in the Update.txt file.

    A conflict occurs when the Manifest versions are different, the file versions are different and the client's live
    hash and the hash saved in its Manifest are also different. Thus, a conflict is when someone pushed an update to
    the server which incrementing the file’s version and server’s manifest version and modified the hash. This also means
    that the client has not seen it and the user (present client) made a change locally so live hash does not match the
    manifest hash in its own Manifest.

    Most likely, the remedy for a conflict is to make sure that all the files are added (using the add() command)
    to the Manifest correctly especially after any updates to the file.

    In all other cases, the client's project Manifest is up-to-date and no changes need to be done. In this instance, a
    blank Updated.txt file is made.

    Note that the client does not generate a hash for, or record any information for, files in the project directory that
    are not in the Manifest.txt file. It is only concerned with files listed in the Manifest.txt file.

6) python upgrade <projectName>

    The client will use the Update.txt file in the project directory to make necessary updates to sync with the server.
    Any files tagged 'D' will be deleted. Any files tagged 'M' will be fetched from the server. Any files tagged 'A' will
    be written into the server side project directory and Manifest.

    By the end of this commands both the Manifests should be the same versions.

