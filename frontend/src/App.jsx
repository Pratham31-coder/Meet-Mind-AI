import { useState } from 'react';
import Uploader from './components/Uploader';
import Dashboard from './components/Dashboard';
import { Sparkles } from 'lucide-react';

function App() {
  const [meetingId, setMeetingId] = useState(null);

  return (
    <div className="app-container">
      <header>
        <h1 className="logo">
          <Sparkles className="text-accent" />
          AI Video Assistant
        </h1>
      </header>
      
      <main>
        {!meetingId ? (
          <Uploader onUploadComplete={(id) => setMeetingId(id)} />
        ) : (
          <Dashboard meetingId={meetingId} onReset={() => setMeetingId(null)} />
        )}
      </main>
    </div>
  );
}

export default App;
