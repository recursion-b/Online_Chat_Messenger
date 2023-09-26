#TCP
import socket
import threading

class TCPServer:
    def __init__(self, ip='0.0.0.0', port=12345):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((ip, port))
        self.server_socket.listen(5)
        self.rooms = {}

    def handle_client(self, client_socket):
        header = client_socket.recv(32)
        room_name_len = header[0]
        operation = header[1]

        body = client_socket.recv(4096)
        room_name = body[:room_name_len].decode('utf-8')
        username = body[room_name_len:].decode('utf-8')

        if operation == 1:  
            if room_name not in self.rooms:
                self.rooms[room_name] = []
                print(f"Room '{room_name}' has been created!")
            token = body[room_name_len + len(username):].decode('utf-8')
            self.rooms[room_name].append(token)
            client_socket.sendall(b'\x00\x01\x01' + b'0' * 29)
            client_socket.close()
        elif operation == 2:  
            token = body[room_name_len + len(username):].decode('utf-8')
            if room_name in self.rooms:
                self.rooms[room_name].append(token)
                client_socket.sendall(b'\x00\x01\x01' + b'0' * 29)
                client_socket.close()

    def run(self):
        print("TCP server started on port 12345...")
        while True:
            client_socket, addr = self.server_socket.accept()
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

if __name__ == "__main__":
    server = TCPServer()
    server.run()
