import React, { useRef } from 'react';
import { Button, Form, Stack } from 'react-bootstrap';
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
function ChatArea({ messages, clientInfo, messageInput, onMessageChange, onSendMessage }) {
    const chatAreaRef = useRef(null);

    return (
        <div style={chatContainerStyle}>
            <div id="chatArea" style={{ ...chatAreaStyle, display: 'none' }} ref={chatAreaRef}>
                <div id="messages">
                    {messages.map((message, index) => {
                        const isSelf = message.token === clientInfo.access_token;
                        const cardStyle = isSelf ? styles.selfCard : styles.otherCard;
                        const textColor = isSelf ? styles.selfText : styles.otherText;

                        return (
                            <div key={index} style={cardStyle}>
                                <p style={textColor}>{message.content}</p>
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