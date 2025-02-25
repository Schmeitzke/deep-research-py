// src/components/ChatList.tsx
import React, { useState, useEffect } from 'react';
import LoadingSpinner from './LoadingSpinner';

interface ChatSessionItem {
  id: number;
  title: string;
  created_at: string;
}

interface ChatListProps {
  onSelectChat: (sessionId: number) => void;
  onNewChat: () => void;
}

const ChatList: React.FC<ChatListProps> = ({ onSelectChat, onNewChat }) => {
  const [sessions, setSessions] = useState<ChatSessionItem[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  const fetchSessions = async (search: string = '') => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/api/chat/list/?search=${encodeURIComponent(search)}`);
      const data = await response.json();
      setSessions(data.sessions);
    } catch (error) {
      console.error("Error fetching sessions", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSessions();
  }, []);

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const term = e.target.value;
    setSearchTerm(term);
    fetchSessions(term);
  };

  // Format date to a more readable format
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const today = new Date();
    
    // If today, show only time
    if (date.toDateString() === today.toDateString()) {
      return `Today at ${date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
    }
    
    // If this year, show month and day
    if (date.getFullYear() === today.getFullYear()) {
      return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
    }
    
    // Otherwise show full date
    return date.toLocaleDateString([], { year: 'numeric', month: 'short', day: 'numeric' });
  };

  return (
    <div className="chat-sidebar">
      <div className="sidebar-header">
        <h2 className="sidebar-title">Deep Research</h2>
      </div>

      <button 
        onClick={onNewChat}
        className="new-chat-button"
      >
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M8 3.33337V12.6667" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
          <path d="M3.33337 8H12.6667" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
        </svg>
        New Chat
      </button>

      <div className="chat-search">
        <input 
          type="text" 
          placeholder="Search conversations..." 
          value={searchTerm}
          onChange={handleSearchChange}
        />
      </div>

      {loading ? (
        <div style={{ padding: '20px', textAlign: 'center' }}>
          <LoadingSpinner message="Loading conversations..." />
        </div>
      ) : (
        <ul className="chat-list">
          {sessions.length === 0 ? (
            <li className="empty-state">No conversations found</li>
          ) : (
            sessions.map(session => (
              <li key={session.id} className="chat-list-item">
                <div 
                  className="chat-list-item-content"
                  onClick={() => onSelectChat(session.id)}
                >
                  <div className="chat-list-item-title">{session.title || "Untitled conversation"}</div>
                  <div className="chat-list-item-date">{formatDate(session.created_at)}</div>
                </div>
              </li>
            ))
          )}
        </ul>
      )}
    </div>
  );
};

export default ChatList;
