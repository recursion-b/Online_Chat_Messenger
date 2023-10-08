import React, { useState, useEffect, useRef } from 'react';
import io from 'socket.io-client';
import 'bootstrap/dist/css/bootstrap.min.css';

import { Button, Form, Container, Row, Col} from 'react-bootstrap';
import { FaUser, FaKey, FaDoorOpen, FaPlus } from 'react-icons/fa';
import ChatArea from './ChatArea';
import Dropzone from './Deopzone';

function ChatComponent() {
    const [currentToken, setCurrentToken] = useState(null);
    const [userName, setUserName] = useState('');
    const [roomName, setRoomName] = useState('');
    const [password, setPassword] = useState('');
    const [iconImage, setIconImage] = useState(null)
    const [messageInput, setMessageInput] = useState('');
    const [messages, setMessages] = useState([]);
    const [clients, setClients] = useState([]);
    const [clientInfo, setClientInfo] = useState(null);
    const socketRef = useRef(null);
    console.log(clients)
    useEffect(() => {
        socketRef.current = io('https://online-chat-messenger.onrender.com/');
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
        socketRef.current.emit('createRoom', userName, roomName, iconImage, password, (response) => {
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
        socketRef.current.emit('joinRoom', userName, roomName, iconImage, password, (response) => {
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
        if (clientInfo && currentToken && messageInput) {
            const uid = clientInfo.uid;
            socketRef.current.emit('message', uid, currentToken, messageInput, userName, iconImage);
            setMessageInput('');
        }
    };

    return (
        <Container>
            {/* アイコン選択 */}
            <Row className="mt-3" >
                <Col>
                    <Dropzone iconImage={iconImage} setIconImage={setIconImage} />
                </Col>
            </Row>
            <Container>
                <Row className="mt-3">
                    <Col md={4} className="mb-3">
                        <Form.Label><FaUser /> Username:</Form.Label>
                        <Form.Control type="text" value={userName} onChange={e => setUserName(e.target.value)} />
                    </Col>
                    <Col md={4} className="mb-3">
                        <Form.Label><FaDoorOpen /> Room name:</Form.Label>
                        <Form.Control type="text" placeholder="Enter room name" value={roomName} onChange={e => setRoomName(e.target.value)} />
                    </Col>
                    <Col md={4} className="mb-3">
                        <Form.Label><FaKey /> Password:</Form.Label>
                        <Form.Control type="password" placeholder="password" value={password} onChange={e => setPassword(e.target.value)} />
                    </Col>
                </Row>
                <Row className="mb-3 justify-content-center">
                    <Col xs={5} md={3}>
                        <Button variant="primary" id="createRoom" onClick={handleCreateRoom} className="w-100"><FaPlus/>Create Room</Button>
                    </Col>
                    <Col xs={5} md={3}>
                        <Button variant="info" id="joinRoom" onClick={handleJoinRoom} className="w-100"><FaDoorOpen/>Join Room</Button>
                    </Col>
                </Row>

            </Container>      
      
            <div id="roomInfoArea" className="mt-4">
                <h2>Room Info</h2>
                <div id="currentRoomName">Room Name: {roomName || '部屋に参加していません'}</div>
                <div id="currentHostName">Host Name: {clients.length > 0 && clients[0].host_name}</div>
                <h3>Clients:</h3>
                <ul id="clientList">
                    {clients.map((client, idx) => (
                        <li key={idx}>
                            Name: {client.userName}
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