# This is the client program.
# Author: Chris Zachariah - chriszachariah3@gmail.com

import socket
import sys


def client():
    if len(sys.argv) < 2:
        print("[C]: ERROR: Not enough arguments given. Please try again.")
        exit()
    if sys.argv[1] == "configure":
        print("[C]: configure")
    elif sys.argv[1] == "checkout":
        print("[C]: checkout")
    elif sys.argv[1] == "update":
        print("[C]: update")
    elif sys.argv[1] == "upgrade":
        print("[C]: upgrade")
    elif sys.argv[1] == "commit":
        print("[C]: commit")
    elif sys.argv[1] == "push":
        print("[C]: push")
    elif sys.argv[1] == "create":
        print("[C]: create")
    elif sys.argv[1] == "destroy":
        print("[C]: destroy")
    elif sys.argv[1] == "add":
        print("[C]: add")
    elif sys.argv[1] == "remove":
        print("[C]: remove")
    elif sys.argv[1] == "currentversion":
        print("[C]: currentversion")
    elif sys.argv[1] == "history":
        print("[C]: history")
    elif sys.argv[1] == "rollback":
        print("[C]: rollback")
    else:
        print("[C]: ERROR: Invalid command used. Please try again.")
        exit()

    print("[C]: Closing client program.")
    exit()


if __name__ == '__main__':
    client()
