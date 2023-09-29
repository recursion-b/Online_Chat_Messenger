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
        """
        チャットルームプロトコル
        サーバの初期化(0): クライアントが新しいチャットルームを作成するリクエストを送信
        ペイロードには希望するユーザー名が含まれる

        Chat_Room_Protocol
        Header(32): RoomNameSize(1) | Operation(1) | State(1) | OperationPayloadSize(29)
        Body: RoomName(RoomNameSize) | OperationPayload(room_name + user_name)(2^29)
        """

        room_name_bits = room_name.encode()
        # 最初のRoomNameSizeバイトがルーム名、その後にOperationPayloadSizeバイトが続く
        operation_payload_bits = room_name.encode() + operation_payload.encode()

        header = self.tcp_chat_room_protocol_header(
            len(room_name_bits), operation_code, state, len(operation_payload_bits)
        )

        # TCPソケットの作成
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            # サーバーへ接続要求
            tcp_socket.connect((self.server_address, self.tcp_port))

            # ヘッダの送信
            tcp_socket.send(header)

            # ペイロード(room_name + user_name)の送信
            tcp_socket.send(operation_payload_bits)

            """
            チャットルームプロトコル
            リクエストの応答(1): サーバからステータスコードを含むペイロードで即座に応答を受け取る
            """
            # ヘッダ受信
            header = tcp_socket.recv(32)
            # ヘッダから長さなどを抽出
            room_name_size = int.from_bytes(header[:1], "big")
            operation_code = int.from_bytes(header[1:2], "big")
            state = int.from_bytes(header[2:3], "big")
            operation_payload_size = int.from_bytes(header[3:33], "big")

            room_name = tcp_socket.recv(room_name_size).decode()
            status = tcp_socket.recv(operation_payload_size).decode()

            if state == 1:
                if status == "200":
                    print("サーバから応答がありました")
                else:
                    print("サーバから応答がありませんでした。")

            """
            TODO: チャットルームプロトコル
            リクエストの完了(2): サーバで生成されたユニークなトークンを受け取る。
            チャットルームを作成する時このトークンはチャットルームのホストとして識別される。
            チャットルームに参加する時も生成されたトークンを受け取るが、ホストではない。
            トークンは最大255バイト。
            """
            # トークンの受信
            token = tcp_socket.recv(4096).decode()
            print(token)

        finally:
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

        if not operation_code.isdecimal():
            raise Exception("引数には数字を指定してください")

        # TODO: token受け取りに失敗した場合のエラーハンドリング
        token = self.initialize_tcp_connection(
            room_name, int(operation_code), 0, user_name
        )

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
