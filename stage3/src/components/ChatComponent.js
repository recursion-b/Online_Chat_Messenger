import React, { useState, useEffect, useRef } from 'react';
import io from 'socket.io-client';
import 'bootstrap/dist/css/bootstrap.min.css';
import { Button, Form, Container, Row, Col, Stack } from 'react-bootstrap';
import Dropzone from './Deopzone';
import defaultIcon from './../assets/user_icon.png'


const styles = {
    selfCard: {
        backgroundColor: 'limegreen',
        padding: '10px',
        borderRadius: '20px',
        maxWidth: '300px',
    },
    otherCard: {
        backgroundColor: 'white',
        padding: '10px',
        border: '1px solid #ccc',
        borderRadius: '20px',
        maxWidth: '300px',
    },
    selfText: {
        color: 'black',
        wordWrap: 'break-word',
        margin: '0 0 0 0'
    },
    otherText: {
        color: 'black',
        wordWrap: 'break-word',
        margin: '0 0 0 0'
    }
}

const chatContainerStyle = {
    height: '300px', 
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'flex-end',
    backgroundColor: '#e0f0ff' 
};
  
const chatAreaStyle = {
    overflowY: 'auto',
    flexGrow: 1
};

const iconImageStyle = {
    width: '50px',
    height: '50px',
    borderRadius: '50%',
    margin: '0 5px 0 0'
}

function ChatComponent() {
    const [currentToken, setCurrentToken] = useState(null);
    const [userName, setUserName] = useState('');
    const [roomName, setRoomName] = useState('');
    const [iconImage, setIconImage] = useState(null)
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
        socketRef.current.emit('createRoom', userName, roomName, iconImage, (response) => {
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
        socketRef.current.emit('joinRoom', userName, roomName, iconImage, (response) => {
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
            socketRef.current.emit('message', currentToken, messageInput, userName, iconImage);
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
            <div style={chatContainerStyle}>
                <div id="chatArea" style={{ ...chatAreaStyle, display: 'none' }} ref={chatAreaRef}>
                    <div id="messages">
                        {messages.map((message, index) => {
                            const isSelf = message.token === clientInfo.access_token;
                            const cardStyle = isSelf ? styles.selfCard : styles.otherCard;
                            const textColor = isSelf ? styles.selfText : styles.otherText;

                            return (
                                <div key={index}>
                                    {isSelf ? (
                                        <div className='d-flex justify-content-end my-2'>
                                            <div style={styles.selfCard}>
                                                <p style={textColor}>{message.content}</p>
                                            </div>                              
                                        </div>
                                        ) : (
                                            <div className='d-flex flex-column my-2'>
                                                <p className='mb-0'>{message.userName}</p>
                                                <div className='d-flex align-items-top'>
                                                    <img src={message.iconImage != null ? message.iconImage : defaultIcon} style={iconImageStyle} alt='user-icon' />
                                                    <div style={cardStyle}>
                                                        <p style={textColor}>{message.content}</p>
                                                    </div>
                                                </div>
                                            </div>
                                        )
                                    }
                                </div>
                            );
                        })}
                    </div>
                </div>
                <Form>
                    <Stack direction="horizontal" className="mt-3">
                        <Form.Control type="text" placeholder="Type a message" value={messageInput} onChange={e => setMessageInput(e.target.value)} />
                        <Button type="submit" variant="success" id="sendMessage" onClick={handleSendMessage}>Send</Button>
                    </Stack>
                </Form>
            </div>
        </Container>
    );
}

export default ChatComponent;