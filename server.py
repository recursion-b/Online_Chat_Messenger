import socket


class Server:
    def __init__(self):
        self.__SERVER_ADDRESS = "0.0.0.0"
        self.__SERVER_PORT = 9001
        self.__MAX_MESSAGE_SIZE = 4096
        self.clients = {}
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((self.__SERVER_ADDRESS, self.__SERVER_PORT))

    def standby(self):
        print("チャットサーバーがスタートしました。")

        while True:
            data, client_address = self.server_socket.recvfrom(self.__MAX_MESSAGE_SIZE)
            message = data.decode("utf-8")

            if client_address not in self.clients:
                client_name = message
                self.clients[client_address] = client_name
                print(f"{client_name}がチャットに参加しました")
            else:
                print(f"受信したメッセージ)({client_address}):{message}")

                for client, _ in self.clients.items():
                    if client != client_address:
                        self.server_socket.sendto(
                            f"{self.clients[client_address]}: {message}".encode(),
                            client,
                        )


class Main:
    server = Server()
    server.standby()


if __name__ == "__main__":
    Main()
