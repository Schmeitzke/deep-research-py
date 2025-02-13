import React, { useState } from 'react';
import PromptScreen from './components/PromptScreen';
import ChatScreen from './components/ChatScreen';

function App() {
  const [initialPrompt, setInitialPrompt] = useState<string | null>(null);

  const handleStartChat = (prompt: string) => {
    setInitialPrompt(prompt);
  };

  return (
    <div className="app-container">
      {!initialPrompt ? (
        <PromptScreen onStartChat={handleStartChat} />
      ) : (
        <ChatScreen initialPrompt={initialPrompt} />
      )}
    </div>
  );
}

export default App;
