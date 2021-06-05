import socket
import json
import pyDH
import threading
import sys
import ast
import os
from des import DesKey

import keyexchange
import msgpassing
import peerservlog
import userjson

peer_info = {
    "ip" : '',
    "port" : -5,
    "current_user" : ''
}

# 
def peer_key_exchange(client_sock, addr, my_addr, recv_msg):

    recv_username = recv_msg[0]
    recv_msg_list = recv_msg[1]

    recv_original_msg = recv_msg_list[1]

    ip = peer_info["ip"]
    port = peer_info["port"]

    shared_key = keyexchange.exchange_key_as_serv(client_sock)
    peerservlog.log_print(my_addr, msg=[addr , shared_key])

    userjson.add_new_user_info(ip, port, [recv_username, recv_original_msg[0], recv_original_msg[1], shared_key])

# 
def peer_add_new_group_member(client_sock, addr, my_addr, recv_msg):

    recv_username = recv_msg[0]
    recv_msg_list = recv_msg[1]

    recv_original_msg = recv_msg_list[1]

    ip = peer_info["ip"]
    port = peer_info["port"]

    user_dict = userjson.get_user_json(ip, port)
    recv_user_info = user_dict["user_info"][recv_username]

    des_key = DesKey(recv_user_info[2].encode())

    plain_text = des_key.decrypt(recv_original_msg, padding=True).decode()
    plain_text = ast.literal_eval(plain_text)

    new_user_info = [plain_text[-1],plain_text[-3],plain_text[-2]]
    userjson.add_new_group_member(ip, port, plain_text[2], new_user_info)

# 
def peer_group_key_exchange(client_sock, addr, my_addr, recv_msg):

    recv_username = recv_msg[0]
    recv_msg_list = recv_msg[1]

    recv_original_msg = recv_msg_list[1]

    ip = peer_info["ip"]
    port = peer_info["port"]

    user_dict = userjson.get_user_json(ip, port)
    recv_user_info = user_dict["user_info"][recv_username]

    des_key = DesKey(recv_user_info[2].encode())
    plain_text = des_key.decrypt(recv_original_msg, padding=True).decode()

    group_key = user_dict["group_info"][plain_text][0]
    msgpassing.peer_send_encript_msg(client_sock, peer_info["current_user"], des_key, msg=group_key, msg_type = 1 )

# 
def save_recved_file(file_name, file_content):

    cwd_path = os.getcwd()
    dir_path = os.path.join(cwd_path, "user_info_json")

    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
    
    ip = peer_info["ip"]
    port = peer_info["port"]

    user_dir = str(ip) + ":" + str(port)
    user_dir_path = os.path.join(dir_path, user_dir)

    file_path = os.path.join(user_dir_path, file_name)

    file = open(file_path, "wb")
    file.write(file_content)
    file.close()

def save_peer_msg(sndr_info, data, client_sock, des_key):
    data_type = data[0]
    data_content_info = data[1]

    if data_type.upper() == "MSG":
        print(sndr_info, " : ", data_content_info)
    else:

        dummy = "dummy"
        client_sock.sendall(dummy.encode())

        file_name = data_content_info
        encripted_file_content = msgpassing.recv_no_decoded_msg(client_sock)

        file_content = des_key.decrypt(encripted_file_content, padding=True)

        save_recved_file(file_name, file_content)
        print(sndr_info, " : ", file_name)

# 
def peer_recv_peer_msg(client_sock, addr, my_addr, recv_msg):

    sndr_username = recv_msg[0]
    recv_msg_list = recv_msg[1]

    recv_original_msg = recv_msg_list[1]

    ip = peer_info["ip"]
    port = peer_info["port"]

    user_dict = userjson.get_user_json(ip, port)
    recv_user_info = user_dict["user_info"][sndr_username]

    des_key = DesKey(recv_user_info[2].encode())

    plain_text = des_key.decrypt(recv_original_msg, padding=True).decode()
    peerservlog.log_print(my_addr, msg=[sndr_username,plain_text])
    
    plain_text = ast.literal_eval(plain_text)
    peerservlog.log_print(my_addr, msg=[sndr_username, " : " , plain_text[2:]])

    save_peer_msg(sndr_username, plain_text[2:], client_sock, des_key)

# 
def peer_recv_group_msg(client_sock, addr, my_addr, recv_msg):

    sndr_group_id = recv_msg[0]
    recv_msg_list = recv_msg[1]

    recv_original_msg = recv_msg_list[1]

    ip = peer_info["ip"]
    port = peer_info["port"]

    user_dict = userjson.get_user_json(ip, port)
    recv_user_info = user_dict["group_info"][sndr_group_id]

    des_key = DesKey(recv_user_info[0].encode())

    plain_text = des_key.decrypt(recv_original_msg, padding=True).decode()
    peerservlog.log_print(my_addr, msg=[sndr_group_id,plain_text])

    plain_text = ast.literal_eval(plain_text)

    sndr_username = plain_text[4]    
    peerservlog.log_print(my_addr, msg=[(sndr_group_id, sndr_username), " : " , plain_text[2:]])

    if len(plain_text) == 5:
        save_peer_msg([sndr_group_id, sndr_username], plain_text[2:-1], client_sock, des_key)

    elif len(plain_text) == 6:
        data = list(plain_text)[2:6]
        del data[-2]

        save_peer_msg([sndr_group_id, sndr_username], data, client_sock, des_key)
# 
def serve_req(client_sock, addr, my_addr):
    peerservlog.log_print(my_addr, msg=[addr , "Coversation started"])

    recv_msg = msgpassing.peer_recv_msg(client_sock)
    peerservlog.log_print(my_addr, msg=[addr , recv_msg])

    recv_msg = ast.literal_eval(recv_msg)
    recv_msg_list = recv_msg[1]
    recv_msg_type = recv_msg_list[0]

    if recv_msg_type == -5:
        peer_key_exchange(client_sock, addr, my_addr, recv_msg)
    
    elif recv_msg_type == -6:
        peer_add_new_group_member(client_sock, addr, my_addr, recv_msg)
        
    elif recv_msg_type == -7:
        peer_group_key_exchange(client_sock, addr, my_addr, recv_msg)

    elif recv_msg_type == 0:
        peer_recv_peer_msg(client_sock, addr, my_addr, recv_msg)
    
    elif recv_msg_type == 1:
        peer_recv_group_msg(client_sock, addr, my_addr, recv_msg)

# 
def start_peer_server(ip, port, user_name):
    s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    peerservlog.log_print((ip,port), msg="socket info")

    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    peer_info["ip"] = peer_serv_ip = ip
    peer_info["port"] = peer_serv_port = port

    s.bind((peer_serv_ip,peer_serv_port))
    peerservlog.log_print((ip,port), msg="Bind info : "+str(peer_serv_ip)+":"+str(peer_serv_port))

    s.listen(10)
    peerservlog.log_print((ip,port), msg="Listen success\n\n")

    peer_info["current_user"] = user_name

    thread_count = 0
    while True:

        thread_count+=1

        client_sock, addr = s.accept()
        threading.Thread(target=serve_req, args=(client_sock, addr, (ip, port))).start()
