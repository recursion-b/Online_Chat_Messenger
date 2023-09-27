import socket
import threading
import random
import string

class ChatServer:
    def __init__(self):
        self.chat_rooms = {}
        self.tokens = {}
        self.tcp_port = 12345
        self.udp_port = 12346

    def generate_token(self, size=10):
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(size))

    def tcp_handler(self, conn, addr):
        operation = conn.recv(1).decode()
        room_name = conn.recv(255).decode().rstrip('\x00')

        if operation == 'C':
            if room_name not in self.chat_rooms:
                self.chat_rooms[room_name] = []
            token = self.generate_token()
            self.tokens[token] = room_name
            conn.send(token.encode())

        elif operation == 'J':
            if room_name in self.chat_rooms:
                token = self.generate_token()
                self.tokens[token] = room_name
                conn.send(token.encode())
            else:
                conn.send("ERROR".encode())

        conn.close()

    def udp_handler(self):
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.bind(('0.0.0.0', self.udp_port))

        while True:
            data, addr = udp_socket.recvfrom(4096)
            token, username_message = data.decode().split('|', 1)
            username, message = username_message.split(']', 1)

            if token in self.tokens:
                room_name = self.tokens[token]
                print(f"[{room_name} - {addr}] {username} says: {message}")
                room_message = f"[{room_name}]{username}] {message}"
                for client in self.chat_rooms[room_name]:
                    if client != addr:
                        udp_socket.sendto(room_message.encode(), client)
                if addr not in self.chat_rooms[room_name]:
                    self.chat_rooms[room_name].append(addr)

    def start(self):
        tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_server.bind(('0.0.0.0', self.tcp_port))
        tcp_server.listen(5)

        threading.Thread(target=self.udp_handler).start()

        while True:
            conn, addr = tcp_server.accept()
            threading.Thread(target=self.tcp_handler, args=(conn, addr)).start()

if __name__ == "__main__":
    server = ChatServer()
    server.start()
