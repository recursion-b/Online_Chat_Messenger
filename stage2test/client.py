import socket
import threading

class ChatClient:
    def __init__(self):
        self.server_address = '127.0.0.1'
        self.tcp_port = 12345
        self.udp_port = 12346

    def initialize_tcp_connection(self, operation_code, room_name):
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.connect((self.server_address, self.tcp_port))
        tcp_socket.send(operation_code.encode())
        tcp_socket.send(room_name.ljust(255, '\x00').encode())

        token = tcp_socket.recv(4096).decode()
        tcp_socket.close()

        return token

    def udp_receive_messages(self, udp_socket):
        while True:
            message, addr = udp_socket.recvfrom(4096)

            # メッセージからルーム名を取り出す
            room_name, user_message = message.decode().split('] ', 1)
            print(f"{room_name}] {addr} says: {user_message}")

    def start(self):
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.bind(('0.0.0.0', 0))

        username = input("Enter your username: ")
        operation = input("Create (C) or Join (J) a chatroom? ")
        room_name = input("Enter room name: ")

        token = self.initialize_tcp_connection(operation, room_name)

        # トークンの取得後に受信用のスレッドを開始
        threading.Thread(target=self.udp_receive_messages, args=(udp_socket,)).start()

        while True:
            message = input("Your message: ")
            full_message = f"{token}|[{username}]{message}"
            udp_socket.sendto(full_message.encode(), (self.server_address, self.udp_port))

if __name__ == "__main__":
    client = ChatClient()
    client.start()
