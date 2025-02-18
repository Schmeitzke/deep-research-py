// src/components/OldChatScreen.tsx
import React from 'react';
import { useChatSession } from '../hooks/useChatSession';
import ChatMessage from './ChatMessage';
import LoadingSpinner from './LoadingSpinner';

interface OldChatScreenProps {
  sessionId: number;
}

const OldChatScreen: React.FC<OldChatScreenProps> = ({ sessionId }) => {
  const { session, loading } = useChatSession(sessionId);

  if (loading) {
    return <div style={{ padding: '20px', color: 'white' }}><LoadingSpinner /> Loading conversation...</div>;
  }

  if (!session) {
    return <div style={{ padding: '20px', color: 'white' }}>Conversation not found.</div>;
  }

  return (
    <div style={{ padding: '20px', overflowY: 'auto', height: '100%', color: 'white' }}>
      <h2>{session.title}</h2>
      {session.messages.map((msg, index) => (
        <ChatMessage key={index} content={msg.content} role={msg.role} />
      ))}
    </div>
  );
};

export default OldChatScreen;
