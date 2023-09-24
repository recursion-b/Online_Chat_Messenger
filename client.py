import socket
import threading
import time
import sys


class Client:
    def __init__(self):
        self.__SERVER_ADDRESS = "localhost"
        self.__SERVER_PORT = 9001
        self.__MAX_USERNAME_BYTE = 255
        self.__TIME_LIMIT = 60
        self.LAST_ACTIVITY_TIME = 0

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def enter_client_name(self):
        while True:
            client_name = input("名前を入力してください：")
            if len(client_name.encode()) > self.__MAX_USERNAME_BYTE:
                print("ユーザー名は255バイト以内で入力してください")
            elif len(client_name.encode()) == 0:
                print("ユーザー名を入力してください")
            else:
                self.client_socket.sendto(
                    client_name.encode(), (self.__SERVER_ADDRESS, self.__SERVER_PORT)
                )
                self.LAST_ACTIVITY_TIME = time.time()
                print("チャットルームに参加しました。")
                break

    def receive_messages(self):
        while True:
            message, _ = self.client_socket.recvfrom(4096)
            message = message.decode("utf-8")
            print(f"\nFROM {message}")

    def send_messages(self):
        while True:
            message = input()
            if message == "exit":
                print("チャットルームを退出しました。")
                break
            else:
                self.client_socket.sendto(
                    message.encode("utf-8"), (self.__SERVER_ADDRESS, self.__SERVER_PORT)
                )
                self.LAST_ACTIVITY_TIME = time.time()

    def check_timeout(self):
        while True:
            current_time = time.time()
            if current_time - self.LAST_ACTIVITY_TIME > self.__TIME_LIMIT:
                break
            time.sleep(10)

    def exit(self):
        print("接続を切断します。")
        self.client_socket.close()
        sys.exit()


class Main:
    client = Client()
    clientname_thread = threading.Thread(target=client.enter_client_name)
    clientname_thread.start()
    clientname_thread.join()

    receive_message_thread = threading.Thread(target=client.receive_messages)
    receive_message_thread.start()

    send_message_thread = threading.Thread(target=client.send_messages)
    send_message_thread.start()

    timeout_thread = threading.Thread(target=client.check_timeout)
    timeout_thread.start()

    timeout_thread.join()
    client.exit()


if __name__ == "__main__":
    Main()
