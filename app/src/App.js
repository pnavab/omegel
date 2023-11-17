import React, { useEffect, useState } from 'react';

const App = () => {
  const [socket, setSocket] = useState(null);
  const [previousMessages, setPreviousMessages] = useState([]);
  const [messages, setMessages] = useState([]);
  const [messageText, setMessageText] = useState('');
  const [showSnackBar, setShowSnackBar] = useState(false);
  const [snackBarMessage, setSnackBarMessage] = useState('');
  const [snackBarStatus, setSnackBarStatus] = useState('');
  const [userID, setUserId] = useState('');

  useEffect(() => {
    const initializeWebSocket = () => {
      const newSocket = new WebSocket(`ws://${window.location.hostname}:8000/messaging`);
      newSocket.onopen = async () => {
        console.log('connected');
        handleShowSnackBar('Connected', 'Success');
        let p = await (await fetch(`http://${window.location.hostname}:8000/prevmessages`)).json()
        setPreviousMessages(p.messages);
      };

      newSocket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'connect') {
            setSenderId(data.id);
          } else if (data.type === 'disconnected') {
            handleShowSnackBar('Disconnected', `Client ${data.id}`);
          } else {
            setMessages((prevMessages) => [data, ...prevMessages]);
          }
        } catch (e) {
          console.log(event.data);
          console.error(e);
        }
      };

      newSocket.onerror = () => {
        console.log('Failed to connect to websocket');
      };

      newSocket.onclose = () => {
        handleShowSnackBar('Disconnected', 'Client disconnected');
        console.log('Connection closed');
      };

      setSocket(newSocket);
    };

    initializeWebSocket();

    return () => {
      try {
        socket.close();
      } catch (e) {
        console.log('Failed to close socket');
      };
    };
  }, []); // Empty dependency array means this effect runs once when component mounts

  const handleSendMessage = () => {
    if (messageText === '') return;
    socket.send(JSON.stringify({ text: messageText, userID }));

    setMessageText('');
  };

  const handleShowSnackBar = (message, status) => {
    setShowSnackBar(true);
    setSnackBarMessage(message);
    setSnackBarStatus(status);

    setTimeout(() => {
      setShowSnackBar(false);
    }, 3000);
  };

  return (
    <div>
      <div>
        <input
          defaultValue="message"
          type="text"
          value={messageText}
          onChange={(e) => setMessageText(e.target.value)}
        />
        <br></br>
        <input
          defaultValue="userID"
          type="text"
          value={userID}
          onChange={(e) => setUserId(e.target.value)}
        />
        <button onClick={handleSendMessage}>Send</button>
      </div>
      <div>
        <ul style={{listStyleType: "none"}}>
          {messages.length > 0 && (
            <li key={0}>{messages[0].userID} : {messages[0].text}</li>
          )}
        </ul>
        <ul style={{listStyleType: "none"}}>
          {previousMessages.map((msg, index) => (
            <li>{msg[0]} : {msg[1]}</li>
          ))}
        </ul>
      </div>
      {showSnackBar && (
        <div>
          <p>{snackBarMessage} message</p>
          <p>{snackBarStatus} status</p>
        </div>
      )}
    </div>
  );
};

export default App;