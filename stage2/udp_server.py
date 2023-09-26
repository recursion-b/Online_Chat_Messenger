#UDP
import socket
import threading

class UDPServer:
    def __init__(self, ip='0.0.0.0', port=12346):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((ip, port))
        self.clients = {}

    def run(self):
        print("UDP server started on port 12346...")
        while True:
            data, addr = self.server_socket.recvfrom(4096)

            # クライアントアドレスをclients辞書に追加
            self.clients[addr] = True
            print(f"Added client address: {addr}")

            room_name_len = data[0]
            token_len = data[1]

            offset = 2
            room_name = data[offset:offset+room_name_len].decode('utf-8')
            offset += room_name_len

            token = data[offset:offset+token_len].decode('utf-8')
            offset += token_len

            message = data[offset:].decode('utf-8')

            print(f"Received message in room '{room_name}' from ({addr}): {message}")

            for client_addr in self.clients:
                print(f"Attempting to send to: {client_addr}")
                # if client_addr != addr:
                #     self.server_socket.sendto(f"({addr[0]}:{addr[1]}): {message}".encode('utf-8'), client_addr)
                try:
                    self.server_socket.sendto(f"({addr}): {message}".encode('utf-8'), client_addr)
                except Exception as e:
                    print(f"Error sending to {client_addr}: {e}")


if __name__ == "__main__":
    server = UDPServer()
    server.run()