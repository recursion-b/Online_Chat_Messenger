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
        self.set_username()
        
        server_alive = self.is_server_alive()
        
        if server_alive:
            # サーバーが起動しているのでsettimeoutをリセットする
            self.sock.settimeout(None)
            
            # tcp接続で新しいチャットルームを作成するか、既存のチャットルームに参加するか決める
            self.tcp_sock.connect((self.server_address, self.server_port))
            self.choice_menu()
            # self.startChat()
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
            
        # packetが4096を超えていないかチェックするバリデーターが必要
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
            username = input('\nユーザー名を入力してください。\n\nUser Name: ')
            
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
            print('\n1:新しいチャットルームを作成する\n2:既存のチャットルームに参加する')
            choice = input('\n-> ')

            if choice == '1':
                print('新しいチャットルームを作成します。作成したいチャットルームの名前を入力してください。')
                room_name = input('Room Name: ')
                self.send_menu_selection(choice, room_name)
                
                # サーバーからのリクエスト応答を受け取る
                self.receive_response()
                
                # サーバーからのリクエスト完了を受け取る
                self.receive_response()
                
                print('チャットルームの作成が完了しました。')
                
                self.tcp_sock.close()
                
                break
            elif choice == '2':
                print('参加したいチャットルームの名前を入力してください。')
                room_name = input('Chat Room Name: ')
                self.send_menu_selection(choice, room_name)
                
                # サーバーからのリクエスト応答を受け取る
                self.receive_response()
                
                # サーバーからのリクエスト完了を受け取る
                self.receive_response()
                
                print(f'{room_name}に参加しました。')
                
                self.tcp_sock.close()
                
                break
            else:
                print('\n1または2を選択してください。')
                
    
    def send_menu_selection(self, choice, room_name):
        room_name_bytes = room_name.encode()
        operation_payload_bytes = self.username.encode()

        # 255バイト以下かどうか確認するバリデータが必要
        room_name_size = len(room_name_bytes)
        operation_payload_size = len(operation_payload_bytes)
        # リクエストのstateコードは0
        state = 0
        header = self.tcrp_header(room_name_size,int(choice),state, operation_payload_size)
        
        self.tcp_sock.sendall(header)
        self.tcp_sock.sendall(room_name_bytes + operation_payload_bytes)
    
    def receive_response(self):
        header_size = 32
        header = self.tcp_sock.recv(header_size)
        room_name_size = header[0]
        operation = header[1]
        state = header[2]
        operation_payload_size = int.from_bytes(header[3:])
        
        response_body = self.tcp_sock.recv(room_name_size + operation_payload_size)
        room_name = response_body[0: room_name_size]
        payload = response_body[room_name_size:]
        print(f'\nRoom Name: {room_name.decode()}')
        print(f'Operation: {operation}')
        print(f'State: {state}')
        print(f'Payload: {payload.decode()}')
        
    def tcrp_header(self,room_name_size, operation, state ,operation_payload_size):
        return room_name_size.to_bytes(1, 'big') + operation.to_bytes(1, 'big') + state.to_bytes(1, 'big') + operation_payload_size.to_bytes(29, 'big')
    
    
    
        

class Main:
    client = Client()
    
if __name__ == "__main__":
    Main()