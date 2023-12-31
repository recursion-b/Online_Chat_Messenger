# client
import socket
import threading
from typing import Tuple
import json
import tkinter as tk
from tkinter import messagebox
import tkinter.ttk as ttk
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
import base64


class ChatClient:
    def __init__(self):
        # self.server_address = "127.0.0.1"
        self.server_address = self.get_ip_address()
        self.tcp_port = 12345
        self.udp_port = 12346
        self.address = (self.server_address, self.udp_port)
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # UDPバインド
        self.udp_socket.bind(("0.0.0.0", 0))
        self.token = ""
        self.user_name = ""
        self.room_name = ""
        self.operation_code = 0  # Noneにしないための仮の数字
        self.state = 0
        self.private_key = None
        self.public_key = None
        self.server_public_key = None

    def get_ip_address(self):
        host = socket.gethostname()
        ip = socket.gethostbyname(host)
        return ip

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
            self.state = 0
            self.tcp_send_data(json_payload)

        except Exception as e:
            print(f"Error: {e} from initialize_tcp_connection")
            self.state = 0
            self.tcp_socket.close()
            exit(1)

    def receive_request_result(self) -> None:
        try:
            """
            チャットルームプロトコル
            リクエストの応答(1): サーバからステータスコードを含むペイロードで即座に応答を受け取る
            state: 正常なら1
            payload: (stauts, message)
            status:
                success: 部屋の作成に成功
                room already exists: すでに同じ名前の部屋が存在する
                not found room: 部屋が存在しない
                failed: 何らかのエラー
            message: メッセージ
            """
            room_name, operation_code, state, json_payload = self.tcp_receive_data()

            if state == 1:
                # stateの更新
                self.state = state
            else:
                print("Server did not respond properly.")
                self.state = 0
                self.tcp_socket.close()
                exit(1)

            status = json_payload["status"]
            message = json_payload["message"]

            if status != "success":
                print(message)
                self.tcp_socket.close()
                exit(1)

            print(message)

        except Exception as e:
            print(f"Error: {e} from receive_request_result")
            self.state = 0
            self.tcp_socket.close()
            exit(1)

    def receive_token_and_public_key(self):
        try:
            room_name, operation_code, state, json_payload = self.tcp_receive_data()

            if state == 2:
                # stateの更新
                self.state = state
            else:
                print("Server did not respond properly.")
                self.tcp_socket.close()
                exit(1)

            token = json_payload["token"]
            server_public_key_base64 = json_payload["public_key"]

        except Exception as e:
            print(f"Error: {e} from receive_token")
            self.state = 0
            exit(1)
        finally:
            self.tcp_socket.close()

        self.set_token(token)

        server_public_key = self.base64_to_bytes(server_public_key_base64)
        self.set_server_public_key(server_public_key)

    def set_token(self, token):
        self.token = token

    def set_server_public_key(self, server_public_key):
        self.server_public_key = server_public_key

    def udp_receive_messages(self):
        while True:
            message, addr = self.udp_socket.recvfrom(4096)
            try:
                # メッセージからルーム名、ユーザー名、メッセージを取り出す
                data = json.loads(message.decode())
                room_name = data["room_name"]
                username = data["username"]
                encrypted_message = data["message"]
                decrypted_message = self.decrypt_message(encrypted_message)

                print(
                    f"\nRoom -> {room_name}| Sender -> {username} says: {decrypted_message}"
                )
            except json.decoder.JSONDecodeError:
                print("Received an invalid message format.")
            except KeyError as e:
                print(
                    f"Key error: {e}. The received message does not have the expected format."
                )

    def decrypt_message(self, encrypted_message) -> str:
        enc_session_key = self.base64_to_bytes(encrypted_message["enc_session_key"])
        nonce = self.base64_to_bytes(encrypted_message["nonce"])
        tag = self.base64_to_bytes(encrypted_message["tag"])
        ciphertext = self.base64_to_bytes(encrypted_message["ciphertext"])

        # 秘密鍵でセッションキーを復号化
        cipher_rsa = PKCS1_OAEP.new(RSA.import_key(self.private_key))
        session_key = cipher_rsa.decrypt(enc_session_key)

        # AESセッションキーでデータを復号化
        cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
        message = cipher_aes.decrypt_and_verify(ciphertext, tag)
        return message.decode()

    def base64_to_bytes(self, encoded_str) -> bytes:
        return base64.b64decode(encoded_str)

    def udp_send_messages(
        self,
        message: dict,
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

    def prompt_and_validate_password(self) -> str:
        # パスワードの文字数制限は必要かもしれない
        prompt_message = (
            "Please set the room password."
            if self.operation_code == 1
            else "Please enter the room password."
        )
        print(prompt_message)

        while True:
            password = input("Enter password: ")

            if len(password) <= 0:
                print("The Password is required.")
            else:
                return password

    def encrypt_message(self, message) -> dict:
        # セッションキーを作成
        session_key = get_random_bytes(16)

        # RSAキーでセッションキーを暗号化
        cipher_rsa = PKCS1_OAEP.new(RSA.import_key(self.server_public_key))
        enc_session_key = cipher_rsa.encrypt(session_key)

        # AESセッションキーでdataを暗号化
        cipher_aes = AES.new(session_key, AES.MODE_EAX)
        ciphertext, tag = cipher_aes.encrypt_and_digest(message.encode())
        nonce = cipher_aes.nonce

        encrypted_message = {
            "enc_session_key": self.bytes_to_base64(enc_session_key),
            "nonce": self.bytes_to_base64(nonce),
            "tag": self.bytes_to_base64(tag),
            "ciphertext": self.bytes_to_base64(ciphertext),
        }

        return encrypted_message

    def bytes_to_base64(self, bytes) -> str:
        return base64.b64encode(bytes).decode()

    def generate_and_set_keys(self):
        key = RSA.generate(2048)
        private_key = key.export_key()
        public_key = key.publickey().export_key()
        self.private_key = private_key
        self.public_key = public_key

    def start(self):
        self.user_name = self.prompt_and_validate_user_name()
        self.operation_code = int(self.prompt_and_validate_operation_code())
        self.room_name = self.prompt_and_validate_room_name()
        self.password = self.prompt_and_validate_password()

        # 公開鍵と秘密鍵を生成、メンバ変数にセット
        self.generate_and_set_keys()

        json_payload = {
            "user_name": self.user_name,
            "password": self.password,
            "public_key": self.bytes_to_base64(self.public_key),
        }

        # TCP接続
        self.initialize_tcp_connection(json_payload)

        # レスポンスの応答
        self.receive_request_result()

        # トークンと公開鍵の受け取り
        self.receive_token_and_public_key()

        # トークン取得後,自動的にUDPへ接続
        first_message = (
            f"{self.user_name} created {self.room_name}."
            if self.operation_code == 1
            else f"{self.user_name} joined."
        )
        encrypted_first_message = self.encrypt_message(first_message)
        self.udp_send_messages(encrypted_first_message)

        # 受信用のスレッドを開始
        threading.Thread(target=self.udp_receive_messages).start()

        while True:
            message = input("Your message: ")
            encrypted_message = self.encrypt_message(message)
            self.udp_send_messages(encrypted_message)

    """
    Tkinter用メソッド
    """

    def initialize_tcp_connection_for_Tkinter(
        self,
        json_payload: dict,
    ) -> None:
        try:
            # TkinterでTCP接続に失敗した場合は、新たにTCPソケットを作成する必要がある
            self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.state = 0
            self.tcp_send_data(json_payload)

        except Exception as e:
            print(f"Error: {e} from initialize_tcp_connection")
            self.state = 0
            self.tcp_socket.close()
            exit(1)

    def receive_request_result_for_tkinter(self) -> Tuple[str, str]:
        try:
            room_name, operation_code, state, json_payload = self.tcp_receive_data()

            if state == 1:
                # stateの更新
                self.state = state
            else:
                self.state = 0
                print("Server did not respond properly.")
                return ("failed", "Server did not respond properly.")

            status = json_payload["status"]
            message = json_payload["message"]

            return (status, message)

        except Exception as e:
            print(f"Error: {e} from receive_request_result")
            self.state = 0
            return ("failed", f"Error: {e} from receive_request_result_for_tkinter")


class Tkinter:
    def __init__(self):
        self.chat_client = ChatClient()

        self.root = tk.Tk()
        self.root.title("Chat Client Setup")
        self.root.geometry("600x800")

        self.frame_user_info = ttk.Frame(self.root)
        self.frame_user_info.pack(pady=20)
        self.setup_user_info_gui()

        self.root.mainloop()

    def setup_user_info_gui(self):
        # ユーザー名入力
        self.username_label = ttk.Label(self.frame_user_info, text="Username:")
        self.username_label.pack(pady=5)
        self.username_entry = ttk.Entry(self.frame_user_info, width=50)
        self.username_entry.pack(pady=5)

        # ルーム名入力
        self.roomname_label = ttk.Label(self.frame_user_info, text="Room Name:")
        self.roomname_label.pack(pady=5)
        self.roomname_entry = ttk.Entry(self.frame_user_info, width=50)
        self.roomname_entry.pack(pady=5)

        # Radio buttons for Create or Join
        self.operation_code_value = tk.IntVar()  # Default is set to "1"
        self.operation_code_value.set(1)
        ttk.Label(self.frame_user_info, text="Choose an operation:").pack(pady=5)
        ttk.Radiobutton(
            self.frame_user_info,
            text="Create",
            variable=self.operation_code_value,
            value=1,
        ).pack(pady=2)
        ttk.Radiobutton(
            self.frame_user_info,
            text="Join",
            variable=self.operation_code_value,
            value=2,
        ).pack(pady=2)

        send_button = ttk.Button(
            self.frame_user_info, text="Send", command=self.on_send
        )
        send_button.pack(pady=10)

    def render_chat_room_gui(self):
        # uesr_info_guiを削除
        self.frame_user_info.destroy()

        self.frame_chat_room = ttk.Frame(self.root)
        self.frame_chat_room.pack(fill=tk.BOTH)

        header_frame = ttk.Frame(self.frame_chat_room)
        header_frame.pack(pady=10, fill=tk.X)

        # TODO: Leave Room Button
        # leave_room_button = ttk.Button(
        #     header_frame,
        #     text="Back",
        #     command=self.go_back_user_unfo_and_disconnect_udp,
        # )
        # leave_room_button.pack(pady=10, side=tk.LEFT)

        roomname_label = ttk.Label(
            header_frame, text=f"Room Name: {self.chat_client.room_name}"
        )
        roomname_label.pack(pady=5)
        # User name
        username_label = ttk.Label(
            header_frame, text=f"Username: {self.chat_client.user_name}"
        )
        username_label.pack(pady=5, side=tk.TOP)
        # Message List
        self.messages_frame = ttk.Frame(self.frame_chat_room)
        self.messages_scrollbar = ttk.Scrollbar(self.messages_frame)
        self.messages_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.messages_listbox = tk.Listbox(
            self.messages_frame, yscrollcommand=self.messages_scrollbar.set
        )
        self.messages_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.messages_scrollbar.config(command=self.messages_listbox.yview)
        self.messages_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # message Input
        self.message_frame = ttk.Frame(self.frame_chat_room)
        self.message_frame.pack(pady=10, fill=tk.X)
        self.message_entry = ttk.Entry(self.message_frame)  # メッセージ入力欄
        self.message_entry.pack(pady=5, side=tk.LEFT, expand=True, fill=tk.X)

        send_button2 = ttk.Button(
            self.message_frame, text="Send", command=self.send_user_message
        )  # メッセージフレームに追加
        send_button2.pack(pady=10, side=tk.RIGHT)

        threading.Thread(
            target=self.udp_receive_messages_for_Tkinter, daemon=True
        ).start()

    def show_message_box(self, message: str):
        messagebox.showerror("Error", message)

    def is_valid_user_name(self):
        user_name = self.username_entry.get().strip()
        max_bytes_in_user_name = 255

        if len(user_name.encode()) > max_bytes_in_user_name:
            error_message = "The username exceeds the maximum character limit."
            print(error_message)
            self.show_message_box(error_message)
            return False

        elif len(user_name) <= 0:
            error_message = "Username is required."
            print(error_message)
            self.show_message_box(error_message)
            return False

        return True

    def is_valid_operation_code(self):
        operation_code = self.operation_code_value.get()

        if operation_code == 1 or operation_code == 2:
            return True

        else:
            error_message = "Invalid input."
            print(error_message)
            return False

    def is_valid_room_name(self):
        room_name = self.roomname_entry.get().strip()
        max_bytes_in_room_name = 255

        if len(room_name.encode()) > max_bytes_in_room_name:
            error_message = "The roomname exceeds the maximum character limit."
            print(error_message)
            self.show_message_box(error_message)
            return False

        elif len(room_name) <= 0:
            error_message = "Roomname is required."
            print(error_message)
            self.show_message_box(error_message)
            return False

        return True

    def on_send(self):
        if (
            self.is_valid_user_name()
            and self.is_valid_operation_code()
            and self.is_valid_room_name()
        ):
            self.chat_client.user_name = self.username_entry.get().strip()
            self.chat_client.operation_code = self.operation_code_value.get()
            self.chat_client.room_name = self.roomname_entry.get().strip()

            self.chat_client.generate_and_set_keys()

            # TCP接続開始
            json_payload = {
                "user_name": self.chat_client.user_name,
                "password": "test_dummy",
                "public_key": self.chat_client.bytes_to_base64(
                    self.chat_client.public_key
                ),
            }

            self.chat_client.initialize_tcp_connection_for_Tkinter(json_payload)

            # レスポンスの応答結果とトークンの受け取り
            status, message = self.chat_client.receive_request_result_for_tkinter()

            if status == "success":
                print(message)

                self.chat_client.receive_token_and_public_key()

                if self.chat_client.token == None:
                    self.messages_listbox.insert(
                        tk.END, "Server did not respond properly."
                    )

                else:
                    # 自動的にUDP接続
                    first_message = (
                        f"{self.chat_client.user_name} created {self.chat_client.room_name}."
                        if self.chat_client.operation_code == 1
                        else f"{self.chat_client.user_name} joned {self.chat_client.room_name}."
                    )
                    encrypted_first_message = self.chat_client.encrypt_message(
                        first_message
                    )
                    self.chat_client.udp_send_messages(encrypted_first_message)
                    # ページ遷移
                    self.render_chat_room_gui()
                    self.messages_listbox.insert(tk.END, first_message)

            else:
                print(message)
                self.chat_client.tcp_socket.close()
                self.show_message_box(message)

    def udp_receive_messages_for_Tkinter(self):
        while True:
            message, addr = self.chat_client.udp_socket.recvfrom(4096)
            try:
                data = json.loads(message.decode())
                room_name = data["room_name"]
                username = data["username"]
                encrypted_message = data["message"]
                decrypted_message = self.chat_client.decrypt_message(encrypted_message)

                display_message = f"{username} says: {decrypted_message}"
                self.messages_listbox.insert(tk.END, display_message)
            except json.decoder.JSONDecodeError:
                display_message = "Received an invalid message format."
                self.messages_listbox.insert(tk.END, display_message)
            except KeyError as e:
                display_message = f"Key error: {e}. The received message does not have the expected format."
                self.messages_listbox.insert(tk.END, display_message)

    def send_user_message(self):
        user_message = self.message_entry.get().strip()
        encrypt_message = self.chat_client.encrypt_message(user_message)
        user_name = self.chat_client.user_name

        self.chat_client.udp_send_messages(encrypt_message)
        formatted_message = f"{user_name} says: {user_message}"
        self.messages_listbox.insert(tk.END, formatted_message)

        # 送信後にメッセージ入力欄をクリア
        self.message_entry.delete(0, tk.END)


def prompt_useage():
    while True:
        usage = input("use CLI(1) or Desktop(2) ? ")
        if usage == "1" or usage == "2":
            return usage
        else:
            print("Please enter 1 or 2.")


if __name__ == "__main__":
    usage = prompt_useage()

    if usage == "1":
        client = ChatClient()
        client.start()
    elif usage == "2":
        Tkinter()
