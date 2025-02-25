// src/components/ChatMessage.tsx
import React from 'react';
import LoadingSpinner from './LoadingSpinner';

interface ChatMessageProps {
  content: string;
  role: 'user' | 'system';
  type?: 'text' | 'question' | 'update' | 'finalReport';
}

const ChatMessage: React.FC<ChatMessageProps> = ({ content, role, type = 'text' }) => {
  // Show loading spinner for update messages
  const isLoading = type === 'update';
  
  // Show different styling for questions
  const isQuestion = type === 'question';
  
  return (
    <div className={`chat-message ${role}`}>
      <div className={`message-bubble ${isLoading ? 'loading' : ''} ${isQuestion ? 'question' : ''}`}>
        {isLoading ? (
          <>
            <LoadingSpinner />
            <span>{content}</span>
          </>
        ) : (
          content
        )}
      </div>
    </div>
  );
};

export default ChatMessage;
