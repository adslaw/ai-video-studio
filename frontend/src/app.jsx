const { useState, useEffect } = React;
const API = window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost'
  ? 'http://127.0.0.1:8000'
  : 'https://ai-video-studio-production-c20a.up.railway.app';

function App() {
  const [view, setView] = useState('dashboard');
  const [projects, setProjects] = useState([]);
  const [current, setCurrent] = useState(null);
  const [status, setStatus] = useState({});

  useEffect(() => { loadProjects(); loadStatus(); }, []);

  async function loadProjects() {
    try {
      const r = await fetch(API + '/projects');
      if (r.ok) setProjects(await r.json());
    } catch (e) { console.error(e); }
  }

  async function loadStatus() {
    try {
      const r = await fetch(API + '/settings/status');
      if (r.ok) setStatus(await r.json());
    } catch (e) { setStatus({ checks: { backend: false, ffmpeg: false } }); }
  }

  async function createProject(e) {
    e.preventDefault();
    const fd = new FormData(e.target);
    const body = Object.fromEntries(fd.entries());
    try {
      const r = await fetch(API + '/projects', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
      if (r.ok) {
        const data = await r.json();
        setCurrent(data);
        setView('project');
        await loadProjects();
      }
    } catch (e) { console.error(e); }
  }

  async function runStep(step) {
    if (!current) return;
    const pid = current.id;
    let r;
    try {
      if (step === 'hooks') r = await fetch(API + '/projects/' + pid + '/generate-hooks', { method: 'POST' });
      else if (step === 'content') r = await fetch(API + '/projects/' + pid + '/generate-content', { method: 'POST' });
      else if (step === 'images') r = await fetch(API + '/projects/' + pid + '/images/generate', { method: 'POST' });
      else if (step === 'tts') r = await fetch(API + '/projects/' + pid + '/tts', { method: 'POST' });
      else if (step === 'timeline') r = await fetch(API + '/projects/' + pid + '/timeline', { method: 'POST' });
      else if (step === 'render') r = await fetch(API + '/projects/' + pid + '/render', { method: 'POST' });
      if (r && r.ok) {
        const updated = await fetch(API + '/projects/' + pid).then(r => r.json());
        setCurrent(updated);
      }
    } catch (e) { console.error(e); }
  }

  function Dashboard() {
    return (
      <div>
        <h1>Dashboard</h1>
        <div className="card">
          <h3>System Status</h3>
          <p>Backend: <span className={status.checks?.backend ? 'status-good' : 'status-bad'}>{status.checks?.backend ? 'Online' : 'Offline'}</span></p>
          <p>FFmpeg: <span className={status.checks?.ffmpeg ? 'status-good' : 'status-bad'}>{status.checks?.ffmpeg ? 'Available' : 'Missing'}</span></p>
        </div>
        <div className="card">
          <h3>Projects</h3>
          {projects.length === 0 && <p>No projects yet.</p>}
          {projects.map(p => (
            <div key={p.id} className="card" style={{cursor: 'pointer'}} onClick={() => { setCurrent(p); setView('project'); }}>
              <strong>{p.name}</strong> <span>({p.status})</span>
              <p>{p.topic}</p>
            </div>
          ))}
        </div>
      </div>
    );
  }

  function Create() {
    return (
      <div className="card">
        <h2>Create New Project</h2>
        <form onSubmit={createProject}>
          <input name="name" placeholder="Project Name" required />
          <input name="topic" placeholder="Topic / Idea" required />
          <select name="language"><option value="en">English</option><option value="id">Indonesian</option></select>
          <select name="platform"><option value="tiktok">TikTok</option><option value="youtube">YouTube</option></select>
          <select name="target_duration"><option value="30-60">30-60sec</option><option value="15-30">15-30sec</option></select>
          <select name="content_type"><option value="facts">Facts</option><option value="educational">Educational</option></select>
          <button type="submit">Create Project</button>
        </form>
      </div>
    );
  }

  function ProjectView() {
    if (!current) return <p>Select a project first.</p>;
    return (
      <div>
        <h2>{current.name}</h2>
        <p>{current.topic} | {current.language} | {current.platform} | Status: {current.status}</p>
        <div className="card">
          <h3>1. Hooks</h3>
          <button onClick={() => runStep('hooks')}>Generate Hooks</button>
          {current.hook_options && current.hook_options.map((h, i) => (<div key={i} className="hook-option">{h}</div>))}
        </div>
        <div className="card">
          <h3>2. Content</h3>
          <button onClick={() => runStep('content')}>Generate Content</button>
          {current.content_json && <pre>{JSON.stringify(current.content_json, null, 2)}</pre>}
        </div>
        <div className="card">
          <h3>3. Assets</h3>
          <button onClick={() => runStep('images')}>Generate Images</button>
          <button onClick={() => runStep('tts')} style={{marginLeft: 8}}>Generate Audio</button>
        </div>
        <div className="card">
          <h3>4. Timeline &amp; Render</h3>
          <button onClick={() => runStep('timeline')}>Build Timeline</button>
          <button onClick={() => runStep('render')} style={{marginLeft: 8}}>Render Video</button>
          {current.video_path && <p>Video: {current.video_path}</p>}
        </div>
      </div>
    );
  }

  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="logo">AI Video Studio</div>
        <nav className="nav">
          <a className={view === 'dashboard' ? 'active' : ''} onClick={() => setView('dashboard')}>Dashboard</a>
          <a className={view === 'create' ? 'active' : ''} onClick={() => setView('create')}>Create Video</a>
          <a className={view === 'project' ? 'active' : ''} onClick={() => setView('project')}>Project</a>
        </nav>
      </aside>
      <main className="main">
        {view === 'dashboard' && <Dashboard />}
        {view === 'create' && <Create />}
        {view === 'project' && <ProjectView />}
      </main>
    </div>
  );
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);

