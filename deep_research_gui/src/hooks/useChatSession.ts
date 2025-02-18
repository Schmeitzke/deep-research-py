// src/hooks/useChatSession.ts
import { useEffect, useState } from 'react';

export interface ChatMessageData {
  role: 'user' | 'system';
  content: string;
  created_at: string;
}

export interface ChatSessionData {
  id: number;
  title: string;
  created_at: string;
  messages: ChatMessageData[];
}

export function useChatSession(sessionId: number) {
  const [session, setSession] = useState<ChatSessionData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  useEffect(() => {
    async function fetchSession() {
      try {
        const response = await fetch(`${API_URL}/api/chat/get/${sessionId}/`);
        const data = await response.json();
        setSession(data.session);
      } catch (error) {
        console.error("Error fetching chat session", error);
      } finally {
        setLoading(false);
      }
    }
    fetchSession();
  }, [sessionId, API_URL]);

  return { session, loading };
}
