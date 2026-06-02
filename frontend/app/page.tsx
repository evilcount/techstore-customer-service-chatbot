"use client";

import { FormEvent, useState } from "react";

import { createSession, sendMessage, validateDemoPassword } from "../lib/api";

type ChatMessage = {
  role: "user" | "assistant";
  content: string;
};

const demoEmails = [
  "john.doe@company.com",
  "sarah.smith@company.com",
  "emily.brown@company.com",
];

export default function Home() {
  const [demoPassword, setDemoPassword] = useState("");
  const [isAuthed, setIsAuthed] = useState(false);
  const [customerEmail, setCustomerEmail] = useState("");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  async function handlePasswordSubmit(event: FormEvent) {
    event.preventDefault();
    setError("");
    try {
      await validateDemoPassword(demoPassword);
      setIsAuthed(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Invalid password");
    }
  }

  async function ensureSession() {
    if (sessionId) {
      return sessionId;
    }
    const session = await createSession(customerEmail, demoPassword);
    setSessionId(session.session_id);
    return session.session_id;
  }

  async function handleMessageSubmit(event: FormEvent) {
    event.preventDefault();
    if (!customerEmail || !message.trim()) {
      return;
    }

    const userMessage = message.trim();
    setMessage("");
    setMessages((current) => [...current, { role: "user", content: userMessage }]);
    setIsLoading(true);
    setError("");

    try {
      const activeSessionId = await ensureSession();
      const response = await sendMessage(activeSessionId, userMessage, demoPassword);
      setMessages((current) => [
        ...current,
        { role: "assistant", content: response.assistant_message },
      ]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not send message");
    } finally {
      setIsLoading(false);
    }
  }

  if (!isAuthed) {
    return (
      <main className="auth-shell">
        <section className="auth-panel">
          <p className="eyebrow">TechStore Plus</p>
          <h1>Support Chat Demo</h1>
          <form onSubmit={handlePasswordSubmit}>
            <label htmlFor="password">Demo password</label>
            <input
              id="password"
              type="password"
              value={demoPassword}
              onChange={(event) => setDemoPassword(event.target.value)}
              placeholder="Enter demo password"
            />
            <button type="submit">Enter demo</button>
          </form>
          {error ? <p className="error">{error}</p> : null}
        </section>
      </main>
    );
  }

  return (
    <main className="chat-shell">
      <section className="sidebar">
        <p className="eyebrow">TechStore Plus</p>
        <h1>Support</h1>
        <label htmlFor="email">Customer email</label>
        <input
          id="email"
          value={customerEmail}
          onChange={(event) => {
            setCustomerEmail(event.target.value);
            setSessionId(null);
            setMessages([]);
          }}
          placeholder="new.customer@example.com"
        />
        <div className="demo-list">
          {demoEmails.map((email) => (
            <button
              key={email}
              type="button"
              onClick={() => {
                setCustomerEmail(email);
                setSessionId(null);
                setMessages([]);
              }}
            >
              {email}
            </button>
          ))}
        </div>
      </section>

      <section className="chat-panel">
        <div className="messages">
          {messages.length === 0 ? (
            <div className="empty-state">
              Enter any customer email and start a support conversation.
            </div>
          ) : (
            messages.map((chatMessage, index) => (
              <div key={`${chatMessage.role}-${index}`} className={`bubble ${chatMessage.role}`}>
                {chatMessage.content}
              </div>
            ))
          )}
          {isLoading ? <div className="bubble assistant">Agent is typing...</div> : null}
        </div>

        <form className="composer" onSubmit={handleMessageSubmit}>
          <input
            value={message}
            onChange={(event) => setMessage(event.target.value)}
            placeholder="Type your message..."
            disabled={!customerEmail || isLoading}
          />
          <button type="submit" disabled={!customerEmail || !message.trim() || isLoading}>
            Send
          </button>
        </form>
        {error ? <p className="error">{error}</p> : null}
      </section>
    </main>
  );
}
