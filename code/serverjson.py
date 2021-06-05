import os
import json

def make_serv_json():
    cwd_path = os.getcwd()
    json_name = "server_data.json"
   
    file_path = os.path.join(cwd_path, json_name)
    empty_dict = { "user_dict" : {}, "group_dict" : {} }    
    
    with open(file_path, "w") as outfile: 
        json.dump(empty_dict, outfile, indent=4) 

def get_serv_json():
    cwd_path = os.getcwd()
    json_name = "server_data.json"
   
    file_path = os.path.join(cwd_path, json_name)
    with open(file_path, "r") as infile: 
        serv_dict = json.load(infile)

    return serv_dict["user_dict"], serv_dict["group_dict"] 

def save_serv_json(user_dict, group_dict):
    
    serv_dict = {}
    serv_dict["user_dict"] = user_dict 
    serv_dict["group_dict"] = group_dict

    cwd_path = os.getcwd()
    json_name = "server_data.json"
   
    file_path = os.path.join(cwd_path, json_name)        
    with open(file_path, "w") as outfile: 
        json.dump(serv_dict, outfile, indent=4) 
