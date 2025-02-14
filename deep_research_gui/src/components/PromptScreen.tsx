import React, { useState } from 'react';
import '../styles/PromptScreen.css';

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

  // New handler for Enter key submission
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      // Create a synthetic event to pass to handleSubmit
      handleSubmit(e as unknown as React.FormEvent);
    }
  };

  return (
    <div className="prompt-screen">
      <div className="prompt-header">
        <h1 className="prompt-title">What can I help with?</h1>
      </div>
      <div className="prompt-form-container">
        <form onSubmit={handleSubmit} className="prompt-form">
          {/* Changed input to textarea for multi-line support */}
          <textarea
            className="prompt-input"
            placeholder="Ask me anything..."
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            rows={3}
            onKeyDown={handleKeyDown}  // New onKeyDown handler added
          />
          <button type="submit" className="prompt-submit-btn">
            <svg viewBox="0 0 36 36" fill="none" width="36" height="36">
              <circle cx="18" cy="18" r="16" fill="#2b81f6" />
              <path
                d="M18 10L18 26M18 10L10 18M18 10L26 18"
                stroke="#fff"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </button>
        </form>
      </div>
    </div>
  );
};

export default PromptScreen;
