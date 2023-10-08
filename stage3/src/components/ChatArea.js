import React, { useEffect, useRef } from 'react';
import { Button, Form, Stack } from 'react-bootstrap';
import defaultIcon from './../assets/user_icon.png'

const styles = {
    selfCard: {
        backgroundColor: 'limegreen',
        padding: '10px',
        borderRadius: '20px',
        margin: '5px 0',
        textAlign: 'right',
        width: '50%',
        float: 'right',
        clear: 'both'
    },
    otherCard: {
        backgroundColor: 'white',
        padding: '10px',
        border: '1px solid #ccc',
        borderRadius: '20px',
        margin: '5px 0',
        textAlign: 'left',
        width: '50%',
        float: 'left',
        clear: 'both'
    },
    selfText: {
        color: 'black'
    },
    otherText: {
        color: 'black'
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

function ChatArea({ messages, clientInfo, messageInput, onMessageChange, onSendMessage }) {
    const chatAreaRef = useRef(null);
    useEffect(() => {
        if (chatAreaRef.current) {
            // スクロールを最下部に移動
            chatAreaRef.current.scrollTop = chatAreaRef.current.scrollHeight;
        }
    }, [messages]);
    
    return (
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
            <Form.Control 
                        type="text" 
                        placeholder="Type a message" 
                        value={messageInput} 
                        onChange={onMessageChange} 
                    />
                <Button type="submit" variant="success" id="sendMessage" onClick={onSendMessage}>Send</Button>
            </Stack>
        </Form>
    </div>
    );
}

export default ChatArea