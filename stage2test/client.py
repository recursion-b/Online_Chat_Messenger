#client
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
            decoded_message = message.decode()
            # 非アクティブのため接続が切断されましたメッセージを受け取ったら終了する
            if decoded_message == "非アクティブのため接続が切断されました":
                print(decoded_message)
                exit(0)  # アプリケーションを終了
            if '] ' in decoded_message:
                room_name, user_message = decoded_message.split('] ', 1)
                print(f"{room_name}] {addr} says: {user_message}")
            else:
                # 予期しないメッセージ形式の場合、そのまま表示
                print(decoded_message)


    def start(self):
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.bind(('0.0.0.0', 0))

        username = input("ユーザー名を入力してください: ")
        operation = input("チャットルームを作成(C)するか、参加(J)しますか？: ")
        room_name = input("チャットルームの名前を入力してください: ")

        token = self.initialize_tcp_connection(operation, room_name)

        if token == "エラー：存在しないチャットルームです":
            print(token)
            return
        else:
            if operation == 'C':
                print(f"チャットルーム'{room_name}'を作成しました！")
            elif operation == 'J':
                print(f"チャットルーム'{room_name}'に参加しました！")

        # トークンの取得後に受信用のスレッドを開始
        threading.Thread(target=self.udp_receive_messages, args=(udp_socket,)).start()

        while True:
            message = input("メッセージを入力してください: ")
            full_message = f"{token}|[{username}]{message}"
            udp_socket.sendto(full_message.encode(), (self.server_address, self.udp_port))

if __name__ == "__main__":
    client = ChatClient()
    client.start()
