import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { Activity, Shield, FileText, Settings, Play, Database, Terminal } from 'lucide-react';
import Dashboard from './pages/Dashboard';
import Engagements from './pages/Engagements';
import Playbooks from './pages/Playbooks';
import Tools from './pages/Tools';
import Settings from './pages/Settings';
import './App.css';

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const menuItems = [
    { path: '/', icon: Activity, label: 'Dashboard' },
    { path: '/engagements', icon: Database, label: 'Engagements' },
    { path: '/playbooks', icon: Play, label: 'Playbooks' },
    { path: '/tools', icon: Terminal, label: 'Tools' },
    { path: '/settings', icon: Settings, label: 'Settings' },
  ];

  return (
    <Router>
      <div className="app">
        <aside className={`sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
          <div className="sidebar-header">
            <Shield className="logo" size={32} />
            {sidebarOpen && <h1>KaliAgent</h1>}
          </div>
          
          <nav className="menu">
            {menuItems.map((item) => (
              <Link key={item.path} to={item.path} className="menu-item">
                <item.icon size={20} />
                {sidebarOpen && <span>{item.label}</span>}
              </Link>
            ))}
          </nav>
          
          <button 
            className="toggle-sidebar"
            onClick={() => setSidebarOpen(!sidebarOpen)}
          >
            {sidebarOpen ? '◀' : '▶'}
          </button>
        </aside>

        <main className="main-content">
          <header className="top-bar">
            <h2>Kali Linux Tool Orchestration</h2>
            <div className="status-indicator">
              <span className="status-dot healthy"></span>
              <span>API Connected</span>
            </div>
          </header>

          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/engagements" element={<Engagements />} />
            <Route path="/playbooks" element={<Playbooks />} />
            <Route path="/tools" element={<Tools />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
