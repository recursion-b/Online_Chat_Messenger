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
    constructor(socket, userName = null, iconImage = null) {
        this.socket = socket;
        this.userName = userName;
        this.iconImage = iconImage;
        this.access_token = null;
        this.connected_at = Date.now();
        this.is_host = false;
        this.last_message_time = Date.now();
    }

    generateToken() {
        this.access_token = crypto.randomBytes(16).toString('hex');
        return this.access_token;
    }
}

let chatRooms = {};

socketIo.on('connection', (socket) => {
    console.log('User connected:', socket.id);

    const client = new ClientInfo(socket);

    socket.on('createRoom', (userName, roomName, iconImage, callback) => {
        if (typeof roomName !== 'string' || roomName.trim() === '') {
            return callback({ error: "Invalid room name" });
        }
        console.log("部屋作成！！")
        if (!chatRooms[roomName]) {
            chatRooms[roomName] = [];
            client.userName = userName;
            client.is_host = true;
            const token = client.generateToken();
            chatRooms[roomName].push(client);
            callback({ token, clientInfo: { userName: client.userName, iconImage: client.iconImage, access_token: client.access_token, is_host: client.is_host } });
            broadcastRoomInfo(roomName);
        } else {
            callback({ error: "Room already exists" });
        }
    });

    socket.on('joinRoom', (userName, roomName, iconImage, callback) => {
        if (typeof roomName !== 'string' || roomName.trim() === '') {
            return callback({ error: "Invalid room name" });
        }
        console.log("部屋参加！！")
        if (chatRooms[roomName]) {
            client.userName = userName;
            const token = client.generateToken();
            chatRooms[roomName].push(client);
            callback({ token, clientInfo: { userName: client.userName, iconImage: client.iconImage, access_token: client.access_token, is_host: client.is_host } });
            broadcastRoomInfo(roomName);
        } else {
            callback({ error: "Room doesn't exist" });
        }
    });

    socket.on('message', (token, message, userName, iconImage) => {
        console.log(message);
        const roomName = Object.keys(chatRooms).find(room => chatRooms[room].some(c => c.access_token === token));
        if (roomName) {
            let roomMessage = {
                content: message,
                userName: userName,
                token: token,
                iconImage: iconImage
            }; // ここを変更
            for (const client of chatRooms[roomName]) {
                client.socket.emit('message', roomMessage);
            }
        }
    });

    socket.on('disconnect', () => {
        for (const room in chatRooms) {
            chatRooms[room] = chatRooms[room].filter(c => c.socket !== socket);
            if (chatRooms[room].length === 0) {
                delete chatRooms[room];
            }
        }
    
        console.log('User disconnected:', socket.id);
    });

    function broadcastRoomInfo(roomName) {
        const clientsInfo = chatRooms[roomName].map(client => {
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
        console.log(`Sending updateRoomInfo event for room: ${roomName}`);
        for (const client of chatRooms[roomName]) {
            client.socket.emit('updateRoomInfo', roomName, clientsInfo);
        }
    }

//     function checkForInactiveClients() {
//         const inactivityThreshold = 30 * 1000; 

//         for (const room in chatRooms) {
//             const clientsToRemove = [];

//             for (const client of chatRooms[room]) {
//                 if (Date.now() - client.last_message_time > inactivityThreshold) {
//                     clientsToRemove.push(client);
//                 }
//             }

//             for (const inactiveClient of clientsToRemove) {
//                 chatRooms[room] = chatRooms[room].filter(c => c !== inactiveClient);
//                 inactiveClient.socket.emit('message', `[Server]: ${inactiveClient.userName} has been disconnected due to inactivity.`);
//                 inactiveClient.socket.disconnect();
//             }

//             if (chatRooms[room].length === 0) {
//                 delete chatRooms[room];
//             } else if (chatRooms[room]) { 
//                 broadcastRoomInfo(room);
//             }
//         }
//     }

//     setInterval(checkForInactiveClients, 10 * 1000);
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
