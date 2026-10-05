import { useState, useRef, useEffect } from 'react';
import { Send, User, Bot, Loader2 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

const API_BASE = 'http://localhost:8000/api';

export default function Chat({ meetingId }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const res = await fetch(`${API_BASE}/meetings/${meetingId}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: userMessage.content, history: [] })
      });
      
      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || 'Failed to get answer');
      }
      const data = await res.json();
      
      setMessages(prev => [...prev, { role: 'assistant', content: data.answer }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'assistant', content: `Error: ${err.message}` }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{display: 'flex', flexDirection: 'column', height: '100%', minHeight: '400px'}}>
      <div className="chat-history" style={{flex: 1, overflowY: 'auto'}}>
        {messages.length === 0 && (
          <p className="text-muted" style={{textAlign: 'center', marginTop: '2rem'}}>
            Ask anything about the meeting...
          </p>
        )}
        {messages.map((msg, idx) => (
          <div key={idx} className={`chat-msg ${msg.role}`}>
            <div style={{display: 'flex', gap: '0.5rem', marginBottom: '0.5rem', alignItems: 'center'}}>
              {msg.role === 'user' ? <User size={16} /> : <Bot size={16} />}
              <strong>{msg.role === 'user' ? 'You' : 'AI Assistant'}</strong>
            </div>
            <ReactMarkdown>{msg.content}</ReactMarkdown>
          </div>
        ))}
        {loading && (
          <div className="chat-msg assistant">
            <Loader2 style={{animation: 'spin 1s linear infinite'}} size={20} />
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      
      <form className="chat-input-area" onSubmit={handleSend} style={{marginTop: 'auto'}}>
        <input 
          type="text" 
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question..."
          disabled={loading}
        />
        <button type="submit" className="primary-btn" disabled={loading || !input.trim()}>
          <Send size={18} />
        </button>
      </form>
    </div>
  );
}
