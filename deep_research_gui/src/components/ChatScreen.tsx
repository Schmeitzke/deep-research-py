// src/components/ChatScreen.tsx
import React, { useState } from 'react';
import { useChat, ChatMessageData } from '../hooks/useChat';
import ChatMessage from './ChatMessage';
import MarkdownMessage from './MarkdownMessage';

interface ChatScreenProps {
  initialPrompt: string;
  computeMode: 'low' | 'medium' | 'high';
}

const ChatScreen: React.FC<ChatScreenProps> = ({ initialPrompt, computeMode }) => {
  const {
    messages,
    sendUserMessage,
    isComplete,
    finalReport
  } = useChat(initialPrompt, computeMode);

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
            return (
              <MarkdownMessage key={index} markdown={msg.content} role="system" />
            );
          }
          return (
            <ChatMessage key={index} content={msg.content} role={msg.role} />
          );
        })}
      </div>
      <form onSubmit={handleSend} className="chat-input">
        <textarea
          placeholder={isComplete ? "Research complete" : "Type your answer here..."}
          value={userInput}
          onChange={(e) => setUserInput(e.target.value)}
          rows={2}
          style={{ width: '60%' }}
          disabled={isComplete}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              handleSend(e);
            }
          }}
        />
        <button type="submit" disabled={isComplete}>Send</button>
      </form>
    </div>
  );
};

export default ChatScreen;
