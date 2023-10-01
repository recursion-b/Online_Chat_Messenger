# client
import socket
import threading
from typing import Tuple
import json


class ChatClient:
    def __init__(self):
        # self.server_address = "127.0.0.1"
        self.server_address = self.get_ip_address()
        self.tcp_port = 12345
        self.udp_port = 12346
        self.address = (self.server_address, self.udp_port)
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.token = ""
        self.user_name = ""
        self.room_name = ""
        self.operation_code = 0  # Noneにしないための仮の数字
        self.state = 0

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

    """
    TODO: サーバーでも同じプロトコルを使うので切り出して使いまわせるようにする
    tcp_chat_room_protocol_header
    tcp_send_data
    tcp_receive_data
    """

    def tcp_chat_room_protocol_header(
        self,
        room_name_size: int,
        operation_code: int,
        state: int,
        json_string_payload_size: int,
    ) -> bytes:
        # Header(32bytes): RoomNameSize(1) | Operation(1) | State(1) | OperationPayloadSize(29)
        # 1つの256ビットバイナリに結合
        return (
            room_name_size.to_bytes(1, "big")
            + operation_code.to_bytes(1, "big")
            + state.to_bytes(1, "big")
            + json_string_payload_size.to_bytes(29, "big")
        )

    def tcp_send_data(self, json_payload: dict):
        # サーバーへ接続要求
        self.tcp_socket.connect((self.server_address, self.tcp_port))

        room_name_bits = self.room_name.encode()
        json_string_payload_bits = json.dumps(json_payload).encode()

        # ヘッダ作成
        header = self.tcp_chat_room_protocol_header(
            len(room_name_bits),
            self.operation_code,
            self.state,
            len(json_string_payload_bits),
        )
        # ボディ作成
        body = room_name_bits + json_string_payload_bits

        self.tcp_socket.send(header)
        self.tcp_socket.send(body)

    def tcp_receive_data(self) -> Tuple[str, int, int, dict]:
        # ヘッダ受信
        header = self.tcp_socket.recv(32)
        # ヘッダから長さなどを抽出
        room_name_size = int.from_bytes(header[:1], "big")
        operation_code = int.from_bytes(header[1:2], "big")
        state = int.from_bytes(header[2:3], "big")
        json_payload_size = int.from_bytes(header[3:33], "big")
        # ボディから抽出
        room_name = self.tcp_socket.recv(room_name_size).decode()
        json_payload = json.loads(self.tcp_socket.recv(json_payload_size).decode())

        return (room_name, operation_code, state, json_payload)

    def udp_chat_message_protocol_header(self, json_size: int) -> bytes:
        return json_size.to_bytes(2, "big")

    def initialize_tcp_connection(
        self,
        json_payload: dict,
    ) -> None:
        try:
            """
            Chat_Room_Protocol: サーバの初期化(0)
            クライアントが新しいチャットルームを作成するリクエストを送信
            ペイロードには希望するユーザー名が含まれる

            Chat_Room_Protocol
            Header(32): RoomNameSize(1) | Operation(1) | State(1) | OperationPayloadSize(29)
            Body: RoomName(RoomNameSize) | OperationPayload(user_name)(2^29)
            """

            self.tcp_send_data(json_payload)
            # # サーバーへ接続要求
            # self.tcp_socket.connect((self.server_address, self.tcp_port))

            # room_name_bits = self.room_name.encode()
            # json_string_payload_bits = json_string_payload.encode()

            # # ヘッダ作成
            # header = self.tcp_chat_room_protocol_header(
            #     len(room_name_bits),
            #     self.operation_code,
            #     self.state,
            #     len(json_string_payload_bits),
            # )
            # # ボディ作成
            # body = room_name_bits + json_string_payload_bits

            # self.tcp_socket.send(header)
            # self.tcp_socket.send(body)

        except Exception as e:
            print(f"Error: {e} from initialize_tcp_connection")
            self.tcp_socket.close()
            exit(1)

    def receive_request_result(self) -> None:
        try:
            """
            チャットルームプロトコル
            リクエストの応答(1): サーバからステータスコードを含むペイロードで即座に応答を受け取る
            返り値: (stauts, message)
            status:
                success: 部屋の作成に成功
                room already exists: すでに同じ名前の部屋が存在する
                not found room: 部屋が存在しない
                failed: 何らかのエラー
            message: メッセージ
            """
            room_name, operation_code, state, json_payload = self.tcp_receive_data()

            status = json_payload["status"]
            message = json_payload["message"]

            if status != "success":
                print(message)
                self.tcp_socket.close()
                exit(1)

            print(message)

        except Exception as e:
            print(f"Error: {e} from receive_request_result")
            self.tcp_socket.close()
            exit(1)

    def receive_token(self) -> str:
        try:
            room_name, operation_code, state, json_payload = self.tcp_receive_data()

            token = json_payload["token"]

        except Exception as e:
            print(f"Error: {e} from receive_token")
            exit(1)

        finally:
            self.tcp_socket.close()

        return token

    def udp_receive_messages(self):
        while True:
            message, addr = self.udp_socket.recvfrom(4096)
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

    def udp_send_messages(
        self,
        message: str,
    ):
        full_content = {
            "token": self.token,
            "user_name": self.user_name,
            "room_name": self.room_name,
            "message": message,
        }

        full_content_bits = json.dumps(full_content).encode()

        # UDPヘッダの作成(2bytes)
        header = self.udp_chat_message_protocol_header(len(full_content_bits))

        # UDPボディの作成(max 4094bytes)
        body = full_content_bits

        self.udp_socket.sendto(header + body, self.address)

    def prompt_and_validate_user_name(self) -> str:
        max_bytes_in_user_name = 255

        while True:
            user_name = input("Enter your username: ")

            if len(user_name.encode()) > max_bytes_in_user_name:
                print("The username exceeds the maximum character limit.")

            elif len(user_name) <= 0:
                print("Username is required.")

            else:
                return user_name

    def prompt_and_validate_operation_code(self) -> str:
        while True:
            operation_code = input("Create (1) or Join (2) a chatroom? ")

            if operation_code == "1" or operation_code == "2":
                return operation_code

            else:
                print("Please enter 1 or 2.")

    def prompt_and_validate_room_name(self) -> str:
        max_bytes_in_room_name = 255

        while True:
            room_name = input("Enter roomname: ")
            if len(room_name.encode()) > max_bytes_in_room_name:
                print("The roomname exceeds the maximum character limit.")
            elif len(room_name) <= 0:
                print("Roomname is required.")
            else:
                return room_name

    def start(self):
        self.user_name = self.prompt_and_validate_user_name()
        self.operation_code = int(self.prompt_and_validate_operation_code())
        self.room_name = self.prompt_and_validate_room_name()

        json_payload = {"user_name": self.user_name}

        # TCP接続
        self.initialize_tcp_connection(json_payload)

        # レスポンスの応答
        self.receive_request_result()

        # トークンの受け取り
        self.token = self.receive_token()

        # トークン取得後,自動的にUDPへ接続
        self.udp_socket.bind(("0.0.0.0", 0))
        first_message = (
            f"{self.user_name}がルームを作成しました"
            if self.operation_code == 1
            else f"{self.user_name}が参加しました"
        )
        self.udp_send_messages(first_message)

        # 受信用のスレッドを開始
        threading.Thread(target=self.udp_receive_messages).start()

        while True:
            message = input("Your message: ")
            self.udp_send_messages(message)


if __name__ == "__main__":
    client = ChatClient()
    client.start()
