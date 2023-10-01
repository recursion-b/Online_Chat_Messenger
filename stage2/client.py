# client
import socket
import threading
from typing import Tuple
import json
import tkinter as tk
import threading


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

    def udp_chat_message_protocol_header(self, json_size: int) -> bytes:
        return json_size.to_bytes(2, "big")

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
        print(token)
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

    def udp_send_messages(
        self,
        udp_socket,
        udp_address: Tuple[str, int],
        token: str,
        user_name: str,
        room_name: str,
        message: str,
    ):
        full_content = {
            "token": token,
            "user_name": user_name,
            "room_name": room_name,
            "message": message,
        }

        full_content_bits = json.dumps(full_content).encode()

        # UDPヘッダの作成(2bytes)
        header = self.udp_chat_message_protocol_header(len(full_content_bits))

        # UDPボディの作成(max 4096bytes)
        body = full_content_bits

        udp_socket.sendto(header + body, udp_address)

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
        # UDPソケットの作成
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # バインド
        udp_socket.bind(("0.0.0.0", 0))

        user_name = self.prompt_and_validate_user_name()
        operation_code = self.prompt_and_validate_operation_code()
        room_name = self.prompt_and_validate_room_name()

        # TODO: token受け取りに失敗した場合のエラーハンドリング
        token = self.initialize_tcp_connection(
            room_name, int(operation_code), 0, user_name
        )

        address = (self.server_address, self.udp_port)

        # トークン取得後に自動的にUDPへ接続
        first_message = (
            f"{user_name}がルームを作成しました" if operation_code == 1 else f"{user_name}が参加しました"
        )
        self.udp_send_messages(
            udp_socket, address, token, user_name, room_name, first_message
        )

        # トークンの取得後に受信用のスレッドを開始
        threading.Thread(target=self.udp_receive_messages, args=(udp_socket,)).start()

        while True:
            message = input("Your message: ")

            self.udp_send_messages(
                udp_socket, address, token, user_name, room_name, message
            )

    def Tkinter_Start(self):
        # 送信ボタン
        def on_send():
            user_name = username_entry.get().strip()
            room_name = roomname_entry.get().strip()
            operation_code = operation_code_value.get()
            
            # TODO: token受け取りに失敗した場合のエラーハンドリング
            token = self.initialize_tcp_connection(
                room_name, int(operation_code), 0, user_name
            )

            address = (self.server_address, self.udp_port)
            first_message = (
                f"{user_name}がルームを作成しました" if operation_code == 1 else f"{user_name}が参加しました"
            )
            self.udp_send_messages(
                udp_socket, address, token, user_name, room_name, first_message
            )
        # UDPソケットの作成
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # バインド
        udp_socket.bind(("0.0.0.0", 0))

        root = tk.Tk()
        root.title("Chat Client Setup")
        root.geometry("600x400")

        # ユーザー名入力
        username_label = tk.Label(root, text="Username:")
        username_label.pack(pady=5)
        username_entry = tk.Entry(root, width=50)
        username_entry.pack(pady=5)

        # ルーム名入力
        roomname_label = tk.Label(root, text="Room Name:")
        roomname_label.pack(pady=5)
        roomname_entry = tk.Entry(root, width=50)
        roomname_entry.pack(pady=5)

       # Radio buttons for Create or Join
        operation_code_value = tk.IntVar()# Default is set to "1"
        tk.Label(root, text="Choose an operation:").pack(pady=5)
        tk.Radiobutton(root, text="Create", variable=operation_code_value, value=1).pack(anchor=tk.W)
        tk.Radiobutton(root, text="Join", variable=operation_code_value, value=2).pack(anchor=tk.W)
        send_button = tk.Button(root, text="Send", command=on_send)
        send_button.pack(pady=10, side=tk.RIGHT)

        def udp_receive_messages_for_Tkinter(udp_socket,messages_listbox):
            while True:
                message, addr = udp_socket.recvfrom(4096)
                try:
                    # メッセージからルーム名、ユーザー名、メッセージを取り出す
                    data = json.loads(message.decode())
                    room_name = data["room_name"]
                    username = data["username"]
                    msg = data["message"]
                    display_message = f"\nRoom -> {room_name}| Sender -> {username} says: {msg}"
                    messages_listbox.insert(tk.END, display_message)
                except json.decoder.JSONDecodeError:
                    display_message = "Received an invalid message format."
                    messages_listbox.insert(tk.END, display_message)
                except KeyError as e:
                   display_message = f"Key error: {e}. The received message does not have the expected format."
                   messages_listbox.insert(tk.END, display_message)
            # トークンの取得後に受信用のスレッドを開始
            # root.destroy()  # ダイアログを閉じる
        # send_button = tk.Button(root, text="Send", command=on_send)
        # send_button.pack(pady=10, side=tk.RIGHT)
        messages_frame = tk.Frame(root)
        messages_scrollbar = tk.Scrollbar(messages_frame)
        messages_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        messages_listbox = tk.Listbox(messages_frame, yscrollcommand=messages_scrollbar.set)
        messages_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        messages_scrollbar.config(command=messages_listbox.yview)
        messages_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        message_frame = tk.Frame(root)
        message_frame.pack(pady=10, fill=tk.X)
        message_entry = tk.Entry(message_frame)  # メッセージ入力欄
        message_entry.pack(pady=5, side=tk.LEFT, expand=True, fill=tk.X)
        def send_user_message():
            user_message = message_entry.get().strip()  # 入力欄からメッセージを取得

            # 以下の部分を、UDPでメッセージを送信するコードで置き換える
            # 必要な情報（例: username, roomname, tokenなど）は前の部分で取得したものを利用できる
            user_name = username_entry.get().strip()
            room_name = roomname_entry.get().strip()
            address = (self.server_address, self.udp_port)
            token = self.initialize_tcp_connection(
                room_name, int("1"), 0, user_name
            )

            address = (self.server_address, self.udp_port)
            # UDPでメッセージを送信するためのコードをここに追加
            self.udp_send_messages(udp_socket, address, token, user_name, room_name, user_message)

            # 送信後にメッセージ入力欄をクリア
            message_entry.delete(0, tk.END)
        
        send_button2 = tk.Button(message_frame, text="Send", command=send_user_message)  # メッセージフレームに追加
        send_button2.pack(pady=10, side=tk.RIGHT)
        threading.Thread(target=udp_receive_messages_for_Tkinter, args=(udp_socket,messages_listbox)).start()

        root.mainloop()



if __name__ == "__main__":
    client = ChatClient()
    # client.start()
    client.Tkinter_Start()

