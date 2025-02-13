import React, { useState } from 'react';

interface PromptScreenProps {
  onStartChat: (prompt: string) => void;
}

const PromptScreen: React.FC<PromptScreenProps> = ({ onStartChat }) => {
  const [prompt, setPrompt] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (prompt.trim().length > 0) {
      onStartChat(prompt.trim());
    }
  };

  return (
    <div className="prompt-screen">
      <h1>What can I help with?</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          className="prompt-input"
          placeholder="Enter your topic or question..."
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
        />
        <button type="submit" className="start-button">
          Start
        </button>
      </form>
    </div>
  );
};

export default PromptScreen;
