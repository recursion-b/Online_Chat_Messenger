//server
const express = require('express');
const http = require('http');
const io = require('socket.io');
const crypto = require('crypto');
const path = require('path');

const app = express();
const server = http.createServer(app);
const socketIo = io(server, {
    cors: {
        origin: "http://localhost:3000",
        methods: ["GET", "PORT"],
    }
});

class ClientInfo {
    constructor(socket, userName, access_token, is_host) {
        this.socket = socket;
        this.userName = userName;
        this.access_token = access_token;
        this.connected_at = Date.now();
        this.is_host = is_host;
        this.last_message_time = Date.now();
    }

}


class ChatRoom{
    constructor(roomName){
        this.roomName = roomName;
        this.clientInfos = [];
    }

    addClientInfo(clientInfo) {
        this.clientInfos.push(clientInfo);
    }

    broadcastMessageToClients(token, message, userName){
        let roomMessage = { content: `${userName} -> ${message}`, token: token };
        for (const client of this.clientInfos) {
            client.socket.emit('message', roomMessage);
        }
    }

    broadcastRoomInfo() {
        const clientInfo = this.clientInfos.map(client =>{
            const info = {
                access_token: client.access_token,
                last_message_time: client.connected_at
            };

            if (client.is_host) {
                info.host_name = client.userName;
            }
            console.log(info)
            return info;
        });
        console.log(`Sending updateRoomInfo event for room: ${this.roomName}`);
        for (const client of this.clientInfos) {
            client.socket.emit('updateRoomInfo', this.roomName, clientInfo);
        }
    }

    findInActiveClients(){
        let clientsToRemove = [];

        for(const clientInfo of this.clientInfos){
            const inactivityThreshold = 30 * 1000;
            if(Date.now() - clientInfo.last_message_time > inactivityThreshold){
                clientsToRemove.push(clientInfo)
                if(clientInfo.is_host){
                    clientsToRemove.push(
                        ...this.clientInfos.filter((info) => !clientsToRemove.includes(info))
                    );
                    break
                }
            }
        }

        return clientsToRemove
    }

    removeClients(clientsToRemove){
        for(const clientInfo of clientsToRemove){
            let index = this.clientInfos.indexOf(clientInfo);
            if (index !== -1) {
                this.clientInfos.splice(index, 1);
            }
        }
    }

    broadcastRemovalMessage(clientsToRemove){
        for(const clientInfo of clientsToRemove){
            if(clientInfo.is_host){
                this.broadcastMessageToClients(null, `${clientInfo.userName} (Host) has left the room.`, "System");
            }else{
                this.broadcastMessageToClients(null, `${clientInfo.userName} has left the room.`, "System");
            }
        }
    }

}

let chatRooms = {}; // {roomName: ChatRoom obj}
let tokens = {}; // {token: room_name}
let clients = {}; // {token: client_info}

socketIo.on('connection', (socket) => {
    console.log('User connected:', socket.id);


    socket.on('createRoom', (userName, roomName, callback) => {
        if (typeof roomName !== 'string' || roomName.trim() === '') {
            return callback({ error: "Invalid room name" });
        }
        console.log("部屋作成！！")
        if (!chatRooms[roomName]) {
            // tokenの作成
            const token = generateToken();

            // チャットルームの作成
            const chatRoom = new ChatRoom(roomName);
            chatRooms[roomName] = chatRoom            
            tokens[token] = roomName

            // clientInfoの作成
            const client = new ClientInfo(socket, userName, token, true);
            clients[token] = client
            
            chatRoom.addClientInfo(client)

            callback({ token, clientInfo: { userName: client.userName, access_token: client.access_token, is_host: client.is_host } });
            chatRoom.broadcastRoomInfo(roomName);
        } else {
            callback({ error: "Room already exists" });
        }
    });

    socket.on('joinRoom', (userName, roomName, callback) => {
        if (typeof roomName !== 'string' || roomName.trim() === '') {
            return callback({ error: "Invalid room name" });
        }
        console.log("部屋参加！！")
        if (chatRooms[roomName]) {
            // tokenの作成
            const token = generateToken();

            // チャットルームの作成
            const chatRoom = chatRooms[roomName]
            tokens[token] = roomName

            // clientInfoの作成
            const client = new ClientInfo(socket, userName, token, false);
            clients[token] = client

            chatRoom.addClientInfo(client)

            callback({ token, clientInfo: { userName: client.userName, access_token: client.access_token, is_host: client.is_host } });
            chatRoom.broadcastRoomInfo(roomName);
        } else {
            callback({ error: "Room doesn't exist" });
        }
    });

    socket.on('message', (token, message, userName) => {
        console.log(message);
        const roomName = tokens[token]
        const chatRoom = chatRooms[roomName];

        if (chatRoom) {
            updateLastMessage(token);
            chatRoom.broadcastMessageToClients(token, message, userName)
        }
    });

    socket.on('disconnect', () => {
        // どの部屋にも所属していない場合は、次の行をスキップ
        const clientInfo = Object.values(clients).find(c => c.socket === socket);
        if (!clientInfo) return;
    
        const roomName = tokens[clientInfo.access_token];
        const chatRoom = chatRooms[roomName];
    
        if (chatRoom) {
            if (clientInfo.is_host) {
                // ホストが切断した場合の処理
                chatRoom.broadcastMessageToClients(null, `${clientInfo.userName} (Host) has left the room.`, "System");
                // 新しいホストを選択するか、部屋を解散する処理をここに追加
            } else {
                chatRoom.broadcastMessageToClients(null, `${clientInfo.userName} has left the room.`, "System");
            }
    
            // クライアント情報を部屋から削除
            chatRoom.clientInfos = chatRoom.clientInfos.filter(c => c.socket !== socket);
    
            // 必要に応じて部屋を削除
            deleteRoomIfEmpty(chatRoom);
        }
    
        // クライアントとトークンの情報を削除
        delete tokens[clientInfo.access_token];
        delete clients[clientInfo.access_token];
    
        console.log('User disconnected:', socket.id);
    });

    function generateToken(){
        return crypto.randomBytes(16).toString('hex');
    }

    function updateLastMessage(token){
        const clientInfo = clients[token];
        clientInfo.last_message_time = Date.now()
    }


    function checkForInactiveClients() {

        for(const chatRoom of Object.values(chatRooms)){
            const clientsToRemove = chatRoom.findInActiveClients();
            chatRoom.broadcastRemovalMessage(clientsToRemove);
            removeTokensAndClients(clientsToRemove);
            chatRoom.removeClients(clientsToRemove);
            deleteRoomIfEmpty(chatRoom);
        }

    }

    function removeTokensAndClients(clientsToRemove){
        for(const clientInfo of clientsToRemove){
            if (clientInfo.access_token in tokens){
                delete tokens[clientInfo.access_token]
            }
            if(clientInfo.access_token in clients){
                delete clients[clientInfo.access_token]
            }
        }
    }
    
    function deleteRoomIfEmpty(chatRoom){
        if(chatRoom.clientInfos.length === 0){
            delete chatRooms[chatRoom.roomName]
        }
    }

    setInterval(checkForInactiveClients, 10 * 1000);
});



// Reactのフロントエンドを提供するための設定
if (process.env.NODE_ENV === 'production') {
    app.use(express.static('build'));
    app.get('*', (req, res) => {
        res.sendFile(path.resolve(__dirname, 'build', 'index.html'));
    });
}

const PORT = process.env.PORT || 8000;
server.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
