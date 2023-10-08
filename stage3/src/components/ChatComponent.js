import React, { useState, useEffect, useRef } from 'react';
import io from 'socket.io-client';
import 'bootstrap/dist/css/bootstrap.min.css';
import { Button, Form, Container, Row, Col} from 'react-bootstrap';
import ChatArea from './ChatArea';

function ChatComponent() {
    const [currentToken, setCurrentToken] = useState(null);
    const [userName, setUserName] = useState('');
    const [roomName, setRoomName] = useState('');
    const [messageInput, setMessageInput] = useState('');
    const [messages, setMessages] = useState([]);
    const [clients, setClients] = useState([]);
    const [clientInfo, setClientInfo] = useState(null);
    const chatAreaRef = useRef(null);
    const socketRef = useRef(null);
    useEffect(() => {
        if (chatAreaRef.current) {
            // スクロールを最下部に移動
            chatAreaRef.current.scrollTop = chatAreaRef.current.scrollHeight;
        }
    }, [messages]);
    useEffect(() => {
        socketRef.current = io('http://localhost:8000');
        socketRef.current.on('connect', () => {
            console.log('Connected to server');
        });
        socketRef.current.on('message', (message) => {
            setMessages(prev => [...prev, message]);
        });

        socketRef.current.on('updateRoomInfo', (updatedRoomName, clientList) => {
            console.log(clientList)
            setRoomName(updatedRoomName);
            setClients(clientList);
        });

        return () => {
            socketRef.current.off('message');
            socketRef.current.off('updateRoomInfo');
            socketRef.current.close();
        };
    }, []);

    const handleCreateRoom = () => {
        socketRef.current.emit('createRoom', userName, roomName, (response) => {
            if (response.token) {
                setCurrentToken(response.token);
                setClientInfo(response.clientInfo);
                document.getElementById('chatArea').style.display = 'block';
            } else if (response.error) {
                alert(response.error);
            } else {
                alert('Unknown error while creating room.');
            }
        });
    };
    
    const handleJoinRoom = () => {
        socketRef.current.emit('joinRoom', userName, roomName, (response) => {
            if (response.token) {
                setCurrentToken(response.token);
                setClientInfo(response.clientInfo);
                document.getElementById('chatArea').style.display = 'block';
            } else if (response.error) {
                alert(response.error);
            } else {
                alert('Unknown error while joining room.');
            }
        });
    };
    

    const handleSendMessage = (e) => {
        e.preventDefault()
        if (currentToken && messageInput) {
            socketRef.current.emit('message', currentToken, messageInput, userName);
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
            
            <div id="roomInfoArea" className="mt-4">
                <h2>Room Info</h2>
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
            <ChatArea 
                messages={messages} 
                clientInfo={clientInfo} 
                messageInput={messageInput} 
                onMessageChange={e => setMessageInput(e.target.value)} 
                onSendMessage={handleSendMessage} 
            />
        </Container>
    );
}

export default ChatComponent;