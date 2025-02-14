// src/components/PromptScreen.tsx
import React, { useState } from 'react';
import '../styles/PromptScreen.css';

interface PromptScreenProps {
  onStartChat: (prompt: string, computeMode: 'low' | 'medium' | 'high') => void;
}

const PromptScreen: React.FC<PromptScreenProps> = ({ onStartChat }) => {
  const [prompt, setPrompt] = useState('');
  const [computeMode, setComputeMode] = useState<'low' | 'medium' | 'high'>('medium');
  const [showComputeOptions, setShowComputeOptions] = useState(false);

  // Map compute mode to research labels
  const computeLabels = {
    low: 'Quick Research',
    medium: 'Balanced Research',
    high: 'Deep Research'
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (prompt.trim().length > 0) {
      onStartChat(prompt.trim(), computeMode);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as unknown as React.FormEvent);
    }
  };

  const toggleComputeOptions = () => {
    setShowComputeOptions(!showComputeOptions);
  };

  const selectComputeMode = (mode: 'low' | 'medium' | 'high') => {
    setComputeMode(mode);
    setShowComputeOptions(false);
  };

  return (
    <div className="prompt-screen">
      <div className="prompt-header">
        <h1 className="prompt-title">What can I help you with?</h1>
      </div>
      <div className="prompt-form-container">
        <form onSubmit={handleSubmit} className="prompt-form">
          <div className="prompt-input-container">
            <textarea
              className="prompt-input"
              placeholder="Ask me anything..."
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              rows={3}
              onKeyDown={handleKeyDown}
            />
            <div className="compute-section">
              <button
                type="button"
                className="compute-button"
                onClick={toggleComputeOptions}
              >
                {computeLabels[computeMode]}
              </button>
              {showComputeOptions && (
                <div className="compute-dropdown">
                  <button type="button" onClick={() => selectComputeMode('low')}>
                    Quick Research
                  </button>
                  <button type="button" onClick={() => selectComputeMode('medium')}>
                    Balanced Research
                  </button>
                  <button type="button" onClick={() => selectComputeMode('high')}>
                    Deep Research
                  </button>
                </div>
              )}
            </div>
          </div>

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
