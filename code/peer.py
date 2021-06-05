import socket
import json
import pyDH
import threading
import sys
import os
import json

import peerclient
import peerserver
import keyexchange
import userjson

# 
def start_peer_client(ip,port):
    peerclient.start_peer_client(ip,port)
    print("Work done")

# 
def main():
    try:
        ip, port = sys.argv[1].split(":")
    
    except Exception:
        print("ip:port Missing")
        exit()

    userjson.make_user_json(ip,port)
    threading.Thread(target=start_peer_client, args=(ip,int(port), )).start()
    
if __name__ == "__main__":
    main()