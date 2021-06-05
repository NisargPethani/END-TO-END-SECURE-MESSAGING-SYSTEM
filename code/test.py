import socket
import sys

def server_client():

    load_balancer_ip = '127.0.0.1'
    load_balancer_port = 8080

    server_ip = '127.0.0.1'
    server_port = 8000

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


if __name__ == '__main__':
    server_client()