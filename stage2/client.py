# client
import socket
import threading


class ChatClient:
    def __init__(self):
        self.server_address = "127.0.0.1"
        self.tcp_port = 12345
        self.udp_port = 12346

    def initialize_tcp_connection(
        self, room_name: str, operation_code: int, state: int, operation_payload: str
    ) -> str:
        # TCPソケットの作成
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # サーバーへ接続要求
        tcp_socket.connect((self.server_address, self.tcp_port))

        # TODO: チャットルームプロトコル
        # サーバの初期化(0): クライアントが新しいチャットルームを作成するリクエストを送信
        # ペイロードには希望するユーザー名が含まれる。

        # Chat_Room_Protocol
        # Header(32): RoomNameSize(1) | Operation(1) | State(1) | OperationPayloadSize(29)
        # Body: payload(user_name)
        room_name_bits = room_name.encode()
        operation_payload_bits = operation_payload.encode()

        header = self.tcp_chat_room_protocol_header(
            len(room_name_bits), operation_code, state, len(operation_payload_bits)
        )

        # ヘッダの送信
        tcp_socket.send(header)

        # ペイロード(user_name)の送信
        tcp_socket.send(operation_payload_bits)

        # トークンの受信
        token = tcp_socket.recv(4096).decode()

        # ソケットを閉じる
        tcp_socket.close()

        return token

    def tcp_chat_room_protocol_header(
        self,
        room_name_size: int,
        operation_code: int,
        state: int,
        operation_payload_size: int,
    ) -> bytes:
        # Header(32bytes): RoomNameSize(1) | Operation(1) | State(1) | OperationPayloadSize(29)
        # 1つの256ビットバイナリに結合
        return (
            room_name_size.to_bytes(1, "big")
            + operation_code.to_bytes(1, "big")
            + state.to_bytes(1, "big")
            + operation_payload_size.to_bytes(29, "big")
        )

    def udp_receive_messages(self, udp_socket):
        while True:
            message, addr = udp_socket.recvfrom(4096)

            # メッセージからルーム名を取り出す
            room_name, user_message = message.decode().split("] ", 1)
            print(f"{room_name}] {addr} says: {user_message}")

    def start(self):
        # UDPソケットの作成
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # バインド
        udp_socket.bind(("0.0.0.0", 0))

        # TODO: バリデーション
        user_name = input("Enter your username: ")
        operation_code = input("Create (1) or Join (2) a chatroom? ")
        room_name = input("Enter room name: ")

        if operation_code.isdecimal():
            token = self.initialize_tcp_connection(
                room_name, int(operation_code), 0, user_name
            )
        else:
            raise Exception("引数には数字を指定してください")

        # トークンの取得後に受信用のスレッドを開始
        threading.Thread(target=self.udp_receive_messages, args=(udp_socket,)).start()

        while True:
            message = input("Your message: ")
            full_message = f"{token}|[{user_name}]{message}"
            udp_socket.sendto(
                full_message.encode(), (self.server_address, self.udp_port)
            )


if __name__ == "__main__":
    client = ChatClient()
    client.start()
