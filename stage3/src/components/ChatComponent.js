import React, { useState, useEffect } from 'react';
import io from 'socket.io-client';
import 'bootstrap/dist/css/bootstrap.min.css';
import { Button, Form, Container, Row, Col } from 'react-bootstrap';

const socket = io('http://localhost:3000');

function ChatComponent() {
    const [currentToken, setCurrentToken] = useState(null);
    const [userName, setUserName] = useState('');
    const [roomName, setRoomName] = useState('');
    const [messageInput, setMessageInput] = useState('');
    const [messages, setMessages] = useState([]);
    const [clients, setClients] = useState([]);

    useEffect(() => {
        socket.on('connect', () => {
            console.log('Connected to server');
        });
        socket.on('message', (message) => {
            setMessages(prev => [...prev, message]);
        });

        socket.on('updateRoomInfo', (updatedRoomName, clientList) => {
            console.log(clientList)
            setRoomName(updatedRoomName);
            setClients(clientList);
        });

        return () => {
            socket.off('message');
            socket.off('updateRoomInfo');
        };
    }, []);

    const handleCreateRoom = () => {
        socket.emit('createRoom', userName, roomName, (response) => {
            if (response.token) {
                setCurrentToken(response.token);
                document.getElementById('chatArea').style.display = 'block';
            } else if (response.error) {
                alert(response.error);
            } else {
                alert('Unknown error while creating room.');
            }
        });
    };
    
    const handleJoinRoom = () => {
        socket.emit('joinRoom', userName, roomName, (response) => {
            if (response.token) {
                setCurrentToken(response.token);
                document.getElementById('chatArea').style.display = 'block';
            } else if (response.error) {
                alert(response.error);
            } else {
                alert('Unknown error while joining room.');
            }
        });
    };
    

    const handleSendMessage = () => {
        if (currentToken && messageInput) {
            socket.emit('message', currentToken, messageInput, userName);
            setMessageInput('');
        }
    };

    return (
        <Container>
            <Row className="mt-3">
                <Col md={3}>
                    <Form.Label>Username:</Form.Label>
                    <Form.Control type="text" value={userName} onChange={e => setUserName(e.target.value)} />
                </Col>
                <Col md={3}>
                    <Form.Label>Room name:</Form.Label>
                    <Form.Control type="text" placeholder="Enter room name" value={roomName} onChange={e => setRoomName(e.target.value)} />
                </Col>
                <Col md={2}>
                    <Button variant="primary" id="createRoom" onClick={handleCreateRoom}>Create Room</Button>
                </Col>
                <Col md={2}>
                    <Button variant="info" id="joinRoom" onClick={handleJoinRoom}>Join Room</Button>
                </Col>
            </Row>

            <div id="chatArea" style={{ display: 'none' }}>
                <div id="messages">
                    {messages.map((message, index) => <div key={index}>{message}</div>)}
                </div>
                <Row className="mt-3">
                    <Col md={10}>
                        <Form.Control type="text" placeholder="Type a message" value={messageInput} onChange={e => setMessageInput(e.target.value)} />
                    </Col>
                    <Col md={2}>
                        <Button variant="success" id="sendMessage" onClick={handleSendMessage}>Send</Button>
                    </Col>
                </Row>
            </div>

            <div id="roomInfoArea" className="mt-4">
                <h2>Room Info!!!!</h2>
                <div id="currentRoomName">Room Name: {roomName || '部屋に参加していません'}</div>
                <div id="currentHostName">Host Name: {clients.length > 0 && clients[0].host_name}</div>
                <h3>Clients:</h3>
                <ul id="clientList">
                    {clients.map((client, idx) => (
                        <li key={idx}>
                            Token: {client.access_token}, Last Message Time: {new Date(client.last_message_time).toLocaleString()}
                            {client.host_name && `, Host: ${client.host_name}`}
                        </li>
                    ))}
                </ul>
            </div>
        </Container>
    );
}

export default ChatComponent;