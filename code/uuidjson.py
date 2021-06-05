import os
import json

def make_uuid_json():
    cwd_path = os.getcwd()
    json_name = "uuid_info.json"
   
    file_path = os.path.join(cwd_path, json_name)
    empty_dict = {}    
    
    with open(file_path, "w") as outfile: 
        json.dump(empty_dict, outfile, indent=4) 

def get_uuid_json():
    cwd_path = os.getcwd()
    json_name = "uuid_info.json"
   
    file_path = os.path.join(cwd_path, json_name)
    with open(file_path, "r") as infile: 
        uuid_dict = json.load(infile)

    return uuid_dict 

def save_uuid_json(uuid_dict):

    cwd_path = os.getcwd()
    json_name = "uuid_info.json"
   
    file_path = os.path.join(cwd_path, json_name)        
    with open(file_path, "w") as outfile: 
        json.dump(uuid_dict, outfile, indent=4) 

def add_new_uuid(uuid, shared_key):

    uuid_dict = get_uuid_json()
    uuid_dict[uuid] = shared_key

    save_uuid_json(uuid_dict)

def get_key(uuid):

    uuid_dict = get_uuid_json()
    return uuid_dict[uuid]