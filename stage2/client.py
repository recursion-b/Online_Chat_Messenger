# client
import socket
import threading
import json


class ChatClient:
    def __init__(self):
        # self.server_address = "127.0.0.1"
        self.server_address = self.get_ip_address()
        self.tcp_port = 12345
        self.udp_port = 12346

    def get_ip_address(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("10.254.254.254", 1))
            ip = s.getsockname()[0]
        except:
            ip = "127.0.0.1"
        finally:
            s.close()
        return ip

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

        # TCPソケットの作成
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            # サーバーへ接続要求
            tcp_socket.connect((self.server_address, self.tcp_port))

            room_name_bits = room_name.encode()
            operation_payload_bits = operation_payload.encode()

            # ヘッダ作成
            header = self.tcp_chat_room_protocol_header(
                len(room_name_bits), operation_code, state, len(operation_payload_bits)
            )

            # ボディ作成
            # 最初のRoomNameSizeバイトがルーム名、その後にOperationPayloadSizeバイトが続く
            body = room_name_bits + operation_payload_bits

            # ヘッダの送信
            tcp_socket.send(header)

            # ペイロード(room_name + user_name)の送信
            tcp_socket.send(body)

            # レスポンスの応答確認
            isSuccess = self.isSuccess_response(tcp_socket)
            if isSuccess:
                print("サーバから応答がありました")
                # トークンの受け取り
                return self.receive_token(tcp_socket)

            else:
                print("サーバから応答がありませんでした。")
                tcp_socket.close()
                exit(1)

        except Exception as e:
            print(f"Error: {e} from initialize_tcp_connection")
            tcp_socket.close()
            exit(1)

    def isSuccess_response(self, tcp_socket) -> bool:
        """
        チャットルームプロトコル
        リクエストの応答(1): サーバからステータスコードを含むペイロードで即座に応答を受け取る
        """
        try:
            # ヘッダ受信
            header = tcp_socket.recv(32)
            # ヘッダから長さなどを抽出
            room_name_size = int.from_bytes(header[:1], "big")
            operation_code = int.from_bytes(header[1:2], "big")
            state = int.from_bytes(header[2:3], "big")
            operation_payload_size = int.from_bytes(header[3:33], "big")

            room_name = tcp_socket.recv(room_name_size).decode()
            status = tcp_socket.recv(operation_payload_size).decode()
            print(str(state) + status)

            return state == 1 and status == "success"

        except Exception as e:
            print(f"Error: {e} from isSuccess_response")
            exit(1)

    def receive_token(self, tcp_socket) -> str:
        try:
            token = tcp_socket.recv(4096).decode()

        except Exception as e:
            print(f"Error: {e} from receive_token")
            exit(1)

        finally:
            tcp_socket.close()

        return token

    def udp_receive_messages(self, udp_socket):
        while True:
            message, addr = udp_socket.recvfrom(4096)
            try:
                # メッセージからルーム名、ユーザー名、メッセージを取り出す
                data = json.loads(message.decode())
                room_name = data["room_name"]
                username = data["username"]
                msg = data["message"]
                print(f"\nRoom -> {room_name}| Sender -> {username} says: {msg}")
            except json.decoder.JSONDecodeError:
                print("Received an invalid message format.")
            except KeyError as e:
                print(
                    f"Key error: {e}. The received message does not have the expected format."
                )

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
            message_content = {
                "token": token,
                "username": user_name,
                "message": message,
            }
            full_message = json.dumps(message_content)
            udp_socket.sendto(
                full_message.encode(), (self.server_address, self.udp_port)
            )


if __name__ == "__main__":
    client = ChatClient()
    client.start()
