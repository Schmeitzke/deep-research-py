// src/components/ChatMessage.tsx
import React from 'react';
import LoadingSpinner from './LoadingSpinner';

interface ChatMessageProps {
  content: string;
  role: 'user' | 'system';
  type?: 'text' | 'question' | 'update' | 'finalReport';
}

const ChatMessage: React.FC<ChatMessageProps> = ({ content, role, type = 'text' }) => {
  return (
    <div className={`chat-message ${role}`}>
      <div className="message-bubble">
        {type === 'update' && <LoadingSpinner />}
        {content}
      </div>
    </div>
  );
};

export default ChatMessage;
