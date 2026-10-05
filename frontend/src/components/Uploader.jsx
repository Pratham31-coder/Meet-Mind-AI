import { useState, useRef } from 'react';
import { UploadCloud, ArrowRight, Loader2 } from 'lucide-react';

const API_BASE = 'http://localhost:8000/api';

export default function Uploader({ onUploadComplete }) {
  const [url, setUrl] = useState('');
  const [isDragging, setIsDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  const handleUrlSubmit = async (e) => {
    e.preventDefault();
    if (!url) return;
    
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/meetings/youtube`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url, language: 'english' })
      });
      if (!res.ok) throw new Error('Failed to submit URL');
      const data = await res.json();
      onUploadComplete(data.id);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  const handleFileUpload = async (file) => {
    if (!file) return;
    setLoading(true);
    setError(null);
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('language', 'english');

    try {
      const res = await fetch(`${API_BASE}/meetings/upload`, {
        method: 'POST',
        body: formData
      });
      if (!res.ok) throw new Error('Failed to upload file');
      const data = await res.json();
      onUploadComplete(data.id);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  return (
    <div className="glass-card uploader-container">
      <div 
        className={`drop-zone ${isDragging ? 'active' : ''}`}
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setIsDragging(false);
          const file = e.dataTransfer.files[0];
          handleFileUpload(file);
        }}
        onClick={() => fileInputRef.current?.click()}
      >
        <UploadCloud />
        <div>
          <h3 style={{fontSize: '1.2rem'}}>Upload Video/Audio File</h3>
          <p className="text-muted" style={{marginTop: '0.5rem', color: 'var(--text-muted)'}}>Drag and drop your .mp4 or .wav file here, or click to browse</p>
        </div>
        <input 
          type="file" 
          ref={fileInputRef}
          style={{ display: 'none' }} 
          accept="audio/*,video/*"
          onChange={(e) => handleFileUpload(e.target.files[0])}
        />
      </div>

      <div className="divider">OR</div>

      <form onSubmit={handleUrlSubmit} className="input-group">
        <input 
          type="url" 
          placeholder="Paste a YouTube link..." 
          className="youtube-input"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
        />
        <button type="submit" className="primary-btn" disabled={loading || !url}>
          {loading ? <Loader2 style={{animation: 'spin 1s linear infinite'}} /> : <ArrowRight />}
          Process URL
        </button>
      </form>
      
      {error && <p style={{color: 'var(--error)', textAlign: 'center'}}>{error}</p>}
      {loading && <p style={{textAlign: 'center', color: 'var(--accent-primary)'}}>Starting pipeline...</p>}
    </div>
  );
}
