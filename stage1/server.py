import socket
import datetime
import uuid

class Server:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.address = '127.0.0.1'
        self.port = 8000
        self.client_map = {} # {'address':{'address':address, 'last_message_time':datetime.datetime.now()}}
        self.host_map = {} # {unique token: {address: address, username: username}}
        self.sock.bind((self.address, self.port))
        
        print('サーバーを起動しました。')
    
    def receive(self):
        print("メッセージを待機中...")
        
        max_buffer = 4096
        
        while True:
            data, address = self.sock.recvfrom(max_buffer)
            decoded_data = self.protocol_receiving(data)
            username = decoded_data[0]
            message = decoded_data[1]
            
            if address in self.client_map:
                self.update_last_message(address)
                
            else:
                self.add_client_map(address)
                
            print(f'{username}: {message}')
            if data:
                packet = self.protocol_sending(username, message)
                self.send(packet)
            
            # tcp接続を開始
            tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # 同じポートをすぐに再利用するためのオプション
            tcp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            tcp_sock.bind((self.address, self.port))
            tcp_sock.listen(5)
            client_socket, address = tcp_sock.accept()
            
            # リクエストの内容を受信
            request = self.receive_request(client_socket)
            room_name_size = request[0]
            operation = request[1]
            room_name_bytes = request[2]
            
            # リクエスト応答のレスポンス
            response_state = 1
            accepted_status_code = '202 Accepted'
            self.send_response(client_socket, room_name_size, room_name_bytes, operation, response_state, accepted_status_code)
            
            # リクエスト完了のレスポンス
            done_state = 2 
            unique_token = str(uuid.uuid4()) # 16バイトのトークン
            self.send_response(client_socket, room_name_size, room_name_bytes, operation, done_state, unique_token)
            self.add_host_map(unique_token, address, username)
            
            # 新しいチャットルームに参加、あるいは既存のチャットルームに参加させる挙動をここに追加
            
            client_socket.close()
            tcp_sock.close()
            
    
    def protocol_sending(self,username, message):
        usernamelen = len(username.encode())
        return bytes([usernamelen]) + username.encode() + message.encode()
    
    def protocol_receiving(self, data):
        usernamelen = data[0]
        username_data = data[1:1 + usernamelen]
        username = username_data.decode()
        message = data[1 + usernamelen: ].decode()
            
        return (username, message)
    
    def tcrp_header(self,room_name_size, operation, state ,operation_payload_size):
        return room_name_size.to_bytes(1, 'big') + operation.to_bytes(1, 'big') + state.to_bytes(1, 'big') + operation_payload_size.to_bytes(29, 'big')

    def receive_request(self,client_socket):
        header_size = 32
        header = client_socket.recv(header_size)
        room_name_size = header[0]
        operation = header[1]
        state = header[2]
        operation_payload_size = int.from_bytes(header[3:])
        
        # クライアントからデータを受信
        data = client_socket.recv(room_name_size + operation_payload_size)
        room_name_bytes = data[0:room_name_size]
        operation_payload = data[room_name_size:]
        
        print(f'\nRoom Name: {room_name_bytes.decode()}')
        print(f'Operation: {operation}')
        print(f'State: {state}')
        print(f'Payload: {operation_payload.decode()}')
        
        return (room_name_size, operation, room_name_bytes)
    
    def send_response(self, client_socket ,room_name_size, room_name_bytes ,operation, state, operation_payload):
        header = self.tcrp_header(room_name_size, operation, state, len(operation_payload.encode()))
        client_socket.sendall(header)
        client_socket.sendall(room_name_bytes + operation_payload.encode())
            
    def send(self, packet):
            for address in self.client_map:
                time_over = self.check_if_time_over(address)
                
                if time_over:
                    self.delete_address_from_client_map(address)
                else:
                    self.sock.sendto(packet, address)     
    
    def check_if_time_over(self, address):
        # 現在の時刻と最後のメッセージの送信時刻を比較する
        td = datetime.datetime.now() - self.client_map[address]['last_message_time']
        
        # 時間、分、秒に変換
        h, m, s = self.get_h_m_s(td)
        
        # 最後のメッセージが30分以上経過していたらTrueを返す
        if m > 30:
            self.client_map.pop(address)
            return True
    
    def delete_address_from_client_map(self, address):
        self.client_map.pop(address)
                
    def get_h_m_s(self, td):
        m, s = divmod(td.seconds, 60)
        h, m = divmod(m, 60)
        return h, m, s

    def update_last_message(self, address):
        self.client_map[address]['last_message_time'] = datetime.datetime.now()    
        
    def add_client_map(self, address):
        self.client_map[address] = {'address':address, 'last_message_time':datetime.datetime.now()}
        
    def add_host_map(self,unique_token, address, username):
        self.client_map[unique_token] = {'address': address, 'username': username}
        
class Main:
    server = Server()
    server.receive()
    
if __name__ == "__main__":
    Main()