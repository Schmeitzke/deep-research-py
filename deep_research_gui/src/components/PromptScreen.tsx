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

  // Map compute mode to research labels and descriptions
  const computeOptions = {
    low: {
      label: 'Quick Research',
      description: 'Fast results with basic research',
      color: '#10b981' // green
    },
    medium: {
      label: 'Balanced Research',
      description: 'Good balance of speed and depth',
      color: '#f59e0b' // amber
    },
    high: {
      label: 'Deep Research',
      description: 'Thorough analysis with comprehensive results',
      color: '#ef4444' // red
    }
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
        <h1 className="prompt-title">Deep Research Assistant</h1>
        <p className="prompt-subtitle">
          Ask a question or describe a topic you'd like to research in-depth
        </p>
      </div>
      
      <div className="prompt-form-container">
        <form onSubmit={handleSubmit} className="prompt-form">
          <div className="prompt-input-container">
            <textarea
              className="prompt-input"
              placeholder="Ask me anything..."
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              onKeyDown={handleKeyDown}
            />
            
            <div className="compute-section">
              <button
                type="button"
                className="compute-button"
                onClick={toggleComputeOptions}
                style={{ borderColor: computeOptions[computeMode].color, color: computeOptions[computeMode].color }}
              >
                {computeOptions[computeMode].label}
              </button>
              
              {showComputeOptions && (
                <div className="compute-dropdown">
                  <button 
                    type="button" 
                    onClick={() => selectComputeMode('low')}
                    data-mode="low"
                  >
                    Quick Research
                  </button>
                  <button 
                    type="button" 
                    onClick={() => selectComputeMode('medium')}
                    data-mode="medium"
                  >
                    Balanced Research
                  </button>
                  <button 
                    type="button" 
                    onClick={() => selectComputeMode('high')}
                    data-mode="high"
                  >
                    Deep Research
                  </button>
                </div>
              )}
            </div>
          </div>

          <button 
            type="submit" 
            className="prompt-submit-btn"
            disabled={!prompt.trim()}
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M5 12H19M19 12L12 5M19 12L12 19" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
        </form>
      </div>
      
      <div className="prompt-help">
        <svg className="prompt-help-icon" viewBox="0 0 20 20" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
          <path fillRule="evenodd" clipRule="evenodd" d="M18 10C18 14.4183 14.4183 18 10 18C5.58172 18 2 14.4183 2 10C2 5.58172 5.58172 2 10 2C14.4183 2 18 5.58172 18 10ZM11 6C11 6.55228 10.5523 7 10 7C9.44772 7 9 6.55228 9 6C9 5.44772 9.44772 5 10 5C10.5523 5 11 5.44772 11 6ZM9 9C8.44772 9 8 9.44772 8 10C8 10.5523 8.44772 11 9 11V14C9 14.5523 9.44772 15 10 15H11C11.5523 15 12 14.5523 12 14C12 13.4477 11.5523 13 11 13V10C11 9.44772 10.5523 9 10 9H9Z" />
        </svg>
        Choose a research depth that fits your needs
      </div>
    </div>
  );
};

export default PromptScreen;
