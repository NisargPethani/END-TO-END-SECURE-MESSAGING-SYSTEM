import ast

def recv_no_decoded_msg(sock):

    recv_text = b''
    while True:
        data = sock.recv(1024)

        recv_text = recv_text + data
        if len(data) < 1024:
            break

    return recv_text


def recv_msg(sock):

    recv_text = ''
    while True:
        data = sock.recv(1024).decode()

        recv_text = recv_text + data
        if len(data) < 1024:
            break

    return recv_text

def get_decripted_msg(des_key, recv_msg):
    
    recv_text = recv_msg[1]
    try:
        plain_text = des_key.decrypt(recv_text, padding=True).decode()
    except Exception:
        return False, []

    plain_text = ast.literal_eval(plain_text)
    return True, plain_text


def recv_decripted_msg(sock, des_key):
    
    recv_text = b''
    while True:
        data = sock.recv(1024)
        recv_text = recv_text + data

        if len(data) < 1024:
            break

    try:
        plain_text = des_key.decrypt(recv_text, padding=True).decode()
    except Exception as e:
        print("Exception : ", e)
        return False, []

    plain_text = ast.literal_eval(plain_text)
    return True, plain_text

def send_uuid_encripted_msg(sock, des_key, msg, uuid, msg_type=0):
    msg_list = [msg_type, msg]
    cifer_text = des_key.encrypt(str(msg_list).encode(), padding=True)
    
    msg = [uuid, cifer_text]
    msg = str(msg)

    sock.sendall(msg.encode())

def send_encripted_msg(sock, des_key, msg, msg_type=0):
    msg_list = [msg_type, msg]
    msg_list = str(msg_list)

    cifer_text = des_key.encrypt(msg_list.encode(), padding=True)
    sock.sendall(cifer_text)

def send_encripted_error_msg(sock, des_key, error_msg = ''):
    msg_type = -1
    msg = "Non Valid command / Command executed un-successfully / "+error_msg

    msg_list = [msg_type, msg]

    cifer_text = des_key.encrypt(str(msg_list).encode(), padding=True)
    sock.sendall(cifer_text)

def send_encripted_succ_msg(sock, des_key):
    msg_type = 1
    msg = "Command executed successfully"

    msg_list = [msg_type, msg]

    cifer_text = des_key.encrypt(str(msg_list).encode(), padding=True)
    sock.sendall(cifer_text)


# 
def peer_recv_msg(sock):

    recv_text = ''
    while True:
        data = sock.recv(1024).decode()

        recv_text = recv_text + data
        if len(data) < 1024:
            break

    return recv_text

def peer_send_msg(sock, own_user_name, msg, msg_type=0):    
    msg_list = [own_user_name, [msg_type, msg]]

    text = str(msg_list).encode()
    sock.sendall(text)


# 
def peer_uuid_send_encript_msg(sock, own_user_name, des_key, msg, uuid, msg_type=0):
    
    cifer_text = des_key.encrypt(str(msg).encode(), padding=True)
    msg_list = [own_user_name, [msg_type, cifer_text]]

    text = str(msg_list)

    msg = [uuid, text]
    msg = str(msg)

    sock.sendall(msg.encode())

def peer_send_encript_msg(sock, own_user_name, des_key, msg, msg_type=0):
    
    cifer_text = des_key.encrypt(str(msg).encode(), padding=True)
    msg_list = [own_user_name, [msg_type, cifer_text]]

    text = str(msg_list)
    sock.sendall(text.encode())

# 
def peer_get_encript_filr_msg(des_key, file_content):
    cifer_text = des_key.encrypt(file_content, padding=True)
    return cifer_text

def peer_get_group_encript_msg(own_user_name, des_key, msg, msg_type=0):
    
    cifer_text = des_key.encrypt(str(msg).encode(), padding=True)
    msg_list = [own_user_name, [msg_type, cifer_text]]

    text = str(msg_list).encode()
    return text

