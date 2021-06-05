import pyDH
import ast
import msgpassing
from uuid import uuid1


def serv_exchange_key_as_client(sock):

    dh = pyDH.DiffieHellman()
    dh_own_pubkey = dh.gen_public_key()

    dh_own_pubkey_str = str(dh_own_pubkey)
    dh_own_pubkey_list = [-5,dh_own_pubkey_str]

    sock.sendall(str(dh_own_pubkey_list).encode())    
    recv_msg = msgpassing.recv_msg(sock)

    recv_msg = ast.literal_eval(recv_msg)
    dh_sender_pubkey_str = recv_msg[0]

    uuid = recv_msg[1]
    dh_sender_pubkey = int(dh_sender_pubkey_str)

    shared_key = dh.gen_shared_key(dh_sender_pubkey)[:24]

    print("uuid : ",uuid)
    print("des_key : ",shared_key , "\n\n")

    return uuid, shared_key

def serv_exchange_key_as_serv(sock, recv_msg):

    dh = pyDH.DiffieHellman()
    dh_own_pubkey = dh.gen_public_key()

    dh_own_pubkey_str = str(dh_own_pubkey)
    
    dh_sender_pubkey_list = recv_msg
    dh_sender_pubkey_str = dh_sender_pubkey_list[1]

    dh_sender_pubkey = int(dh_sender_pubkey_str)
    uuid = str(uuid1())
    
    msg = [dh_own_pubkey_str, uuid]
    msg_str = str(msg)

    sock.sendall(msg_str.encode())    

    shared_key = dh.gen_shared_key(dh_sender_pubkey)[:24]

    print("uuid : ",uuid)
    print("des_key : ",shared_key , "\n\n")

    return uuid, shared_key

def exchange_key_as_client(sock):

    dh = pyDH.DiffieHellman()
    dh_own_pubkey = dh.gen_public_key()

    dh_own_pubkey_str = str(dh_own_pubkey)
    dh_own_pubkey_list = [-5,dh_own_pubkey_str]

    sock.sendall(str(dh_own_pubkey_list).encode())    
    dh_sender_pubkey_str = msgpassing.recv_msg(sock)

    dh_sender_pubkey = int(dh_sender_pubkey_str)
    shared_key = dh.gen_shared_key(dh_sender_pubkey)[:24]

    print("shared_key : ",shared_key)

    return shared_key

def exchange_key_as_serv(sock):

    dh = pyDH.DiffieHellman()
    dh_own_pubkey = dh.gen_public_key()

    dh_own_pubkey_str = str(dh_own_pubkey)
    
    dh_sender_pubkey_list = ast.literal_eval(msgpassing.recv_msg(sock))
    dh_sender_pubkey_str = dh_sender_pubkey_list[1]

    dh_sender_pubkey = int(dh_sender_pubkey_str)

    sock.sendall(dh_own_pubkey_str.encode())    

    shared_key = dh.gen_shared_key(dh_sender_pubkey)[:24]
    print("shared_key : ",shared_key)

    return shared_key