import shutil
import os

def clear():
    cwd = os.getcwd()

    dir_path = os.path.join(cwd, "log")
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)    


    dir_path = os.path.join(cwd, "user_info_json")
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)    



    dir_path = os.path.join(cwd, "__pycache__")
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)    

if __name__ == "__main__":
    clear()