import socket
import time

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.settimeout(2)  # タイムアウトを2秒に設定

def send_message(username):
    message = input("Enter your message: ")
    usernamelen = len(username.encode('utf-8'))
    full_message = bytes([usernamelen]) + username.encode('utf-8') + message.encode('utf-8')
    client_socket.sendto(full_message, ('127.0.0.1', 12345))

    try:
        data, _ = client_socket.recvfrom(4096)
        print(data.decode('utf-8'))
    except socket.timeout:
        print("No response received within the timeout period.")

username = input("Enter your username: ")

while True:
    option = input("1. Send a message\n2. Quit\nChoose an option: ")

    if option == "1":
        send_message(username)
    elif option == "2":
        break

client_socket.close()

