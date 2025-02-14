// src/App.tsx
import React, { useState } from 'react';
import PromptScreen from './components/PromptScreen';
import ChatScreen from './components/ChatScreen';

function App() {
  const [initialPrompt, setInitialPrompt] = useState<string | null>(null);
  const [computeMode, setComputeMode] = useState<'low' | 'medium' | 'high'>('medium');

  const handleStartChat = (prompt: string, mode: 'low' | 'medium' | 'high') => {
    setInitialPrompt(prompt);
    setComputeMode(mode);
  };

  return (
    <div className="app-container">
      {!initialPrompt ? (
        <PromptScreen onStartChat={handleStartChat} />
      ) : (
        <ChatScreen
          initialPrompt={initialPrompt}
          computeMode={computeMode}
        />
      )}
    </div>
  );
}

export default App;
