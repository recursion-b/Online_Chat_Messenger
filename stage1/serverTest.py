import socket
from datetime import datetime, timedelta

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('0.0.0.0', 12345))

clients = {}

print("Server is listening on port 12345...")

while True:
    data, addr = server_socket.recvfrom(4096)

    # ユーザーネームの長さを取得
    usernamelen = data[0]
    # ユーザーネームとメッセージを取得
    username = data[1:1+usernamelen].decode('utf-8')
    message = data[1+usernamelen:].decode('utf-8')

    print(f"Received message from {username}: {message}")

    if addr not in clients:
        clients[addr] = {'username': username, 'last_active': datetime.now()}
    else:
        clients[addr]['last_active'] = datetime.now()

    for client_addr, client_info in list(clients.items()):
        # クライアントの最後のアクティブ時間が60秒以上前の場合、リストから削除
        if datetime.now() - client_info['last_active'] > timedelta(seconds=60):
            del clients[client_addr]
        elif client_addr != addr:
            full_message = f"{username}: {message}".encode('utf-8')
            server_socket.sendto(full_message, client_addr)
