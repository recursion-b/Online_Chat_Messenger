import socket
import time

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.setblocking(0)  # ソケットを非ブロッキングモードに設定

def send_message(username):
    message = input("Enter your message: ")
    usernamelen = len(username.encode('utf-8'))
    full_message = bytes([usernamelen]) + username.encode('utf-8') + message.encode('utf-8')
    
    # デバッグ出力
    print(f"Sending message: {full_message}")

    client_socket.sendto(full_message, ('127.0.0.1', 12345))

    # メッセージ送信後、短い間隔で複数回データ受信を試みる
    end_time = time.time() + 2  # 2秒間データ受信を試みる
    while time.time() < end_time:
        try:
            data, _ = client_socket.recvfrom(4096)
            print(data.decode('utf-8'))
        except BlockingIOError:
            print("No data received, retrying...")  # デバッグ出力
            time.sleep(0.1)  # 短いスリープを入れてリソースの浪費を避ける
        except Exception as e:
            print(f"Unexpected error while receiving data: {e}")  # その他のエラーのデバッグ出力

username = input("Enter your username: ")

while True:
    option = input("1. Send a message\n2. Quit\nChoose an option: ")

    if option == "1":
        send_message(username)
    elif option == "2":
        break

client_socket.close()
