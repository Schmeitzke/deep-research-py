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
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          components={{
            // Add proper styling for code blocks
            code: ({ node, inline, className, children, ...props }) => {
              const match = /language-(\w+)/.exec(className || '');
              return !inline ? (
                <pre className={match ? `language-${match[1]}` : ''}>
                  <code className={className} {...props}>
                    {children}
                  </code>
                </pre>
              ) : (
                <code className={className} {...props}>
                  {children}
                </code>
              );
            }
          }}
        >
          {markdown}
        </ReactMarkdown>
      </div>
    </div>
  );
};

export default MarkdownMessage;
