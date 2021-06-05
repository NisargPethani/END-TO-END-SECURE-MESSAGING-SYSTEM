import os
import json

def make_user_json(ip,port):
    cwd_path = os.getcwd()
    dir_path = os.path.join(cwd_path, "user_info_json")

    if not os.path.exists(dir_path):
        os.mkdir(dir_path)

    user_dir = str(ip) + ":" + str(port)
    user_dir_path = os.path.join(dir_path, user_dir)
    os.mkdir(user_dir_path)

    json_name = str(ip) + ":" + str(port) + ".json"
    file_path = os.path.join(dir_path, user_dir_path, json_name)

    empty_dict = { "user_info" : {}, "group_info" : {} }    
    
    with open(file_path, "w") as outfile: 
        json.dump(empty_dict, outfile, indent=4) 


def get_user_json(ip,port):
    cwd_path = os.getcwd()
    dir_path = os.path.join(cwd_path, "user_info_json")

    if not os.path.exists(dir_path):
        os.mkdir(dir_path)

    user_dir = str(ip) + ":" + str(port)
    user_dir_path = os.path.join(dir_path, user_dir)

    json_name = str(ip) + ":" + str(port) + ".json"
    file_path = os.path.join(dir_path, user_dir_path, json_name)

    with open(file_path, "r") as infile: 
        user_dict = json.load(infile)

    return user_dict     

def add_new_user_info(ip, port, new_user_info):
    # [recv_user_name, recv_ip, recv_port, shared_key]

    cwd_path = os.getcwd()
    dir_path = os.path.join(cwd_path, "user_info_json")

    if not os.path.exists(dir_path):
        os.mkdir(dir_path)

    user_dir = str(ip) + ":" + str(port)
    user_dir_path = os.path.join(dir_path, user_dir)

    json_name = str(ip) + ":" + str(port) + ".json"
    file_path = os.path.join(dir_path, user_dir_path, json_name)

    with open(file_path, "r") as infile: 
        user_dict = json.load(infile)

    user_dict["user_info"][new_user_info[0]] = new_user_info[1:]
    
    with open(file_path, "w") as outfile: 
        json.dump(user_dict, outfile, indent=4) 

def add_new_group_info(ip, port, group_id, new_group_info):
    # [recv_user_name, recv_ip, recv_port, shared_key]

    cwd_path = os.getcwd()
    dir_path = os.path.join(cwd_path, "user_info_json")

    if not os.path.exists(dir_path):
        os.mkdir(dir_path)

    user_dir = str(ip) + ":" + str(port)
    user_dir_path = os.path.join(dir_path, user_dir)

    json_name = str(ip) + ":" + str(port) + ".json"
    file_path = os.path.join(dir_path, user_dir_path, json_name)

    with open(file_path, "r") as infile: 
        user_dict = json.load(infile)

    user_dict["group_info"][group_id] = new_group_info
    
    with open(file_path, "w") as outfile: 
        json.dump(user_dict, outfile, indent=4) 


def add_new_group_member(ip, port, group_id, new_user_info):
    # [recv_user_name, recv_ip, recv_port, shared_key]

    cwd_path = os.getcwd()
    dir_path = os.path.join(cwd_path, "user_info_json")

    if not os.path.exists(dir_path):
        os.mkdir(dir_path)

    user_dir = str(ip) + ":" + str(port)
    user_dir_path = os.path.join(dir_path, user_dir)

    json_name = str(ip) + ":" + str(port) + ".json"
    file_path = os.path.join(dir_path, user_dir_path, json_name)

    with open(file_path, "r") as infile: 
        user_dict = json.load(infile)

    user_dict["group_info"][group_id][2].append(new_user_info)

    with open(file_path, "w") as outfile: 
        json.dump(user_dict, outfile, indent=4) 