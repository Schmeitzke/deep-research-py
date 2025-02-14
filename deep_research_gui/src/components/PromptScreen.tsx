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

  return (
    <div className="prompt-screen">
      <h1 className="prompt-title">What can I help with?</h1>
      <form onSubmit={handleSubmit} className="prompt-form">
        <div className="prompt-box">
          {/* Changed input to textarea for multi-line support */}
          <textarea
            className="prompt-input"
            placeholder="Ask me anything..."
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            rows={3}
          />
          <button type="submit" className="prompt-submit-btn">
            {/* Upward arrow inside a circle */}
            <svg viewBox="0 0 24 24" fill="none" width="24" height="24">
              <circle cx="12" cy="12" r="10" fill="#2b81f6" />
              <path
                d="M12 7L12 17M12 7L7 12M12 7L17 12"
                stroke="#fff"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </button>
        </div>
      </form>
    </div>
  );
};

export default PromptScreen;
