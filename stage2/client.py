#client
import socket
import time
import random
import string

def generate_token(size=255):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(size))

def initialize_tcp_connection(username, operation_code):
    room_name = input("Enter the room name: ")

    header = bytes([len(room_name), operation_code, 0]) + b'0' * 29
    body = room_name.encode('utf-8') + username.encode('utf-8')

    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect(('127.0.0.1', 12345))
    tcp_socket.sendall(header + body)

    response = tcp_socket.recv(4096)
    state = response[2]
    if state == 1:
        token = generate_token()
        payload = token.encode('utf-8')
        header = bytes([len(room_name), operation_code, 2]) + b'0' * 29
        tcp_socket.sendall(header + body + payload)
        tcp_socket.close()
        return room_name, token
    else:
        print("Failed to connect to room.")
        exit()

def send_message_udp(room_name, token):
    message = input("Enter your message: ")
    header = bytes([len(room_name), len(token)])
    full_message = header + room_name.encode('utf-8') + token.encode('utf-8') + message.encode('utf-8')
    client_socket.sendto(full_message, ('127.0.0.1', 12346))

    try:
        data, _ = client_socket.recvfrom(4096)
        print(data.decode('utf-8'))
    except socket.timeout:
        print("No response received within the timeout period.")

if __name__ == "__main__":
    username = input("Enter your username: ")
    option = input("1. Create a chatroom\n2. Join a chatroom\n3. Quit\nChoose an option: ")

    if option == "1":
        room_name, token = initialize_tcp_connection(username, 1)
    elif option == "2":
        room_name, token = initialize_tcp_connection(username, 2)
    else:
        exit()

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # client_socket.bind(('127.0.0.1', 0))
    client_socket.settimeout(10)

    while True:
        send_message_udp(room_name, token)
