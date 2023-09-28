# client
import socket
import threading


class ChatClient:
    def __init__(self):
        self.server_address = "127.0.0.1"
        self.tcp_port = 12345
        self.udp_port = 12346

    def initialize_tcp_connection(self, operation_code, room_name):
        # TCPソケットの作成
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # サーバーへ接続要求
        tcp_socket.connect((self.server_address, self.tcp_port))

        # TODO: チャットルームプロトコル
        # Operation(チャットルーム作成:1, チャットルーム参加:2)
        tcp_socket.send(operation_code.encode())
        # \x00(文字列の終端)を255バイトに左寄せ
        # room_name -> room_name\x00\x00...
        tcp_socket.send(room_name.ljust(255, "\x00").encode())

        # トークン受信
        token = tcp_socket.recv(4096).decode()
        # TCP終了
        tcp_socket.close()

        return token

    def udp_receive_messages(self, udp_socket):
        while True:
            # TODO: UDP(HeaderとBody)プロトコル
            # クライアントはサーバから最大で4094バイトのパケットを受信できます。
            # これはメッセージのみで、ヘッダーは含まれません。
            message, addr = udp_socket.recvfrom(4096)

            # メッセージからルーム名を取り出す
            room_name, user_message = message.decode().split("] ", 1)
            print(f"{room_name}] {addr} says: {user_message}")

    def start(self):
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.bind(("0.0.0.0", 0))

        username = input("Enter your username: ")
        operation = input("Create (C) or Join (J) a chatroom? ")
        room_name = input("Enter room name: ")

        token = self.initialize_tcp_connection(operation, room_name)

        # トークンの取得後に受信用のスレッドを開始
        threading.Thread(target=self.udp_receive_messages, args=(udp_socket,)).start()

        while True:
            message = input("Your message: ")
            # TODO: UDP(HeaderとBody)プロトコル
            # クライアントは最大4096バイトのメッセージを送れる。
            # そのうちの最初の2バイトは、ルーム名とトークンのバイトサイズを示す。
            # Header：RoomNameSize（1バイト）| TokenSize（1バイト）
            # Body :roomName(RoomNameSize) | TokenString(TokenSize) | message(255-2-RoomNameSize-TokenSize)
            # 最初のRoomNameSizeバイトはルーム名、次のTokenSizeバイトはトークン文字列、
            # そしてその残りが実際のメッセージです。
            full_message = f"{token}|[{username}]{message}"
            udp_socket.sendto(
                full_message.encode(), (self.server_address, self.udp_port)
            )


if __name__ == "__main__":
    client = ChatClient()
    client.start()
