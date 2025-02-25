// src/components/OldChatScreen.tsx
import React, { useRef, useEffect } from 'react';
import { useChatSession } from '../hooks/useChatSession';
import ChatMessage from './ChatMessage';
import MarkdownMessage from './MarkdownMessage';
import LoadingSpinner from './LoadingSpinner';

interface OldChatScreenProps {
  sessionId: number;
}

const OldChatScreen: React.FC<OldChatScreenProps> = ({ sessionId }) => {
  const { session, loading } = useChatSession(sessionId);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom when session loads
  useEffect(() => {
    if (session && !loading) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'auto' });
    }
  }, [session, loading]);

  if (loading) {
    return (
      <div className="chat-screen">
        <div className="chat-loading">
          <LoadingSpinner message="Loading conversation..." />
        </div>
      </div>
    );
  }

  if (!session) {
    return (
      <div className="chat-screen">
        <div className="chat-error">
          <h3>Conversation not found</h3>
          <p>The conversation you're looking for couldn't be loaded.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="chat-screen">
      <div className="chat-header">
        <h2>{session.title || "Untitled conversation"}</h2>
        <div className="chat-date">
          {new Date(session.created_at).toLocaleDateString([], {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
          })}
        </div>
      </div>
      <div className="chat-messages">
        {session.messages.map((msg, index) => {
          // Handle markdown content if it looks like markdown
          const hasMarkdown = 
            msg.content.includes('##') || 
            msg.content.includes('```') || 
            msg.content.includes('*') ||
            (msg.content.includes('[') && msg.content.includes(']('));
          
          return hasMarkdown ? (
            <MarkdownMessage key={index} markdown={msg.content} role={msg.role} />
          ) : (
            <ChatMessage key={index} content={msg.content} role={msg.role} />
          );
        })}
        <div ref={messagesEndRef} />
      </div>
      <div className="chat-input history-mode">
        <div className="history-notice">
          Viewing past conversation - Start a new chat to ask more questions
        </div>
      </div>
    </div>
  );
};

export default OldChatScreen;
