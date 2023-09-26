import socket
import threading

class Client:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.username = ''
        self.server_address = '127.0.0.1'
        self.server_port = 8000  
        self.address = ''
        self.port = 9000
        self.max_buffer = 4096
        
        server_alive = self.is_server_alive()
        
        if server_alive:
            # サーバーが起動しているのでsettimeoutをリセットする
            self.sock.settimeout(None)
            self.tcp_sock.connect((self.server_address, self.server_port))
            self.set_username()
            # self.choice_menu()
            self.startChat()
        else:
            print('サーバーと接続できませんでした。')
            self.sock.close()
        
    def is_server_alive(self):
        print('サーバーとの接続を開始します...')
        try:
            message = 'ping'
            packet = self.protocol_sending(message)
            self.sock.sendto(packet,(self.server_address,self.server_port))

            timeout = 1
            self.sock.settimeout(timeout)
            data, address = self.sock.recvfrom(self.max_buffer)
            decoded_data = self.protocol_receiving(data)
            message = decoded_data[1]
            
            if message == 'ping':
                return True
            else:
                return False
            
        except OSError:
            return False
        
    def startChat(self):
        send_thread = threading.Thread(target=self.send)
        receive_thread = threading.Thread(target=self.receive)
        send_thread.start()
        receive_thread.start()
    
    def protocol_sending(self, message):
        usernamelen = len(self.username.encode())
            
        # packetが4096を超えていないかチェックするバリデーターが必要？
        packet = bytes([usernamelen]) + self.username.encode() + message.encode()
        
        return packet
    
    # (username, message)のtupleを返す
    def protocol_receiving(self, data):
        usernamelen = data[0]
        username_data = data[1:1 + usernamelen]
        username = username_data.decode()
        message = data[1 + usernamelen: ].decode()
            
        return (username, message)
    
    def send(self):
        print('\nチャットを開始します。')
        
        while True:
            message = input()
            packet =  self.protocol_sending(message)
            
            self.sock.sendto(packet, (self.server_address, self.server_port))
        
    
    def set_username(self):
        max_username_byte = 255
        
        while True:
            username = input('\nユーザー名を入力してください。\n\nusername: ')
            
            if len(username.encode()) > max_username_byte:
                print('ユーザー名の最大文字数を超えています。\n')
                
            elif len(username) <= 0:
                print('ユーザー名は必須です。\n')
            else:
                self.username = username
                break
    
    def receive(self):
        while True:
            data, address = self.sock.recvfrom(self.max_buffer)
            decoded_data = self.protocol_receiving(data)
            username = decoded_data[0]
            message = decoded_data[1]
            
            print(f'\n{username}: {message}')
            
    def choice_menu(self):
        while True:
            print('\n希望するメニューを入力してEnterを押してください。')
            print('\n1:新しいチャットルームを作成する。2:既存のチャットルームに参加する')
            choice = input('\n-> ')

            if choice == '1':
                print('新しいチャットルームを作成します。作成したいチャットルームの名前を入力してください。')
                room_name = input('Chat Room Name: ')
                room_name_bytes = room_name.encode()
                username_bytes = self.username.encode()
                
                header = self.tcrp_header(len(room_name_bytes), 1, 0, len(username_bytes))
                
                self.tcp_sock.sendall(header)
                self.tcp_sock.sendall(room_name_bytes + username_bytes)
                break
            elif choice == '2':
                print('参加したいチャットルームの名前を入力してください。')
                room_name = input('Chat Room Name: ')
                break
            else:
                print('\n1または2を選択してください。')
                
        
    def tcrp_header(self,room_name_size, operation, state ,operation_payload_size):
            return room_name_size.to_bytes(1, 'big') + operation.to_bytes(1, 'big') + state.to_bytes(1, 'big') + operation_payload_size.to_bytes(29, 'big')
        

class Main:
    client = Client()
    
if __name__ == "__main__":
    Main()