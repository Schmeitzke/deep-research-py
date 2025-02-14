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

  // Use Vite's environment variable or fallback
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  /**
   * Immediately add the user's prompt to the chat as the first message,
   * then call /api/feedback to retrieve follow-up questions from the backend.
   */
  useEffect(() => {
    if (!initialPrompt) return;

    // 1) Show the user’s initial prompt in the chat
    setMessages([
      {
        role: 'user',
        type: 'text',
        content: initialPrompt,
      },
    ]);

    // 2) Fetch follow-up questions from the backend
    const getFeedbackQuestions = async () => {
      try {
        const res = await fetch(`${API_URL}/api/feedback`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query: initialPrompt }),
        });
        if (!res.ok) {
          throw new Error(`HTTP error: ${res.status}`);
        }

        const data: { questions: string[] } = await res.json();
        setQuestionQueue(data.questions);

        // Insert the first follow-up question if it exists
        if (data.questions.length > 0) {
          setMessages((prev) => [
            ...prev,
            { role: 'system', type: 'question', content: data.questions[0] },
          ]);
        }
      } catch (err) {
        console.error('Failed to get feedback questions:', err);
        setMessages((prev) => [
          ...prev,
          { role: 'system', type: 'text', content: 'Error fetching follow-up questions.' },
        ]);
      }
    };

    getFeedbackQuestions();
  }, [initialPrompt, API_URL]);

  /**
   * Called after the user has answered the last question.
   * 1) Adds a "Doing research..." message
   * 2) Calls /api/research
   * 3) Shows "Done" + the final report
   */
  const startDeepResearch = async () => {
    // 1) Notify that we’re starting the research
    setMessages((prev) => [
      ...prev,
      { role: 'system', type: 'update', content: 'Doing research...' },
    ]);

    // Combine the user’s initial prompt + answers
    const combinedQuery = [
      `Initial Query: ${initialPrompt}`,
      ...answers.map((ans, i) => `Q${i + 1}: ${questionQueue[i]} | A: ${ans}`),
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

      // 2) Show the final report (only once!)
      setMessages((prev) => [
        ...prev,
        { role: 'system', type: 'finalReport', content: data.final_report },
      ]);
      setFinalReport(data.final_report);

      // 3) Notify that we’re done
      setMessages((prev) => [
        ...prev,
        { role: 'system', type: 'update', content: 'Done' },
      ]);

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
    // Add user’s answer to the chat
    setMessages((prev) => [
      ...prev,
      { role: 'user', type: 'text', content: message },
    ]);
    setAnswers((prev) => [...prev, message]);

    // Move to next question or start the research if done
    setCurrentQuestionIndex((prevIndex) => {
      const nextIndex = prevIndex + 1;
      if (questionQueue[nextIndex]) {
        setMessages((prev) => [
          ...prev,
          { role: 'system', type: 'question', content: questionQueue[nextIndex] },
        ]);
      } else {
        // All questions answered => run deep research
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
