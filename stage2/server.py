# server
import socket
import threading
import random
import string
import time
from typing import Tuple
import json


class ClientInfo:
    def __init__(
        self,
        udp_addr=None,
        tcp_addr=None,
        access_token=None,
        username=None,
        is_host=False,
    ):
        self.udp_addr = udp_addr
        self.tcp_addr = tcp_addr
        self.access_token = access_token
        self.username = username
        self.is_host = is_host
        self.last_message_time = time.time()

    def __repr__(self):
        return (
            f"<ClientInfo(udp_addr={self.udp_addr}, tcp_addr={self.tcp_addr}, "
            f"access_token={self.access_token}, username={self.username}, is_host={self.is_host})>"
        )


class ChatRoom:
    def __init__(self, room_name):
        self.room_name = room_name
        self.client_infos = []

    def __repr__(self):
        return (
            f"<ChatRoom(room_name={self.room_name}, client_infos={self.client_infos})>"
        )

    def add_client_info_if_not_exists(self, client_info):
        if client_info not in self.client_infos:
            self.client_infos.append(client_info)

    def broadcast_message_to_clients(self, addr, udp_socket, message_content):
        for client_info in self.client_infos:
            if client_info.udp_addr != addr:
                udp_socket.sendto(
                    json.dumps(message_content).encode(), client_info.udp_addr
                )

    def find_inactive_clients(self) -> list:
        clients_to_remove = []

        # 非アクティブクライアントを特定
        for client_info in self.client_infos:
            inactivity_threshold = 30
            if (
                time.time() - client_info.last_message_time > inactivity_threshold
            ):  # 30 seconds inactivity
                clients_to_remove.append(client_info)
                # ホストが非アクティブの場合そのルームに関連するすべてのクライアント（ホスト自身を含む）を削除するためのリストに追加
                if client_info.is_host:
                    clients_to_remove.extend(
                        [
                            client_info
                            for client_info in self.client_infos
                            if client_info not in clients_to_remove
                        ]
                    )
                    break

        return clients_to_remove

    def broadcast_removal_message(self, clients_to_remove, udp_socket):
        for client_info in clients_to_remove:
            if client_info.is_host:
                message = "You have been disconnected due to inactivity. Please rejoin the chat room."
            else:
                message = "Room has been closed due to host inactivity. You are also removed. Please rejoin the chat room."

            removal_msg = {
                "room_name": self.room_name,
                "username": "Server Message",
                "message": message,
            }
            udp_socket.sendto(json.dumps(removal_msg).encode(), client_info.udp_addr)

    def remove_clients(self, clients_to_remove):
        for client_info in clients_to_remove:
            self.client_infos.remove(client_info)


class ChatServer:
    def __init__(self):
        self.chat_rooms = {}  # {room_name: ChatRoom obj}
        self.tokens = {}  # {token: room_name}
        self.clients = {}  # {token: client_info}
        self.tcp_port = 12345
        self.udp_port = 12346

    def generate_token(self, size=10):
        """
        TODO: IPアドレスでトークンを作る
        """
        return "".join(
            random.choice(string.ascii_letters + string.digits) for _ in range(size)
        )

    # def generate_token(self, ip_address, size=10):
    #     """
    #     IPアドレスでトークンを作る
    #     """
    #     hashed = hashlib.sha256(ip_address.encode()).hexdigest()
    #     return hashed[:size]

    def check_for_inactive_clients(self):
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        while True:
            for chat_room in list(self.chat_rooms.values()):
                clients_to_remove = chat_room.find_inactive_clients()

                chat_room.broadcast_removal_message(clients_to_remove, udp_socket)

                self.remove_tokens_and_clients(clients_to_remove)

                chat_room.remove_clients(clients_to_remove)

                self.delete_room_if_empty(chat_room)

            time.sleep(10)
            print(self.chat_rooms)

    def remove_tokens_and_clients(self, clients_to_remove):
        for client_info in clients_to_remove:
            if client_info.access_token in self.tokens:
                del self.tokens[client_info.access_token]
            if client_info.access_token in self.clients:
                del self.clients[client_info.access_token]

    def delete_room_if_empty(self, chat_room):
        if not chat_room.client_infos:
            del self.chat_rooms[chat_room.room_name]

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

    def tcp_handler(self, conn, addr):
        try:
            """
            Chat_Room_Protocol: サーバの初期化(0)
            返り値: (room_name, operation_code, state, user_name)
            state: 正常なら1を返す
            """
            room_name, operation_code, state, user_name = self.tcp_server_init(
                conn, addr
            )

            """
            Chat_Room_Protocol: リクエストの応答(1)
            サーバはステータスコードを含むペイロードで即座に応答する
            返り値: (status, state)
            status:
                success: 部屋の作成に成功
                room already exists: すでに同じ名前の部屋が存在する
                not found room: 部屋が存在しない
                failed: 何らかのエラー
            state: 正常なら2を返す
            """
            status, state = self.respond_for_request(
                conn, room_name, operation_code, state
            )

            """
            Chat_Room_Protocol: リクエストの完了(2)
            サーバは特定の生成されたユニークなトークンをクライアントに送り、このトークンにユーザー名を割り当てる
            このトークンはクライアントをチャットルームのホストとして識別する。トークンは最大255バイト。
            TODO: 部屋の作成・参加を関数化
            TODO: TCRPでトークンを送信
            """
            if status == "success":
                # トークンを生成
                token = self.generate_token()
                # チャットルーム作成
                if operation_code == 1:
                    self.get_or_create_chat_room(room_name)

                    self.tokens[token] = room_name
                    # クライアント情報の作成(ホスト権限アリ)
                    client_info = ClientInfo(
                        tcp_addr=addr,
                        access_token=token,
                        username=user_name,
                        is_host=True,
                    )
                    # トークンにクライアント情報を割り当てる
                    self.clients[token] = client_info

                # チャットルーム参加
                elif operation_code == 2:
                    if room_name in self.chat_rooms:
                        self.tokens[token] = room_name
                        # クライアント情報作成(ホスト権限ナシ)
                        client_info = ClientInfo(
                            tcp_addr=addr, access_token=token, username=user_name
                        )
                        # トークンにユーザーを割り当てる
                        self.clients[token] = client_info

                # TODO: TCRPでトークンを送信
                conn.send(token.encode())

        except Exception as e:
            print(e)

        finally:
            conn.close()

    # サーバの初期化(0)
    def tcp_server_init(self, conn, addr) -> Tuple[str, int, int, str]:
        """
        Chat_Room_Protocol: サーバの初期化(0)
        Header(32): RoomNameSize(1) | Operation(1) | State(1) | OperationPayloadSize(29)
        Body: payload(room_name + user_name)
        """
        # ヘッダ受信
        header = conn.recv(32)

        # ヘッダから長さなどを抽出
        room_name_size = int.from_bytes(header[:1], "big")
        operation_code = int.from_bytes(header[1:2], "big")
        state = int.from_bytes(header[2:3], "big")
        json_string_payload_size = int.from_bytes(header[3:33], "big")
        """
            TODO: サーバー側バリデーション
            room_name room_name_size == 0
            user_name operation_payload_size == 0
            クライアントにエラーメッセージを返す。
        """

        room_name = conn.recv(room_name_size).decode()
        json_payload = json.loads(conn.recv(json_string_payload_size).decode())
        user_name = json_payload["user_name"]

        print(
            f"Received header from client."
            f"RoomNameSize: {room_name_size}, "
            f"Operation: {operation_code}, "
            f"State: {state}, "
            f"OperationPayloadSize: {json_string_payload_size}."
        )

        # TODO: stateのバリデーション（そもそもうまく使えてない）
        if state == 0:
            state = 1

        return (room_name, operation_code, state, user_name)

    # リクエストの応答(1)
    def respond_for_request(
        self, conn, room_name: str, operation_code: int, state: int
    ) -> Tuple[str, int]:
        status = "failed"

        if operation_code == 1 and state == 1:
            # もし既に同じルーム名があれば、不可
            if room_name in self.chat_rooms:
                status = "room already exists"
                message = f"すでに{room_name}が存在します"
                print(message)
            else:
                status = "success"
                message = "サーバから応答がありました"
                print(message)

        elif operation_code == 2 and state == 1:
            # もし既に同じ名前のチャットルームがないと、不可
            if room_name not in self.chat_rooms:
                status = "not found room"
                message = f"{room_name}は見つかりませんでした"
                print(message)
            else:
                status = "success"
                message = "サーバから応答がありました"
                print(message)
        else:
            message = "何らかのエラーが発生しました"
            print(message)

        state = 2
        operation_payload = {"status": status, "message": message}

        room_name_bits = room_name.encode()
        operation_payload_bits = json.dumps(operation_payload).encode()

        # ヘッダ作成
        header = self.tcp_chat_room_protocol_header(
            len(room_name_bits), operation_code, state, len(operation_payload_bits)
        )
        # ボディ作成
        body = room_name_bits + operation_payload_bits

        conn.send(header)
        conn.send(body)

        return (status, state)

    def udp_handler(self):
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.bind(("0.0.0.0", self.udp_port))

        while True:
            # クライアントからメッセージを受け取る
            addr, token, user_name, room_name, message = self.udp_receive_messages(
                udp_socket
            )

            if token in self.tokens:
                user_name = self.clients[token].username
                self.clients[token].udp_addr = addr
                self.clients[token].last_message_time = time.time()

                # サーバー側でメッセージを表示
                print(f"[{room_name} - {addr}] {user_name} says: {message}")

                # メッセージにルーム名とユーザー名を付け加える
                message_content = {
                    "room_name": room_name,
                    "username": user_name,
                    "message": message,
                }

                chat_room = self.get_or_create_chat_room(room_name)

                current_client = self.clients[token]
                chat_room.add_client_info_if_not_exists(current_client)

                chat_room.broadcast_message_to_clients(
                    addr, udp_socket, message_content
                )

    def get_or_create_chat_room(self, room_name) -> ChatRoom:
        if room_name in self.chat_rooms:
            return self.chat_rooms[room_name]
        else:
            chat_room = ChatRoom(room_name)
            self.chat_rooms[room_name] = chat_room
            return chat_room

    def udp_receive_messages(self, udp_socket):
        data, addr = udp_socket.recvfrom(4096)
        # ヘッダ(2bytes) + ボディ(max 4096bytes)
        header = data[:2]
        body = data[2:]
        # ヘッダから長さなど抽出
        json_size = int.from_bytes(header[:2], "big")

        message_dict = json.loads(body.decode())
        token = message_dict["token"]
        user_name = message_dict["user_name"]
        room_name = message_dict["room_name"]
        message = message_dict["message"]

        return (addr, token, user_name, room_name, message)

    def start(self):
        # TCPソケットの作成
        tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # バインド
        tcp_server.bind(("0.0.0.0", self.tcp_port))
        # クライアントからの接続待ち
        tcp_server.listen(5)

        # UDP
        threading.Thread(target=self.udp_handler).start()
        threading.Thread(target=self.check_for_inactive_clients).start()

        while True:
            # TCP クライアントからの接続受付
            conn, addr = tcp_server.accept()
            # サブスレッド化
            threading.Thread(target=self.tcp_handler, args=(conn, addr)).start()


if __name__ == "__main__":
    server = ChatServer()
    server.start()
