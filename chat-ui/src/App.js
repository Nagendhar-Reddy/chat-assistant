import React, { useState, useRef, useEffect } from 'react';
import './App.css';

function App() {
  const [messages, setMessages] = useState([
    { 
      id: 1, 
      text: "Hello! I'm your database assistant. Ask me questions about people in the database.", 
      sender: 'bot' 
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (input.trim() === '') return;
    
    // Add user message to chat
    const userMessage = { id: messages.length + 1, text: input, sender: 'user' };
    setMessages([...messages, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Send request to backend API
      const response = await fetch('http://127.0.0.1:8001/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: input }),
      });

      if (!response.ok) {
        throw new Error('Something went wrong');
      }

      const data = await response.json();
      
      // Add bot response to chat
      const botMessage = { id: messages.length + 2, text: data.answer, sender: 'bot' };
      setMessages(prevMessages => [...prevMessages, botMessage]);
    } catch (error) {
      console.error('Error:', error);
      const errorMessage = { 
        id: messages.length + 2, 
        text: "Sorry, I couldn't process your request. Please try again.", 
        sender: 'bot' 
      };
      setMessages(prevMessages => [...prevMessages, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSend();
    }
  };

  return (
    <div className="app">
      <div className="chat-container">
        <div className="chat-header">
          <div className="chat-title">
            <h1>My Assistant</h1>
            <p>Ask questions about people in the database</p>
          </div>
        </div>
        
        <div className="messages-container">
          {messages.map((message) => (
            <div 
              key={message.id} 
              className={`message ${message.sender === 'user' ? 'user-message' : 'bot-message'}`}
            >
              <div className="message-avatar">
                {message.sender === 'user' ? '👤' : '🤖'}
              </div>
              <div className="message-content">
                <p>{message.text}</p>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="message bot-message">
              <div className="message-avatar">🤖</div>
              <div className="message-content">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
        
        <div className="input-container">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about people in the database..."
            disabled={isLoading}
          />
          <button 
            onClick={handleSend}
            disabled={isLoading || input.trim() === ''}
            className={isLoading ? 'loading' : ''}
          >
            {isLoading ? <div className="spinner"></div> : <span>Send</span>}
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;