import socket
import datetime

class Server:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.address = '127.0.0.1'
        self.port = 8000
        self.clientMap = {} # {'address':{'username': username, 'address':address, 'last_message_time':datetime.datetime.now()}}
        self.sock.bind((self.address, self.port))
        
        print('サーバーを起動しました。')
    
    def receive(self):
        print("メッセージを待機中...")
        
        max_buffer = 4096
        
        while True:
            data, address = self.sock.recvfrom(max_buffer)
            usernamelen = data[0]
            
            username_data = data[1:1 + usernamelen]
            username = username_data.decode()
            
            message = data[1 + usernamelen: ].decode()
            
            self.update_last_message(address, username)    
            
            print(f'{username}: {message}')

            if data:
                packet = self.protocol_sending(usernamelen, username, message)
                self.send(packet)
    
    def protocol_sending(self, usernamelen, username, message):
        return bytes([usernamelen]) + username.encode() + message.encode()
            
    def send(self, packet):
            for address in self.clientMap:
                time_over = self.check_if_time_over(address)
                
                if time_over:
                    self.delete_address_from_clientMap(address)
                else:
                    self.sock.sendto(packet, address)     
    
    def check_if_time_over(self, address):
        # 現在の時刻と最後のメッセージの送信時刻を比較する
        td = datetime.datetime.now() - self.clientMap[address]['last_message_time']
        
        # 時間、分、秒に変換
        h, m, s = self.get_h_m_s(td)
        
        # 最後のメッセージが30分以上経過していたらTrueを返す
        if m > 30:
            self.clientMap.pop(address)
            return True
    
    def delete_address_from_clientMap(self, address):
        self.clientMap.pop(address)
                
    def get_h_m_s(self, td):
        m, s = divmod(td.seconds, 60)
        h, m = divmod(m, 60)
        return h, m, s

    def update_last_message(self, address, username):
        if self.clientMap in address:
            self.clientMap[address]['last_message_time'] = datetime.datetime.now()    
        else:
            self.clientMap[address] = {'username': username, 'address':address, 'last_message_time':datetime.datetime.now()}
            
class Main:
    server = Server()
    server.receive()
    
if __name__ == "__main__":
    Main()