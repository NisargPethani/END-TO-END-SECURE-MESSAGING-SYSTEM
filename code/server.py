import socket
import json
import threading
import ast
import sys
from des import DesKey

import keyexchange
import msgpassing
import clearrecord
import serverjson
import uuidjson

_password = 0
_ip = 1
_port = 2

# 
def join_fun(recv_msg_list, sock, des_key):
    user_dict, group_dict = serverjson.get_serv_json()

    if len(recv_msg_list) != 5:
        msgpassing.send_encripted_error_msg(sock, des_key, "Invalid command format")

    elif not(recv_msg_list[1] in group_dict.keys()):
        msgpassing.send_encripted_error_msg(sock, des_key, "Group does not exist")
    else:
        group_name = recv_msg_list[1]

        group_members = [group_dict[group_name][0]]
        group_members.extend(group_dict[group_name][1])

        group_dict[group_name][1].append([recv_msg_list[4],recv_msg_list[2],recv_msg_list[3]])

        msgpassing.send_encripted_msg(sock, des_key, group_members, msg_type=1)

    serverjson.save_serv_json(user_dict, group_dict)

# 
def list_fun(recv_msg_list, sock, des_key):
    _, group_dict = serverjson.get_serv_json()

    if len(recv_msg_list) != 1:
        msgpassing.send_encripted_error_msg(sock,des_key, "Invalid format command of list")
    else:

        all_group_info = []
        for key in group_dict.keys():
            member_count = 1 + len(group_dict[key][1])

            all_group_info.append([key,member_count])
        
        msgpassing.send_encripted_msg(sock, des_key, all_group_info)

# 
def create_fun(recv_msg_list, sock, des_key):
    user_dict, group_dict = serverjson.get_serv_json()

    if(len(recv_msg_list) != 5):
        msgpassing.send_encripted_error_msg(sock,des_key, "Invalid command format")

    elif (recv_msg_list[1] in group_dict.keys()):
        msgpassing.send_encripted_error_msg(sock,des_key, "Group already exists")
    else:
        group_name = recv_msg_list[1]
        group_info = [[recv_msg_list[4],recv_msg_list[2],recv_msg_list[3]], []]

        group_dict[group_name] = group_info
        msgpassing.send_encripted_succ_msg(sock, des_key)

    serverjson.save_serv_json(user_dict, group_dict)    

# 
def send_fun(recv_msg_list, sock, des_key):
    user_dict, group_dict = serverjson.get_serv_json()

    if len(recv_msg_list) != 2:
        msgpassing.send_encripted_error_msg(sock, des_key, "Invalid Command Format")

    elif not(recv_msg_list[1] in user_dict.keys()):
        msgpassing.send_encripted_error_msg(sock, des_key, "The user you want to send the message to does not exist")
    else:
        user_name = recv_msg_list[1]
        user_info = user_dict[user_name][1:]

        msg = [user_name,user_info]
        msgpassing.send_encripted_msg(sock, des_key, str(msg), msg_type=5)
    
    serverjson.save_serv_json(user_dict, group_dict)

# 
def signup_fun(recv_msg_list, sock, des_key):
    user_dict, group_dict = serverjson.get_serv_json()

    if len(recv_msg_list) != 5:
        msgpassing.send_encripted_error_msg(sock,des_key, "Invalid command format")

    elif (recv_msg_list[1] in user_dict.keys()):
        msgpassing.send_encripted_error_msg(sock,des_key, "Username already taken")
    else:
        user_name = recv_msg_list[1]

        user_dict[user_name] = recv_msg_list[2:]
        msgpassing.send_encripted_succ_msg(sock, des_key)
    
    serverjson.save_serv_json(user_dict, group_dict)

# 
def signin_fun(recv_msg_list, sock, des_key):
    user_dict, _ = serverjson.get_serv_json()
    if len(recv_msg_list) != 3:
        msgpassing.send_encripted_error_msg(sock,des_key, "Invalid command format")

    elif not(recv_msg_list[1] in user_dict.keys()):
        msgpassing.send_encripted_error_msg(sock,des_key, "No such username exists. Sign up first")
    else:
        user_name = recv_msg_list[1]
        password = recv_msg_list[2]

        if user_dict[user_name][_password] == password:
            msgpassing.send_encripted_succ_msg(sock, des_key)
        else:
            msgpassing.send_encripted_error_msg(sock,des_key,"Wrong credentials")

def exchange_and_store_key(client_sock, recv_msg):

    uuid, shared_key = keyexchange.serv_exchange_key_as_serv(client_sock, recv_msg)
    uuidjson.add_new_uuid(uuid, shared_key)

# 
def serve_req(client_sock, addr):

    recv_msg = msgpassing.recv_msg(client_sock)
    recv_msg = ast.literal_eval(recv_msg)

    if recv_msg[0] == -5:
        exchange_and_store_key(client_sock, recv_msg)
    else:
        uuid = recv_msg[0]
        shared_key = uuidjson.get_key(uuid)

        des_key = DesKey(shared_key.encode())        
            
        flag, plain_text = msgpassing.get_decripted_msg(des_key, recv_msg)
        print(addr, " : ", flag, plain_text)

        if flag == False:
            client_sock.close()
            return
        
        plain_text = plain_text[1]
        plain_text_list = ast.literal_eval(plain_text)
        
        if len(plain_text_list) == 0:
            msgpassing.send_encripted_error_msg(client_sock,des_key)
            return

        if plain_text_list[0].upper() == "SIGNUP":
            signup_fun(plain_text_list, client_sock, des_key)            
        elif plain_text_list[0].upper() == "SIGNIN":
            signin_fun(plain_text_list, client_sock, des_key)    
        elif plain_text_list[0].upper() == "SEND":
            send_fun(plain_text_list, client_sock, des_key)    
        elif plain_text_list[0].upper() == "CREATE":
            create_fun(plain_text_list, client_sock, des_key)    
        elif plain_text_list[0].upper() == "LIST":
            list_fun(plain_text_list, client_sock, des_key)    
        elif plain_text_list[0].upper() == "JOIN":
            join_fun(plain_text_list, client_sock, des_key)    
        else:
            user_dict, group_dict = serverjson.get_serv_json()
            msgpassing.send_encripted_msg(client_sock, des_key, [user_dict, group_dict])

# 
def startServer(serv_ip, serv_port):

    s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("socket created")

    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    s.bind((serv_ip,serv_port))
    print("Bind info : "+str(serv_ip)+":"+str(serv_port))

    s.listen(10)
    print("Listen success\n\n")

    thread_count = 0
    while True:

        thread_count+=1
        # print("New Thread created, Thread-count:"+str(thread_count))

        client_sock, addr = s.accept()

        try:
            threading.Thread(target=serve_req, args=(client_sock, addr,)).start()
        except Exception:
            print("Exception in thread : "+addr)

def server_client(server_ip, server_port):

    with open("server_info.json") as j:
        server_info = json.load(j)
    
    load_balancer_ip = server_info["ip"]
    load_balancer_port = server_info["port"]

    try:
        sockt = socket.socket(socket.AF_INET, socket.SOCK_STREAM )
    
    except socket.error as error:
        print("Socket creation failed with error :", error)
        sys.exit(0)
        
    try:
        sockt.connect((load_balancer_ip, load_balancer_port))
        heartBeatMessage = [-10, (server_ip, server_port)]
        sockt.sendall(str(heartBeatMessage).encode())

    except socket.error as error:
        print("Socket connection failed with error :", error)
    finally:
        sockt.close()     


def main():

    try:
        serv_ip, serv_port = sys.argv[1].split(":")    
    except Exception:
        print("ip:port Missing")
        exit()

    serverjson.make_serv_json()
    uuidjson.make_uuid_json()

    server_client(serv_ip, int(serv_port))
    startServer(serv_ip, int(serv_port))    

    
if __name__ == "__main__":
    main()