// src/components/ChatList.tsx
import React, { useState, useEffect } from 'react';

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

  return (
    <>
      <style>{`
        .chat-button, .chat-input {
          display: block;
          width: 90%;
          margin: 10px auto;
          border-radius: 4px;
          transition: transform 0.2s ease, background-color 0.2s ease;
          font-size: 1rem;
        }
        .chat-button {
          padding: 8px;
          background-color:rgb(94, 94, 94);
          border: none;
          cursor: pointer;
          color: black;
        }
        .chat-button:hover {
          transform: scale(1.05);
          background-color:rgb(108, 108, 108);
        }
        .chat-input {
          padding: 5px;
          border: 1px solid #ccc;
          background-color: #d3d3d3;
          color: black;
        }
        .chat-input:focus {
          outline: none;
          border-color: #aaa;
        }
      `}</style>
      <div style={{ width: '15%', borderRight: '1px solid #444', padding: '10px', boxSizing: 'border-box', height: '100vh', overflowY: 'auto', backgroundColor: '#222', color: 'white' }}>
        <button
          onClick={onNewChat}
          className="chat-button"
        >
          New chat
        </button>
        <input 
          type="text" 
          placeholder="Search conversations..." 
          value={searchTerm}
          onChange={handleSearchChange}
          className="chat-input"
        />
        {loading ? (
          <div>Loading...</div>
        ) : (
          <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
            {sessions.map(session => (
              <li key={session.id} style={{ marginBottom: '10px' }}>
                <div 
                  style={{ backgroundColor: '#444', padding: '10px', borderRadius: '5px', cursor: 'pointer', color: 'white' }}
                  onClick={() => onSelectChat(session.id)}
                >
                  <div style={{ fontWeight: 'bold' }}>{session.title || "Untitled conversation"}</div>
                  {/* Removed created_at display */}
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </>
  );
};

export default ChatList;
