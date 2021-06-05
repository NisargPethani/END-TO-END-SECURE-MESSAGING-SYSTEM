import socket
import json
import pyDH
import threading
import sys
import ast
from des import DesKey
from uuid import uuid4

import msgpassing
import keyexchange
import userjson
import peerserver

peer_info = {
    "users" : [],
    "current_user" : ''
}

# 
def validate(command):
    #Check if the user is a part of the group or not
    # We need to see if the user has info of that group



    return True

def get_file_content(command):
    file_path = command[3]

    file_name = file_path.split("/")[-1]
    command[3] = file_name

    file = open(file_path, "rb")
    content = file.read()
    file.close()

    return content

def send_to_user(command, recv_user_info, msg_type=0, user_name=None):

    if user_name is None:
        user_name = peer_info["current_user"]

    if command[0].upper() == "JOIN":
        msg_type = -6

    des_key = DesKey(recv_user_info[2].encode())
    encripted_file = b''

    if msg_type == 0 or msg_type == 1:
        if command[2].upper() != "MSG":
            command.append("")
            file_content = get_file_content(command)
            encripted_file = msgpassing.peer_get_encript_filr_msg(des_key, file_content)

    peer_serv_sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    peer_serv_sock.connect((recv_user_info[0],recv_user_info[1]))

    msgpassing.peer_send_encript_msg(peer_serv_sock, user_name, des_key, command, msg_type )
    
    # encripted_msg = msgpassing.peer_get_group_encript_msg(group_id, des_key, command, msg_type=1)
    # peer_serv_sock.sendall(encripted_msg)

    if msg_type == 0 or msg_type == 1:
        if command[2].upper() != "MSG":
            peer_serv_sock.recv(1024).decode()
            peer_serv_sock.sendall(encripted_file)

    return True, []

def set_peer_info(ip, port, des_key, command, uuid):
    # Plzz dont mind

    with open("server_info.json") as j:
        server_info = json.load(j)
    
    serv_ip = server_info["ip"]
    serv_port = server_info["port"]

    serv_sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serv_sock.connect((serv_ip,serv_port))

    # foolowing code is to get username=command[1] info and save to file

    join_flag = False
    if command[0].upper() == "JOIN":
        command[0] = "SEND"
        join_flag = True

    msgpassing.send_uuid_encripted_msg(serv_sock, des_key, str(command[:2]), uuid)
    flag, plain_text = msgpassing.recv_decripted_msg(serv_sock, des_key)

    if join_flag == True:
        command[0] = "JOIN"

    if flag == False:
        return False, []
    
    # 5 ensure correct msg
    if plain_text[0] == 5:

        recv_user_info = ast.literal_eval(plain_text[1])
        
        recv_user_name = recv_user_info[0]
        recv_ip = recv_user_info[1][0]
        recv_port = recv_user_info[1][1]

        peer_serv_sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        peer_serv_sock.connect((recv_ip,recv_port))
        
        msg = [ip, port]
        msgpassing.peer_send_msg(peer_serv_sock, peer_info["current_user"], msg, msg_type=-5)

        shared_key = keyexchange.exchange_key_as_client(peer_serv_sock)
        peer_serv_sock.close()

        userjson.add_new_user_info(ip, port, [recv_user_name, recv_ip, recv_port, shared_key])
        
        user_dict = userjson.get_user_json(ip, port)
        return send_to_user(command, user_dict["user_info"][command[1]])

    return flag, []

# 
def send_to_group_parallel(recv_ip, recv_port, encripted_msg, command, encripted_file):

    peer_serv_sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    peer_serv_sock.connect((recv_ip,recv_port))

    peer_serv_sock.sendall(encripted_msg)

    if command[2].upper() != "MSG":
        peer_serv_sock.recv(1024).decode()
        peer_serv_sock.sendall(encripted_file)

    peer_serv_sock.close()

# 
def send_to_group(command, group_info):
    command.append(peer_info["current_user"])

    group_id = command[1]
    group_key = group_info[0]
    group_creator = group_info[1]
    group_members = group_info[2]

    recv_ip = group_creator[1]
    recv_port = group_creator[2]
    
    des_key = DesKey(group_key.encode())
    encripted_file = b''

    if command[2].upper() != "MSG":
        command.append("")
        file_content = get_file_content(command)
        encripted_file = msgpassing.peer_get_encript_filr_msg(des_key, file_content)
        
    encripted_msg = msgpassing.peer_get_group_encript_msg(group_id, des_key, command, msg_type=1)

    if peer_info["current_user"] != group_creator[0]:
        threading.Thread(target=send_to_group_parallel, args=(recv_ip, recv_port, encripted_msg, command, encripted_file, )).start()

    for user in group_members:
        if peer_info["current_user"] != user[0]:

            recv_ip = user[1]
            recv_port = user[2]
            
            threading.Thread(target=send_to_group_parallel, args=(recv_ip, recv_port, encripted_msg, command, encripted_file, )).start()
    
    return True, []

# 
def send_fun(serv_sock, ip, port, des_key, command, uuid):    

    user_dict = userjson.get_user_json(ip, port)

    if not validate(command):
        return False, []

    users_groups = command[1].split(",")

    for id in users_groups:
        command[1] = id
    
        if command[1] in user_dict["user_info"].keys():
            send_to_user(command, user_dict["user_info"][command[1]])
        elif command[1] in user_dict["group_info"].keys():
            send_to_group(command, user_dict["group_info"][command[1]])
        else:
            set_peer_info(ip, port, des_key, command, uuid)

    return True, []

# 
def start_peer_server(ip, port, user_name):
    peerserver.start_peer_server(ip, port, user_name)

def signin_fun(serv_sock, ip, port, des_key, command, uuid):
    
    msgpassing.send_uuid_encripted_msg(serv_sock, des_key, str(command), uuid)            
    flag, plain_text= msgpassing.recv_decripted_msg(serv_sock, des_key)

    if flag == False:
        return flag, []

    if plain_text[0] == 1:
        peer_info["current_user"] = command[1]
        threading.Thread(target=start_peer_server, args=(ip,int(port), command[1], )).start()
   
    return flag, plain_text

# 
def signup_fun(serv_sock, ip, port, des_key, command, uuid):
    command.append(ip)
    command.append(port)

    msgpassing.send_uuid_encripted_msg(serv_sock, des_key, str(command), uuid)            
    flag, plain_text= msgpassing.recv_decripted_msg(serv_sock, des_key)

    if flag == False:
        return flag, []

    if plain_text[0] == 1:
        peer_info["users"].append(command[1])

    return flag, plain_text

# 
def create_group(serv_sock, ip, port, des_key, command, uuid):
    command.append(ip)
    command.append(port)
    command.append(peer_info["current_user"])

    msgpassing.send_uuid_encripted_msg(serv_sock, des_key, str(command), uuid)            
    flag, plain_text= msgpassing.recv_decripted_msg(serv_sock, des_key)

    if flag == False:
        return flag, []

    if plain_text[0] == 1:
        # gen random key

        group_id = command[1]

        lowercase_str = uuid4().hex  
        shared_key = lowercase_str[:24]
        
        new_group_info = [shared_key, [command[-1], ip, port], []]

        userjson.add_new_group_info(ip, port, group_id, new_group_info)

    return flag, plain_text

# 
def get_group_key(ip, port, group_id , group_creator_info):

    user_dict = userjson.get_user_json(ip, port)        

    des_key = DesKey(user_dict["user_info"][group_creator_info[0]][2].encode())

    peer_serv_sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    peer_serv_sock.connect((group_creator_info[1],group_creator_info[2]))

    msgpassing.peer_send_encript_msg(peer_serv_sock, peer_info["current_user"], des_key, msg=group_id, msg_type = -7 )
    
    recv_msg = msgpassing.peer_recv_msg(peer_serv_sock)
    recv_msg = ast.literal_eval(recv_msg)

    recv_msg_list = recv_msg[1]
    recv_original_msg = recv_msg_list[1]
   
    plain_text = des_key.decrypt(recv_original_msg, padding=True).decode()
    return plain_text

def join_group(serv_sock, ip, port, des_key, command, uuid):
    command.append(ip)
    command.append(port)
    command.append(peer_info["current_user"])

    msgpassing.send_uuid_encripted_msg(serv_sock, des_key, str(command), uuid)            
    flag, plain_text = msgpassing.recv_decripted_msg(serv_sock, des_key)

    if flag == False:
        return flag, []

    # [join, un, gid, ip, port, own_un]

    if plain_text[0] == 1:
        command.insert(1, "dummy")
        for user in plain_text[1]:
            command[1]=user[0]
            send_fun(serv_sock, ip, port, des_key, command, uuid)

        group_id = command[2]
        group_creator_info = plain_text[1][0]

        group_key = get_group_key(ip, port, group_id , group_creator_info)
        group_members = [[peer_info["current_user"], ip, port]]
        group_creator_info = plain_text[1][0]

        plain_text = plain_text[1][1:]
        
        if len(plain_text) > 0:
            for i in list(plain_text):
                group_members.append(i)

        new_group_info = [group_key, group_creator_info , group_members]
        userjson.add_new_group_info(ip, port, group_id, new_group_info)

    return flag, []

# 
def list_group(serv_sock, ip, port, des_key, command, uuid):
    msgpassing.send_uuid_encripted_msg(serv_sock, des_key, str(command), uuid)            
    flag, plain_text= msgpassing.recv_decripted_msg(serv_sock, des_key)

    if flag == False:
        return flag, []       

    return flag, plain_text

# 
def talk_to_server(ip, port, serv_ip, serv_port):

    serv_sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serv_sock.connect((serv_ip,serv_port))
    
    uuid, shared_key = keyexchange.serv_exchange_key_as_client(serv_sock)
    serv_sock.close()

    des_key = DesKey(shared_key.encode())

    while True:
        command = input(":").split()

        serv_sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serv_sock.connect((serv_ip,serv_port))

        if len(command) > 0:
            if command[0].upper() == "SIGNUP":
                flag, plain_text = signup_fun(serv_sock, ip, port, des_key, command, uuid)
            elif command[0].upper() == "SIGNIN":
                flag, plain_text = signin_fun(serv_sock, ip, port, des_key, command, uuid)
            elif command[0].upper() == "SEND":
                new_command = ' '.join(i for i in command)
                command = new_command.split(" ",3)
                print(command)

                flag, plain_text = send_fun(serv_sock, ip, port, des_key, command, uuid)
            elif command[0].upper() == "CREATE":
                flag, plain_text = create_group(serv_sock, ip, port, des_key, command, uuid)
            elif command[0].upper() == "LIST":
                flag, plain_text = list_group(serv_sock, ip, port, des_key, command, uuid)
            elif command[0].upper() == "JOIN":
                flag, plain_text = join_group(serv_sock, ip, port, des_key, command, uuid)
            else:
                msgpassing.send_encripted_msg(serv_sock, des_key, uuid, str(command))            
                flag, plain_text= msgpassing.recv_decripted_msg(serv_sock, des_key)

        print("serv_reply : " ,flag, plain_text)
        if flag == False:
            break
        
def start_peer_client(ip, port):
    with open("server_info.json") as j:
        server_info = json.load(j)
    
    serv_ip = server_info["ip"]
    serv_port = server_info["port"]

    talk_to_server(ip, port, serv_ip, serv_port)