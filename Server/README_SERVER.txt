This is the README for the server program.
Author: Chris Zachariah

Running the client:
python server.py <port#>

The server must be run before the client starts using its commands. There are no user commands for the server. It
will wait for connections from multiple clients and lock and unlock the repository when in use. Depending on the command
received, it will act accordingly.

Expected Commands:

1) create

    When a client tells tells the server that it wants to "create", the server will then expect the client to send the
    name of the new project directory. Once the name is received, the server will make a new project directory under
    that assigned name and also an empty Manifest.txt file inside of it. The client will also follow pursuit and do the
    same. If the server or client runs into any trouble getting this done, then both sides will delete the Manifest and
    the project directory and tell the user (of the client) to try again.

