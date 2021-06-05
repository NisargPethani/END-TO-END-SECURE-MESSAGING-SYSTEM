import socket
import threading
import ast
import sys
import json
import time

import clearrecord

class ServerDetails:
    HOST_IP = ""
    PORT_NO = 8000
    LISTEN_QUEUE_SIZE = 100


class Constants:
    BUF_SIZE = 1024

ip_address_servers = []

class LoadBalancer:
    def __init__(self, host_ip="", port_no=8000):
        self.host_ip = host_ip
        self.port_no = port_no
        self.num_servers = 0
        self.server_details = []
        self.lock = threading.Lock()

    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            print("Binding the socket on host ip and port")
            self.sock.bind((self.host_ip, self.port_no))

        except Exception:
            print("Error in binding the socket to ip: {} and port no: {}".format(
                self.host_ip, self.port_no))
            sys.exit(1)

        self._listen_on_ip_port()

    def _listen_on_ip_port(self):
        print("Will listen on ip : {} and port: {}".format(
            self.host_ip, self.port_no))
        self.sock.listen(ServerDetails.LISTEN_QUEUE_SIZE)

        while True:
            connection, addr = self.sock.accept()
            print("\n\nGot connection from ip: {}".format(addr))
            threading.Thread(target=self._respond,
                             args=(connection, addr)).start()

    def _send_request_to_server(self, request):
        hash_value = hash(request)
        status = False
        while not status:
            chosen_server = hash_value % self.num_servers
            print("\nchosen_server : ", chosen_server)
            server_ip_port = self.server_details[chosen_server]

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            try:
                sock.connect((server_ip_port[0], server_ip_port[1]))
            #Connection timed out
            except ConnectionRefusedError:
                #lock start
                self.lock.acquire()

                if(server_ip_port in self.server_details):
                    self.num_servers -= 1
                    self.server_details.remove(server_ip_port)

                self.lock.release()
                continue
                #lock end

            except Exception:
                continue

            sock.sendall(request)

            response = b''
            while True:
                temp = sock.recv(Constants.BUF_SIZE)
                response += temp

                if len(temp) < Constants.BUF_SIZE:
                    break
            
            status = True

        print("\nServ - response : ",response)
        return response

    def _add_server_entry(self, ip_port):
        self.lock.acquire()

        self.num_servers += 1
        self.server_details.append(ip_port)

        self.lock.release()

    def _respond(self, connection, addr):

        request = connection.recv(Constants.BUF_SIZE)
        print("\npeer/serv - request : ",request)
        try:
            
            request_check = ast.literal_eval(request.decode())
            if(request_check[0] == -10):
                # New Server has been added
                self._add_server_entry(request_check[1])

            else:
                response = self._send_request_to_server(request)

                connection.sendall(response)

        except Exception:
            # Key share which should be sent to the server

            response = self._send_request_to_server(request)

            connection.sendall(response)

        connection.close()

if __name__ == "__main__":

    clearrecord.clear()

    with open("server_info.json") as j:
        server_info = json.load(j)
    
    serv_ip = server_info["ip"]
    serv_port = server_info["port"]

    load_balancer = LoadBalancer(serv_ip, serv_port)
    load_balancer.start()