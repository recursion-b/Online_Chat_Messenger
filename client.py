import socket
import threading
import asyncio

SERVER_ADDRESS = "localhost"
SERVER_PORT = 9001

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

client_name = input("名前を入力してください：")
client_socket.sendto(client_name.encode(), (SERVER_ADDRESS, SERVER_PORT))


def receive_messages():
    while True:
        message, _ = client_socket.recvfrom(4096)
        message = message.decode("utf-8")
        print(f"\nFROM {message}")
        print("メッセージを入力してください：")


receive_thread = threading.Thread(target=receive_messages)
receive_thread.start()


async def send_messages():
    while True:
        message = await asyncio.to_thread(input, "メッセージを入力してください：")
        client_socket.sendto(message.encode("utf-8"), (SERVER_ADDRESS, SERVER_PORT))
        print("メッセージを送信しました。")


asyncio.run(send_messages())

receive_thread.join()
client_socket.close()
