// src/components/ChatScreen.tsx
import React, { useState, useRef, useEffect } from 'react';
import { useChat, ChatMessageData } from '../hooks/useChat';
import ChatMessage from './ChatMessage';
import MarkdownMessage from './MarkdownMessage';

interface ChatScreenProps {
  initialPrompt: string;
  computeMode: 'low' | 'medium' | 'high';
}

const ChatScreen: React.FC<ChatScreenProps> = ({ initialPrompt, computeMode }) => {
  const {
    messages,
    sendUserMessage,
    isComplete,
    finalReport
  } = useChat(initialPrompt, computeMode);

  const [userInput, setUserInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Auto-resize the textarea based on content
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = '24px';
      const scrollHeight = textareaRef.current.scrollHeight;
      textareaRef.current.style.height = `${Math.min(scrollHeight, 120)}px`;
    }
  }, [userInput]);

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = userInput.trim();
    if (trimmed.length > 0) {
      sendUserMessage(trimmed);
      setUserInput('');
      // Reset textarea height
      if (textareaRef.current) {
        textareaRef.current.style.height = '24px';
      }
    }
  };

  return (
    <div className="chat-screen">
      <div className="chat-messages">
        {messages.map((msg: ChatMessageData, index: number) => {
          if (msg.type === 'finalReport') {
            return (
              <MarkdownMessage key={index} markdown={msg.content} role="system" />
            );
          }
          return (
            <ChatMessage key={index} content={msg.content} role={msg.role} type={msg.type} />
          );
        })}
        <div ref={messagesEndRef} />
      </div>
      <form onSubmit={handleSend} className="chat-input">
        <textarea
          ref={textareaRef}
          placeholder={isComplete ? "Research complete" : "Type your message..."}
          value={userInput}
          onChange={(e) => setUserInput(e.target.value)}
          disabled={isComplete}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              handleSend(e);
            }
          }}
        />
        <button type="submit" disabled={isComplete || !userInput.trim()}>
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M15 8L1 15L3.5 8L1 1L15 8Z" stroke="currentColor" fill="currentColor" />
          </svg>
        </button>
      </form>
    </div>
  );
};

export default ChatScreen;
