import React from 'react';

interface ChatMessageProps {
  content: string;
  role: 'user' | 'system';
}

const ChatMessage: React.FC<ChatMessageProps> = ({ content, role }) => {
  return (
    <div className={`chat-message ${role}`}>
      <div className="message-bubble">
        {content}
      </div>
    </div>
  );
};

export default ChatMessage;
