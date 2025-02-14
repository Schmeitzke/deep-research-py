// src/hooks/useChat.ts
import { useEffect, useState, useRef } from 'react';

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

export function useChat(initialPrompt: string, computeMode: 'low' | 'medium' | 'high'): UseChatReturn {
  const [messages, setMessages] = useState<ChatMessageData[]>([]);
  const [questionQueue, setQuestionQueue] = useState<string[]>([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState<number>(0);
  const [answers, setAnswers] = useState<string[]>([]);
  const [isComplete, setIsComplete] = useState<boolean>(false);
  const [finalReport, setFinalReport] = useState<string | null>(null);

  const hasFetchedRef = useRef(false);
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  useEffect(() => {
    if (!initialPrompt || hasFetchedRef.current) return;
    hasFetchedRef.current = true;

    // Show user's initial prompt
    setMessages([
      { role: 'user', type: 'text', content: initialPrompt },
    ]);

    // Get follow-up questions from /api/feedback
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

  // Dynamically map computeMode -> breadth/depth
  const getBreadthDepth = () => {
    switch (computeMode) {
      case 'low':
        return { breadth: 2, depth: 1 };
      case 'high':
        return { breadth: 10, depth: 5 };
      case 'medium':
      default:
        return { breadth: 5, depth: 3 };
    }
  };

  // Called after user answers all follow-up questions
  const startDeepResearch = async () => {
    setMessages((prev) => [
      ...prev,
      { role: 'system', type: 'update', content: 'Doing research...' },
    ]);

    const combinedQuery = [
      `Initial Query: ${initialPrompt}`,
      ...answers.map((ans, i) => `Q${i + 1}: ${questionQueue[i]} | A: ${ans}`),
    ].join('\n');

    const { breadth, depth } = getBreadthDepth();

    try {
      const response = await fetch(`${API_URL}/api/research`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: combinedQuery,
          breadth,
          depth,
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

      setMessages((prev) => [
        ...prev,
        { role: 'system', type: 'finalReport', content: data.final_report },
        { role: 'system', type: 'update', content: 'Done' },
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

  // Called when user enters an answer in ChatScreen
  const sendUserMessage = (message: string) => {
    setMessages((prev) => [
      ...prev,
      { role: 'user', type: 'text', content: message },
    ]);
    setAnswers((prev) => [...prev, message]);

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
