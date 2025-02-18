// src/hooks/useChat.ts
import { useEffect, useState, useRef } from 'react';
import { flushSync } from 'react-dom';

export interface ChatMessageData {
  role: 'user' | 'system';
  type: 'text' | 'question' | 'update' | 'finalReport';
  content: string;
}

interface UseChatReturn {
  messages: ChatMessageData[];
  sendUserMessage: (message: string) => Promise<void>;
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

  // A ref to ensure research starts only once.
  const researchStartedRef = useRef(false);
  const hasFetchedRef = useRef(false);
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001';

  // Helper: update or add an "update" message.
  const updateProgressMessage = (newContent: string) => {
    setMessages(prev => {
      const index = prev.findIndex(m => m.type === 'update');
      if (index !== -1) {
        const updated = [...prev];
        updated[index] = { ...updated[index], content: newContent };
        return updated;
      } else {
        return [...prev, { role: 'system', type: 'update', content: newContent }];
      }
    });
  };

  useEffect(() => {
    if (!initialPrompt || hasFetchedRef.current) return;
    hasFetchedRef.current = true;

    // Display the user's initial prompt.
    setMessages([{ role: 'user', type: 'text', content: initialPrompt }]);

    // Use streaming endpoint to fetch follow-up questions.
    const getFollowUpQuestions = async () => {
      try {
        const res = await fetch(`${API_URL}/api/follow_up_stream`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query: initialPrompt }),
        });
        if (!res.ok) throw new Error(`HTTP error: ${res.status}`);
        const reader = res.body?.getReader();
        const decoder = new TextDecoder("utf-8");
        let buffer = "";
        let questions: string[] = [];
        while (true) {
          const { done, value } = await reader!.read();
          if (done) break;
          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n\n");
          buffer = lines.pop() || "";
          for (let line of lines) {
            if (line.startsWith("data: ")) {
              const jsonStr = line.replace("data: ", "");
              const eventData = JSON.parse(jsonStr);
              if (eventData.type === 'progress') {
                const content = `${eventData.data.stage}: ${eventData.data.message}`;
                updateProgressMessage(content);
              } else if (eventData.type === 'final') {
                questions = eventData.data.questions;
                // Remove the progress message.
                setMessages(prev => prev.filter(m => m.type !== 'update'));
              } else if (eventData.type === 'error') {
                updateProgressMessage(`Error: ${eventData.data}`);
              }
            }
          }
        }
        setQuestionQueue(questions);
        if (questions.length > 0) {
          setMessages(prev => [
            ...prev,
            { role: 'system', type: 'question', content: questions[0] },
          ]);
        }
      } catch (err) {
        console.error('Failed to get follow-up questions:', err);
        setMessages(prev => [
          ...prev,
          { role: 'system', type: 'text', content: 'Error fetching follow-up questions.' },
        ]);
      }
    };

    getFollowUpQuestions();
  }, [initialPrompt, API_URL]);

  // Map computeMode to research parameters.
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

  // Function to initiate the deep research process using streaming updates.
  const startDeepResearch = async () => {
    const combinedQuery = [
      `Initial Query: ${initialPrompt}`,
      ...answers.map((ans, i) => `Q${i + 1}: ${questionQueue[i]} | A: ${ans}`),
    ].join('\n');

    const { breadth, depth } = getBreadthDepth();

    try {
      const response = await fetch(`${API_URL}/api/research_stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: combinedQuery,
          breadth,
          depth,
          concurrency: 2,
        }),
      });
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const reader = response.body?.getReader();
      const decoder = new TextDecoder("utf-8");
      let buffer = "";
      while (true) {
        const { done, value } = await reader!.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n\n");
        buffer = lines.pop() || "";
        for (let line of lines) {
          if (line.startsWith("data: ")) {
            const jsonStr = line.replace("data: ", "");
            const eventData = JSON.parse(jsonStr);
            if (eventData.type === 'progress') {
              const content = `Progress: ${eventData.data.percentage}% | Elapsed: ${eventData.data.elapsed}s | Remaining: ${eventData.data.remaining}s`;
              updateProgressMessage(content);
            } else if (eventData.type === 'final') {
              setMessages(prev => prev.filter(m => m.type !== 'update'));
              setMessages(prev => [
                ...prev,
                { role: 'system', type: 'finalReport', content: eventData.data.final_report },
                { role: 'system', type: 'text', content: 'Done' },
              ]);
              setFinalReport(eventData.data.final_report);
              setIsComplete(true);
            }            
          }
        }
      }
    } catch (error) {
      console.error('Error fetching research results:', error);
      setMessages(prev => [
        ...prev,
        { role: 'system', type: 'finalReport', content: 'Error fetching research results.' },
      ]);
      setFinalReport('Error fetching research results.');
      setIsComplete(true);
    }
  };

  // Convert sendUserMessage into an async function.
  const sendUserMessage = async (message: string) => {
    // Append the user's message.
    setMessages(prev => [
      ...prev,
      { role: 'user', type: 'text', content: message },
    ]);
    setAnswers(prev => [...prev, message]);

    const nextIndex = currentQuestionIndex + 1;

    if (questionQueue[nextIndex]) {
      // Display the next follow-up question.
      setMessages(prev => [
        ...prev,
        { role: 'system', type: 'question', content: questionQueue[nextIndex] },
      ]);
    } else if (!researchStartedRef.current) {
      researchStartedRef.current = true;
      // Synchronously update with an initial "Doing research..." progress message.
      flushSync(() => {
        setMessages(prev => [
          ...prev,
          { role: 'system', type: 'update', content: 'Doing research...' },
        ]);
      });
      // Start the research process with progress streaming.
      startDeepResearch();
    }
    setCurrentQuestionIndex(nextIndex);
  };

  return {
    messages,
    sendUserMessage,
    isComplete,
    finalReport,
  };
}
