// src/api/saveChat.ts
/**
 * Saves a chat session to the backend.
 * Expects an object with a session title and an array of message objects.
 */
export async function saveChatSession(sessionData: {
    title: string;
    messages: { role: string; content: string }[];
  }): Promise<any> {
    const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    const response = await fetch(`${API_URL}/api/chat/save_chat/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ session: sessionData })
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
  }
  