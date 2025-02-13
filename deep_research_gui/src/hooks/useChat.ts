// src/hooks/useChat.ts
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
  const [questionQueue, setQuestionQueue] = useState<string[]>([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState<number>(0);
  const [answers, setAnswers] = useState<string[]>([]);
  const [isComplete, setIsComplete] = useState<boolean>(false);
  const [finalReport, setFinalReport] = useState<string | null>(null);

  // We'll define the API URL for local dev via .env => VITE_API_URL
  // or fallback to http://localhost:8000
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  /**
   * 1) Immediately call /api/feedback to get real follow-up questions.
   * 2) Insert the first question into the chat.
   */
  useEffect(() => {
    if (!initialPrompt) return;

    const getFeedbackQuestions = async () => {
      try {
        // Call /api/feedback with the user's prompt
        const res = await fetch(`${API_URL}/api/feedback`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query: initialPrompt }),
        });
        if (!res.ok) {
          throw new Error(`HTTP error: ${res.status}`);
        }

        // Response is { questions: string[] }
        const data: { questions: string[] } = await res.json();

        // Store the question queue
        setQuestionQueue(data.questions);

        // Display the first question if available
        if (data.questions.length > 0) {
          setMessages((prev) => [
            ...prev,
            { role: 'system', type: 'question', content: data.questions[0] },
          ]);
        }
      } catch (err) {
        console.error('Failed to get feedback questions:', err);
        // Optionally display an error message in the chat
        setMessages((prev) => [
          ...prev,
          { role: 'system', type: 'text', content: 'Error fetching follow-up questions.' },
        ]);
      }
    };

    // Fire it once
    getFeedbackQuestions();
  }, [initialPrompt, API_URL]);

  /**
   * Called after the user has answered the last question.
   * This function sends the combined prompt + answers to /api/research
   * and then displays the final report in the chat.
   */
  const startDeepResearch = async () => {
    // Combine the user’s initial prompt + answers
    const combinedQuery = [
      `Initial Query: ${initialPrompt}`,
      ...answers.map((ans, i) => `Q${i+1}: ${questionQueue[i]} | A: ${ans}`),
    ].join('\n');

    try {
      const response = await fetch(`${API_URL}/api/research`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: combinedQuery,
          breadth: 4,
          depth: 2,
          concurrency: 2,
        }),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data: {
        learnings: string[];
        visited_urls: string[];
        final_report: string;
      } = await response.json();

      // Display the final report in the chat
      setMessages((prev) => [
        ...prev,
        { role: 'system', type: 'finalReport', content: data.final_report },
      ]);
      setFinalReport(data.final_report);
      setIsComplete(true);
    } catch (error) {
      console.error('Error fetching research results:', error);
      setMessages((prev) => [
        ...prev,
        { role: 'system', type: 'finalReport', content: 'Error fetching research results.' },
      ]);
      setFinalReport('Error fetching research results.');
      setIsComplete(true);
    }
  };

  /**
   * The user typed an answer to the current question and hit "Send".
   * We store that answer, then move on to the next question (if any).
   * If there are no more questions, we start deep research.
   */
  const sendUserMessage = (message: string) => {
    // Append user’s answer to the chat
    setMessages((prev) => [
      ...prev,
      { role: 'user', type: 'text', content: message },
    ]);
    // Store the answer
    setAnswers((prev) => [...prev, message]);

    // Move to the next question
    setCurrentQuestionIndex((prevIndex) => {
      const nextIndex = prevIndex + 1;
      // If we still have more questions, show the next question
      if (questionQueue[nextIndex]) {
        setMessages((prev) => [
          ...prev,
          { role: 'system', type: 'question', content: questionQueue[nextIndex] },
        ]);
      } else {
        // No more questions => run deep research
        startDeepResearch();
      }
      return nextIndex;
    });
  };

  return {
    messages,
    sendUserMessage,
    isComplete,
    finalReport,
  };
}
