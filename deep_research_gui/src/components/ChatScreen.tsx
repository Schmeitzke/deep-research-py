import React, { useState } from 'react';
import { useChat, ChatMessageData } from '../hooks/useChat';
import ChatMessage from './ChatMessage';
import MarkdownMessage from './MarkdownMessage';

interface ChatScreenProps {
  initialPrompt: string;
}

const ChatScreen: React.FC<ChatScreenProps> = ({ initialPrompt }) => {
  const {
    messages,
    sendUserMessage,
    isComplete,
    finalReport
  } = useChat(initialPrompt);

  const [userInput, setUserInput] = useState('');

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = userInput.trim();
    if (trimmed.length > 0) {
      sendUserMessage(trimmed);
      setUserInput('');
    }
  };

  return (
    <div className="chat-screen">
      <div className="chat-messages">
        {messages.map((msg: ChatMessageData, index: number) => {
          if (msg.type === 'finalReport') {
            // Render the final markdown report
            return (
              <MarkdownMessage key={index} markdown={msg.content} role="system" />
            );
          }
          return (
            <ChatMessage
              key={index}
              content={msg.content}
              role={msg.role}
            />
          );
        })}

        {/* Optionally, render the final report again if you want a separate display */}
        {isComplete && finalReport && (
          <MarkdownMessage markdown={finalReport} role="system" />
        )}
      </div>

      {!isComplete && (
        <form onSubmit={handleSend} className="chat-input">
          <input
            type="text"
            placeholder="Type your answer here..."
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') handleSend(e);
            }}
          />
          <button type="submit">Send</button>
        </form>
      )}
    </div>
  );
};

export default ChatScreen;
