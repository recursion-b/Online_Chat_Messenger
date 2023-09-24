import socket
import asyncio
from datetime import datetime
import selectors

selector = selectors.DefaultSelector()

loop = asyncio.get_event_loop()

class ClientInfo:
    def __init__(self, username, address):
        self.username = username
        self.address = address
        self.last_active = datetime.now()

clients = {}

async def cleanup_clients():
    while True:
        current_time = datetime.now()
        clients_to_remove = [
            addr for addr, client in clients.items()
            if (current_time - client.last_active).seconds > 60
        ]
        for addr in clients_to_remove:
            del clients[addr]
        await asyncio.sleep(10)  # Cleanup every 10 seconds

async def handle_client(data, addr):
    print(f"Data received from {addr}: {data}")

    usernamelen = data[0]
    username = data[1:1 + usernamelen].decode('utf-8')
    message = data[1 + usernamelen:].decode('utf-8')
    
    if addr not in clients:
        clients[addr] = ClientInfo(username, addr)
    else:
        clients[addr].last_active = datetime.now()

    print(f"Received message from {username}: {message}")
    for client_addr, client_info in clients.items():
        if client_addr != addr:
            full_message = f"{username}: {message}".encode('utf-8')
            server_socket.sendto(full_message, client_addr)
    print(f"Attempting to send message to {client_addr}")
    server_socket.sendto(full_message, client_addr)

async def recvfrom(sock):
    future = loop.create_future()

    def on_ready(*args):
        selector.unregister(sock)
        try:
            result = sock.recvfrom(4096)
            future.set_result(result)
        except Exception as e:
            future.set_exception(e)

    key = selector.register(sock, selectors.EVENT_READ, on_ready)

    return await future

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('0.0.0.0', 12345))
server_socket.setblocking(False)

async def main():
    asyncio.create_task(cleanup_clients())  # Cleanup taskを起動
    while True:
        data, addr = await recvfrom(server_socket) 
        asyncio.create_task(handle_client(data, addr))

loop.run_until_complete(main())
