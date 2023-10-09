import React, { useState, useEffect, useRef } from 'react';
import io from 'socket.io-client';
import 'bootstrap/dist/css/bootstrap.min.css';

import { Button, Form, Container, Row, Col} from 'react-bootstrap';
import { FaUser, FaKey, FaDoorOpen, FaPlus, FaImage} from 'react-icons/fa';
import ChatArea from './ChatArea';
import Dropzone from './Dropzone';

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
    const [isChatAreaVisible, setIsChatAreaVisible] = useState(false);

    useEffect(() => {
        socketRef.current = io('https://online-chat-messenger.onrender.com/');
        socketRef.current.on('connect', () => {
            console.log('Connected to server');
        });
        socketRef.current.on('message', (message) => {
            setMessages(prev => [...prev, message]);
            console.log(message)
        });

        socketRef.current.on('updateRoomInfo', (updatedRoomName, clientList) => {
            console.log(clientList)
            setRoomName(updatedRoomName);
            setClients(clientList);
        });

        socketRef.current.on('clientDisconnected', (data) => {
            console.log(data.message);
            setCurrentToken(null);
            setClientInfo(null);
            setRoomName('');
            setClients([]);
        });

        socketRef.current.on('hostExited', () => {
            setTimeout(() => {
                setIsChatAreaVisible(false);
            }, 10000); 
        });
    

        return () => {
            socketRef.current.off('message');
            socketRef.current.off('updateRoomInfo');
            socketRef.current.off('clientDisconnected');
            socketRef.current.off('hostExited');
            socketRef.current.close();
        };
    }, []);

    const handleCreateRoom = () => {
        socketRef.current.emit('createRoom', userName, roomName, iconImage, password, (response) => {
            if (response.token) {
                setCurrentToken(response.token);
                setClientInfo(response.clientInfo);
                setIsChatAreaVisible(true);
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
                setIsChatAreaVisible(true);
            } else if (response.error) {
                alert(response.error);
            } else {
                alert('Unknown error while joining room.');
            }
        });
    };

    const handleExitRoom = () => {
        setIsChatAreaVisible(false);
        socketRef.current.emit('exitRoom', { roomName, clientInfo });
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
            {isChatAreaVisible ? (
                <>
                <div id="roomInfoArea" className="mt-4">
                    <h2>Room Info</h2>
                    
                    <div className="d-flex align-items-center justify-content-between mb-2">
                        <div id="currentRoomName">Room Name: {roomName || '部屋に参加していません'}</div>
                        
                        {roomName && (
                            <Button variant="danger" onClick={handleExitRoom}>exit</Button>
                        )}
                    </div>

                    <div id="currentHostName">Host Name: {clients.length > 0 && clients[0].host_name}</div>
                    <div><Dropzone iconImage={iconImage} setIconImage={setIconImage} /></div>
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

                </>
            ) : (
                <>
                    <Container className="d-flex justify-content-center align-items-center" style={{ minHeight: '70vh' }}>
                        <div className="w-100">
                            <Row className="mt-3 justify-content-center">
                                <Col md={6} className="mb-3">
                                    <Form.Label><FaUser /> Username:</Form.Label>
                                    <Form.Control type="text" value={userName} onChange={e => setUserName(e.target.value)} />
                                </Col>
                                <Col md={6} className="mb-3">
                                    <Form.Label><FaDoorOpen /> Room name:</Form.Label>
                                    <Form.Control type="text" placeholder="Enter room name" value={roomName} onChange={e => setRoomName(e.target.value)} />
                                </Col>
                            </Row>

                            <Row className="mt-3 justify-content-center">
                                <Col md={6} className="mb-3">
                                    <Form.Label><FaKey /> Password:</Form.Label>
                                    <Form.Control type="password" placeholder="password" value={password} onChange={e => setPassword(e.target.value)} />
                                </Col>
                                <Col md={6} className="mb-3">
                                    <Form.Label><FaImage /> Choose Icon:</Form.Label>
                                    <div><Dropzone iconImage={iconImage} setIconImage={setIconImage} /></div>
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
                        </div>
                    </Container>
                </>
            )}
        </Container>
    );    
}

export default ChatComponent;