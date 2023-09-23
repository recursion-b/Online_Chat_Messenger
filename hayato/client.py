import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('127.0.0.1', 12345))

def create_room():
    title = input("Enter room title: ")
    max_participants = input("Enter max participants: ")
    request = f"create_room:{title}:{max_participants}"
    client_socket.sendall(request.encode('utf-8'))
    response = client_socket.recv(4096)
    print(response.decode('utf-8'))

def join_room():
    room_name = input("Enter room name to join: ")
    request = f"{room_name}:join"
    client_socket.sendall(request.encode('utf-8'))
    response = client_socket.recv(4096)
    print(response.decode('utf-8'))

while True:
    option = input("1. Send a message\n2. Create a room\n3. Join a room\n4. Quit\nChoose an option: ")

    if option == "1":
        room_name = input("Enter room name: ")
        message = input("Enter your message: ")
        full_message = f"{room_name}:{len(message)}:{message}"
        client_socket.sendall(full_message.encode('utf-8'))
    elif option == "2":
        create_room()
    elif option == "3":
        join_room()
    elif option == "4":
        break

client_socket.close()