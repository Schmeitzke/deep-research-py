import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface MarkdownMessageProps {
  markdown: string;
  role: 'user' | 'system';
}

const MarkdownMessage: React.FC<MarkdownMessageProps> = ({ markdown, role }) => {
  return (
    <div className={`chat-message ${role}`}>
      <div className="message-bubble markdown-content">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>
          {markdown}
        </ReactMarkdown>
      </div>
    </div>
  );
};

export default MarkdownMessage;
