import { useEffect, useState } from 'react';

// Types of messages in the chat
export interface ChatMessageData {
  role: 'user' | 'system';
  type: 'text' | 'question' | 'update' | 'finalReport';
  content: string;
}

interface UseChatReturn {
  messages: ChatMessageData[];
  sendUserMessage: (message: string) => void;
  isComplete: boolean;
  finalReport: string | null;
}

export function useChat(initialPrompt: string): UseChatReturn {
  const [messages, setMessages] = useState<ChatMessageData[]>([]);
  const [isComplete, setIsComplete] = useState<boolean>(false);
  const [finalReport, setFinalReport] = useState<string | null>(null);
  const [questionQueue, setQuestionQueue] = useState<string[]>([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState<number>(0);

  // Mock function to simulate the “deep research” process:
  // 1) Return some follow-up questions
  // 2) Show some progress updates
  // 3) Return a final report
  const mockDeepResearchInit = async (prompt: string) => {
    // In reality, call your Python backend here
    // e.g. const response = await fetch('/api/initResearch', { ... })
    // Then parse the JSON with follow-up questions, etc.
    return {
      questions: [
        "What is your main objective with this research?",
        "Do you have any specific subtopics you want explored?"
      ]
    };
  };

  const mockDeepResearchProgress = async () => {
    // Another mock function that might be called after all questions are answered
    // to produce progress updates or the final report
    return {
      updates: [
        "Gathering resources from multiple search endpoints...",
        "Analyzing data for relevant insights..."
      ],
      finalReport: `
# Final Report

This is the final markdown report from the deep research process.

- Item 1
- Item 2
- **Bold** and *italic* text

\`\`\`python
# Sample code block
print("Hello from the final report")
\`\`\`

      `
    };
  };

  // Initialize the conversation by sending the initial prompt to the system
  useEffect(() => {
    (async () => {
      // The user has provided an initial prompt
      setMessages((prev) => [
        ...prev,
        { role: 'user', type: 'text', content: initialPrompt }
      ]);

      // The system responds with follow-up questions
      const { questions } = await mockDeepResearchInit(initialPrompt);
      setQuestionQueue(questions);

      // Display the first question
      if (questions.length > 0) {
        setMessages((prev) => [
          ...prev,
          { role: 'system', type: 'question', content: questions[0] }
        ]);
      }
    })();
  }, [initialPrompt]);

  // Function to handle user responses
  const sendUserMessage = (message: string) => {
    // Add user's message to chat
    setMessages((prev) => [
      ...prev,
      { role: 'user', type: 'text', content: message }
    ]);

    // Move to next question or proceed to final steps
    setCurrentQuestionIndex((prevIndex) => {
      const nextIndex = prevIndex + 1;
      if (questionQueue[nextIndex]) {
        // If there is another question, show it
        setMessages((prev) => [
          ...prev,
          {
            role: 'system',
            type: 'question',
            content: questionQueue[nextIndex]
          }
        ]);
      } else {
        // No more questions -> simulate progress updates and final report
        simulateProgressAndReport();
      }
      return nextIndex;
    });
  };

  // Simulate receiving progress messages and final report
  const simulateProgressAndReport = async () => {
    const { updates, finalReport } = await mockDeepResearchProgress();

    // Display updates
    for (const update of updates) {
      await new Promise((resolve) => setTimeout(resolve, 1000));
      setMessages((prev) => [
        ...prev,
        { role: 'system', type: 'update', content: update }
      ]);
    }

    // Display final report
    setMessages((prev) => [
      ...prev,
      { role: 'system', type: 'finalReport', content: finalReport }
    ]);
    setFinalReport(finalReport);
    setIsComplete(true);
  };

  return {
    messages,
    sendUserMessage,
    isComplete,
    finalReport
  };
}
