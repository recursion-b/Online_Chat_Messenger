import socket
import threading

SERVER_ADDRESS = "0.0.0.0"
SERVER_PORT = 9001

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((SERVER_ADDRESS, SERVER_PORT))

clients = {}

print("チャットサーバーがスタートしました。")

while True:
    message, client_address = server_socket.recvfrom(4096)
    message = message.decode("utf-8")

    if client_address not in clients:
        client_name = message
        clients[client_address] = client_name
        print(f"{client_name}がチャットに参加しました")

    else:
        print(f"受信したメッセージ)({client_address}):{message}")

        for client, name in clients.items():
            if client != client_address:
                server_socket.sendto(
                    f"{clients[client_address]}: {message}".encode(), client
                )
