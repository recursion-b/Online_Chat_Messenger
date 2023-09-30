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


class ChatServer:
    def __init__(self):
        self.chat_rooms = {}
        self.tokens = {}
        self.clients = {}
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
            for room_name, client_infos in list(self.chat_rooms.items()): 
                clients_to_remove = []

                # 非アクティブクライアントを特定
                for client_info in client_infos:
                    if (time.time() - client_info.last_message_time > 30):  # 30 seconds inactivity
                        clients_to_remove.append(client_info)
                        # ホストが非アクティブの場合そのルームに関連するすべてのクライアント（ホスト自身を含む）を削除するためのリストに追加
                        if client_info.is_host: 
                            clients_to_remove.extend([ci for ci in client_infos if ci not in clients_to_remove])
                            break

                # 実際に削除とその通知を行っていく処理
                for client_info in clients_to_remove:
                    if client_info.is_host:
                        message = "You have been disconnected due to inactivity. Please rejoin the chat room."
                    else:
                        message = "Room has been closed due to host inactivity. You are also removed. Please rejoin the chat room."
                    
                    removal_msg = {
                        "room_name": room_name,
                        "username": "Server Message",
                        "message": message,
                    }
                    udp_socket.sendto(json.dumps(removal_msg).encode(), client_info.udp_addr)

                    # Remove the token from tokens list and clients list
                    if client_info.access_token in self.tokens:
                        del self.tokens[client_info.access_token]
                    if client_info.access_token in self.clients:
                        del self.clients[client_info.access_token]

                    # Remove the client from the client_infos list
                    client_infos.remove(client_info)

                # If the room has no clients, delete it
                if not client_infos:
                    del self.chat_rooms[room_name]

            time.sleep(10)
            print(self.chat_rooms)


    def tcp_handler(self, conn, addr):
        # Chat_Room_Protocol: サーバの初期化(0)
        room_name, operation_code, state, user_name = self.tcp_server_init(conn, addr)

        """
        チャットルームプロトコル
        リクエストの応答(1): サーバはステータスコードを含むペイロードで即座に応答する
        """
        state = 1
        status = "success"
        room_name_bits = room_name.encode()
        operation_payload_bits = status.encode()

        header = self.tcp_chat_room_protocol_header(
            len(room_name_bits), operation_code, state, len(operation_payload_bits)
        )

        body = room_name_bits + operation_payload_bits

        conn.send(header)

        conn.send(body)

        """
        TODO: チャットルームプロトコル
        リクエストの完了(2): サーバは特定の生成されたユニークなトークンをクライアントに送り、このトークンにユーザー名を割り当てる
        このトークンはクライアントをチャットルームのホストとして識別する。トークンは最大255バイト。
        """
        # チャットルーム作成
        if operation_code == 1:
            # chatroomsにroom_nameが存在しなければ、新しくroomを作成
            if room_name not in self.chat_rooms:
                self.chat_rooms[room_name] = []
            # トークンを生成
            token = self.generate_token()
            self.tokens[token] = room_name
            # クライアント情報の作成(ホスト権限アリ)
            client_info = ClientInfo(tcp_addr=addr, access_token=token, is_host=True)
            # トークンにクライアント情報を割り当てる
            self.clients[token] = client_info
            conn.send(token.encode())

        # TODO: 指定したチャットルーム名がない場合の処理

        # チャットルーム参加
        elif operation_code == 2:
            if room_name in self.chat_rooms:
                token = self.generate_token()
                self.tokens[token] = room_name
                # クライアント情報作成(ホスト権限ナシ)
                client_info = ClientInfo(tcp_addr=addr, access_token=token)
                # トークンにユーザーを割り当てる
                self.clients[token] = client_info
                # クライアントにトークン送信
                conn.send(token.encode())
            else:
                conn.send("ERROR".encode())

        conn.close()

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
        operation_payload_size = int.from_bytes(header[3:33], "big")

        print(
            f"Received header from client."
            f"RoomNameSize: {room_name_size}, "
            f"Operation: {operation_code}, "
            f"State: {state}, "
            f"OperationPayloadSize: {operation_payload_size}."
        )

        """
        TODO: サーバー側バリデーション
        room_name room_name_size == 0
        user_name operation_payload_size == 0
        クライアントにエラーメッセージを返す。
        """

        room_name = conn.recv(room_name_size).decode()
        print(f"Room name: {room_name}")
        user_name = conn.recv(operation_payload_size).decode()
        print(f"User name: {user_name}")

        return (room_name, operation_code, state, user_name)

    def udp_handler(self):
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.bind(("0.0.0.0", self.udp_port))

        while True:
            data, addr = udp_socket.recvfrom(4096)
            message_dict = json.loads(data.decode())

            token = message_dict["token"]
            username = message_dict["username"]
            message = message_dict["message"]

            if token in self.tokens:
                room_name = self.tokens[token]
                self.clients[token].udp_addr = addr
                self.clients[token].username = username
                self.clients[token].last_message_time = time.time()

                # サーバー側でメッセージを表示
                print(f"[{room_name} - {addr}] {username} says: {message}")

                # メッセージにルーム名とユーザー名を付け加える
                message_content = {
                    "room_name": room_name,
                    "username": username,
                    "message": message,
                }

                if room_name not in self.chat_rooms:
                    self.chat_rooms[room_name] = []

                current_client = self.clients[token]
                if current_client not in self.chat_rooms[room_name]:
                    self.chat_rooms[room_name].append(current_client)

                for client_info in self.chat_rooms[room_name]:
                    if client_info.udp_addr != addr:
                        udp_socket.sendto(
                            json.dumps(message_content).encode(), client_info.udp_addr
                        )

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
