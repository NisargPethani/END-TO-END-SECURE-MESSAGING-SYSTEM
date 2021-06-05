import os
import json

def log_print(own_addr, msg):
    cwd_path = os.getcwd()
    dir_path = os.path.join(cwd_path, "log")

    if not os.path.exists(dir_path):
        os.mkdir(dir_path)

    log_file_name = str(own_addr)[1:-1] + ".txt"
    file_path = os.path.join(dir_path, log_file_name)
    
    with open(file_path, "a") as myfile:
        myfile.write(str(msg)+"\n")