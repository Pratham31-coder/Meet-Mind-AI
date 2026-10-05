import { useState, useEffect } from 'react';
import Chat from './Chat';
import { RefreshCw, FileText, CheckSquare, Target, HelpCircle, AlertCircle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

const API_BASE = 'http://localhost:8000/api';

export default function Dashboard({ meetingId, onReset }) {
  const [meeting, setMeeting] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let interval;
    
    const fetchStatus = async () => {
      try {
        const res = await fetch(`${API_BASE}/meetings/${meetingId}`);
        if (!res.ok) throw new Error('Failed to fetch status');
        const data = await res.json();
        setMeeting(data);
        
        if (data.status === 'completed' || data.status === 'error') {
          clearInterval(interval);
        }
      } catch (err) {
        setError(err.message);
        clearInterval(interval);
      }
    };

    fetchStatus();
    interval = setInterval(fetchStatus, 3000); // poll every 3s
    
    return () => clearInterval(interval);
  }, [meetingId]);

  if (error) {
    return (
      <div className="glass-card" style={{textAlign: 'center'}}>
        <AlertCircle size={48} color="var(--error)" style={{margin: '0 auto 1rem'}} />
        <h2>Error Loading Meeting</h2>
        <p style={{color: 'var(--error)'}}>{error}</p>
        <button className="primary-btn" onClick={onReset} style={{margin: '1rem auto'}}>Start Over</button>
      </div>
    );
  }

  if (!meeting) return <div className="progress-container"><div className="spinner"></div><p>Loading...</p></div>;

  if (meeting.status === 'error') {
    return (
      <div className="glass-card" style={{textAlign: 'center'}}>
        <AlertCircle size={48} color="var(--error)" style={{margin: '0 auto 1rem'}} />
        <h2>Pipeline Failed</h2>
        <p style={{color: 'var(--error)', marginTop: '1rem'}}>{meeting.errorMessage}</p>
        <button className="primary-btn" onClick={onReset} style={{margin: '1rem auto'}}>Start Over</button>
      </div>
    );
  }

  if (meeting.status !== 'completed') {
    return (
      <div className="glass-card progress-container">
        <div className="spinner"></div>
        <h2>Processing Video...</h2>
        <div className="stage-badge">{meeting.stage.replace(/_/g, ' ')}</div>
        <p className="text-muted">This may take a few minutes depending on the video length.</p>
      </div>
    );
  }

  const renderList = (items) => {
    if (!items) return <p className="text-muted">None found.</p>;
    if (Array.isArray(items) && items.length > 0) {
      return items.map((item, idx) => {
        // If it's an action item object, format it as a markdown string
        let content = item;
        if (typeof item === 'object' && item !== null) {
          content = `**${item.task}**\n\n*Owner:* ${item.owner || 'Unassigned'} | *Deadline:* ${item.deadline || 'None'}`;
        }
        return (
          <div key={idx} className="list-item">
            <ReactMarkdown>{content}</ReactMarkdown>
          </div>
        );
      });
    } else if (typeof items === 'string') {
        return (
            <div className="list-item">
              <ReactMarkdown>{items}</ReactMarkdown>
            </div>
        );
    }
    return <p className="text-muted">None found.</p>;
  }

  return (
    <div className="dashboard-grid">
      <div className="glass-card">
        <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start'}}>
          <h2 className="dashboard-title">{meeting.title || 'Untitled Meeting'}</h2>
          <button onClick={onReset} className="primary-btn" style={{padding: '0.5rem 1rem'}}>
            <RefreshCw size={16} /> New
          </button>
        </div>
        
        <div className="list-section">
          <h3><FileText size={20} /> Executive Summary</h3>
          <div className="summary-text">
            <ReactMarkdown>{meeting.summary || ''}</ReactMarkdown>
          </div>
        </div>

        <div className="list-section">
          <h3><CheckSquare size={20} /> Action Items</h3>
          {renderList(meeting.actionItems)}
        </div>

        <div className="list-section">
          <h3><Target size={20} /> Key Decisions</h3>
          {renderList(meeting.keyDecisions)}
        </div>

        <div className="list-section">
          <h3><HelpCircle size={20} /> Open Questions</h3>
          {renderList(meeting.openQuestions)}
        </div>
      </div>
      
      <div className="glass-card chat-container" style={{padding: '1.5rem', display: 'flex'}}>
        <h2 className="dashboard-title" style={{marginBottom: '0'}}>Ask AI</h2>
        <Chat meetingId={meetingId} />
      </div>
    </div>
  );
}
