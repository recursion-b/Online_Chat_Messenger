import socket
import asyncio

class ChatClient:
    def __init__(self, address, port, additional_data=None):
        self.address = address
        self.port = port
        self.additional_data = additional_data

    def unique_key(self):
        return f"{self.address}:{self.port}"

class ChatRoom:
    def __init__(self, title, max_participants):
        self.title = title
        self.max_participants = max_participants
        self.participants = {}

rooms = {}
def create_chatroom(title, max_participants):
    roomname = title + "_" + str(len(rooms))
    new_room = ChatRoom(title, max_participants)
    rooms[roomname] = new_room
    return roomname
def join_room(roomname, client_socket, addr):  # client_socket parameter added
    room = rooms.get(roomname)
    client_key = f"{addr[0]}:{addr[1]}"
    if room and len(room.participants) < room.max_participants and client_key not in room.participants:
        client_obj = ChatClient(addr[0], addr[1], client_socket)  # pass client_socket here
        room.participants[client_obj.unique_key()] = client_obj
        return f"Joined room {roomname}."
    elif room and client_key in room.participants:
        return f"You are already in room {roomname}."
    else:
        return "Room is full or doesn't exist."
async def handle_client(client, addr):
    client_key = f"{addr[0]}:{addr[1]}"  
    while True:
        data = await loop.sock_recv(client, 4096)
        if not data:
            break
        msg = data.decode('utf-8')
        print(f"Received message from {addr}: {msg}")
        parts = msg.split(":")
        roomname = parts[0]

        if msg.startswith("create_room"):
            _, title, max_participants = msg.split(":")
            roomname = create_chatroom(title, int(max_participants))
            await loop.sock_sendall(client, f"Room {roomname} created.".encode('utf-8'))
            continue

        elif parts[1] == "join":
            response = join_room(roomname, client, addr)
            await loop.sock_sendall(client, response.encode('utf-8'))

        else:
            message_size = int(parts[1])
            message = parts[2]
            room = rooms.get(roomname)
            if room and client_key in room.participants:
                for participant_key, participant in room.participants.items():
                    if participant_key != client_key:  
                        participant_socket = participant.additional_data
                        await loop.sock_sendall(participant_socket, message.encode('utf-8')) 

loop = asyncio.get_event_loop()
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('0.0.0.0', 12345)) 
server_socket.listen(5)
server_socket.setblocking(False)

async def main():
    while True:
        client, addr = await loop.sock_accept(server_socket)
        loop.create_task(handle_client(client, addr))

loop.run_until_complete(main())
