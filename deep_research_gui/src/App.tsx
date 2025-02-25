// src/App.tsx
import React, { useState } from 'react';
import PromptScreen from './components/PromptScreen';
import ChatScreen from './components/ChatScreen';
import ChatList from './components/ChatList';
import OldChatScreen from './components/OldChatScreen';

const App: React.FC = () => {
  const [initialPrompt, setInitialPrompt] = useState<string | null>(null);
  const [computeMode, setComputeMode] = useState<'low' | 'medium' | 'high'>('medium');
  const [selectedSessionId, setSelectedSessionId] = useState<number | null>(null);

  const handleStartChat = (prompt: string, mode: 'low' | 'medium' | 'high') => {
    setInitialPrompt(prompt);
    setComputeMode(mode);
    setSelectedSessionId(null);
  };

  const handleSelectChat = (sessionId: number) => {
    setSelectedSessionId(sessionId);
    setInitialPrompt(null);
  };

  // New handler for "New chat" button
  const handleNewChat = () => {
    setInitialPrompt(null);
    setSelectedSessionId(null);
  };

  return (
    <div className="app-container">
      <ChatList onSelectChat={handleSelectChat} onNewChat={handleNewChat} />
      <main className="app-main">
        {selectedSessionId ? (
          <OldChatScreen sessionId={selectedSessionId} />
        ) : (
          !initialPrompt ? (
            <PromptScreen onStartChat={handleStartChat} />
          ) : (
            <ChatScreen initialPrompt={initialPrompt} computeMode={computeMode} />
          )
        )}
      </main>
    </div>
  );
};

export default App;
