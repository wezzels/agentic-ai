import React, { useState } from 'react';
import { Play, Target, Globe, Key, WiFi, Building, Terminal, Clock, AlertTriangle, CheckCircle } from 'lucide-react';

function Playbooks() {
  const [selectedPlaybook, setSelectedPlaybook] = useState(null);
  const [executing, setExecuting] = useState(false);
  const [executionLog, setExecutionLog] = useState([]);

  const playbooks = [
    {
      id: 'recon',
      name: 'Comprehensive Reconnaissance',
      icon: Target,
      color: '#3b82f6',
      description: 'Full external reconnaissance with multiple data sources',
      tools: ['Nmap', 'theHarvester', 'Amass', 'DNSrecon', 'Nikto'],
      duration: '45-90 min',
      authorization: 'BASIC',
      steps: [
        { tool: 'Nmap', action: 'Port scan (1-10000)', icon: '🔍' },
        { tool: 'theHarvester', action: 'Email/subdomain harvest', icon: '📧' },
        { tool: 'Amass', action: 'Subdomain enumeration', icon: '🌐' },
        { tool: 'DNSrecon', action: 'DNS records enumeration', icon: '📝' },
        { tool: 'Nikto', action: 'Web server scan', icon: '🔎' },
      ],
    },
    {
      id: 'web_audit',
      name: 'Web Application Security Audit',
      icon: Globe,
      color: '#10b981',
      description: 'Complete web application vulnerability assessment',
      tools: ['Gobuster', 'Nikto', 'WPScan', 'SQLMap', 'SSLScan'],
      duration: '60-120 min',
      authorization: 'ADVANCED',
      steps: [
        { tool: 'Gobuster', action: 'Directory brute-force', icon: '📁' },
        { tool: 'Nikto', action: 'Web vulnerabilities', icon: '🐛' },
        { tool: 'WPScan', action: 'WordPress audit', icon: '📰' },
        { tool: 'SQLMap', action: 'SQL injection test', icon: '💉' },
        { tool: 'SSLScan', action: 'TLS configuration', icon: '🔒' },
      ],
    },
    {
      id: 'password_audit',
      name: 'Password Cracking Audit',
      icon: Key,
      color: '#f59e0b',
      description: 'Password hash cracking and strength analysis',
      tools: ['John', 'Hashcat', 'Hash-Identifier', 'Crunch'],
      duration: '30 min - 24 hrs',
      authorization: 'ADVANCED',
      steps: [
        { tool: 'Hash-Identifier', action: 'Identify hash types', icon: '🏷️' },
        { tool: 'John', action: 'Dictionary attack', icon: '📖' },
        { tool: 'Hashcat', action: 'GPU brute-force', icon: '🎮' },
        { tool: 'Crunch', action: 'Custom wordlist gen', icon: '⚙️' },
      ],
    },
    {
      id: 'wireless_audit',
      name: 'Wireless Security Audit',
      icon: WiFi,
      color: '#8b5cf6',
      description: 'WiFi network security assessment',
      tools: ['Wifite', 'Aircrack-ng', 'Reaver', 'Kismet'],
      duration: '30-90 min',
      authorization: 'ADVANCED',
      steps: [
        { tool: 'Kismet', action: 'Network detection', icon: '📡' },
        { tool: 'Wifite', action: 'Automated audit', icon: '🤖' },
        { tool: 'Aircrack-ng', action: 'WPA crack', icon: '🔓' },
        { tool: 'Reaver', action: 'WPS attack', icon: '🎯' },
      ],
    },
    {
      id: 'ad_audit',
      name: 'Active Directory Audit',
      icon: Building,
      color: '#ef4444',
      description: 'AD security posture assessment',
      tools: ['BloodHound', 'Impacket', 'LDAPSearch'],
      duration: '30-60 min',
      authorization: 'CRITICAL',
      steps: [
        { tool: 'BloodHound', action: 'AD mapping', icon: '🗺️' },
        { tool: 'Impacket', action: 'Protocol analysis', icon: '🔬' },
        { tool: 'LDAPSearch', action: 'Directory query', icon: '📋' },
      ],
    },
  ];

  const handleExecute = async (playbook) => {
    setExecuting(true);
    setSelectedPlaybook(playbook);
    setExecutionLog([]);

    // Simulate execution log
    for (const step of playbook.steps) {
      setExecutionLog(prev => [...prev, {
        time: new Date().toLocaleTimeString(),
        tool: step.tool,
        action: step.action,
        status: 'running',
      }]);
      
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      setExecutionLog(prev => prev.map(log => 
        log.tool === step.tool ? { ...log, status: 'completed' } : log
      ));
    }

    setExecuting(false);
  };

  return (
    <div className="playbooks-page">
      <div className="page-header">
        <h1>Automated Playbooks</h1>
        <p className="subtitle">Pre-configured multi-tool workflows for security engagements</p>
      </div>

      <div className="playbooks-grid">
        {playbooks.map((playbook) => (
          <PlaybookCard 
            key={playbook.id} 
            playbook={playbook} 
            onExecute={handleExecute}
            executing={executing && selectedPlaybook?.id === playbook.id}
          />
        ))}
      </div>

      {executing && selectedPlaybook && (
        <ExecutionConsole 
          playbook={selectedPlaybook} 
          logs={executionLog}
        />
      )}
    </div>
  );
}

function PlaybookCard({ playbook, onExecute, executing }) {
  const AuthBadge = ({ level }) => {
    const colors = {
      BASIC: '#3b82f6',
      ADVANCED: '#f59e0b',
      CRITICAL: '#ef4444',
    };
    
    return (
      <span 
        className="auth-badge"
        style={{ background: colors[level] }}
      >
        {level}
      </span>
    );
  };

  return (
    <div className="playbook-card" style={{ '--accent-color': playbook.color }}>
      <div className="playbook-header">
        <div className="playbook-icon" style={{ background: `${playbook.color}20` }}>
          <playbook.icon size={32} style={{ color: playbook.color }} />
        </div>
        <AuthBadge level={playbook.authorization} />
      </div>

      <h3>{playbook.name}</h3>
      <p className="playbook-desc">{playbook.description}</p>

      <div className="playbook-meta">
        <div className="meta-item">
          <Clock size={16} />
          <span>{playbook.duration}</span>
        </div>
        <div className="meta-item">
          <Terminal size={16} />
          <span>{playbook.tools.length} tools</span>
        </div>
      </div>

      <div className="tools-list">
        {playbook.tools.map((tool, idx) => (
          <span key={idx} className="tool-tag">{tool}</span>
        ))}
      </div>

      <div className="playbook-steps">
        <h4>Execution Steps</h4>
        {playbook.steps.map((step, idx) => (
          <div key={idx} className="step-item">
            <span className="step-icon">{step.icon}</span>
            <div className="step-info">
              <span className="step-tool">{step.tool}</span>
              <span className="step-action">{step.action}</span>
            </div>
          </div>
        ))}
      </div>

      <button 
        className="execute-btn"
        onClick={() => onExecute(playbook)}
        disabled={executing}
        style={{ 
          background: executing 
            ? 'linear-gradient(135deg, #6b7280 0%, #4b5563 100%)'
            : `linear-gradient(135deg, ${playbook.color} 0%, ${playbook.color}dd 100%)`
        }}
      >
        {executing ? (
          <>
            <div className="spinner"></div>
            Executing...
          </>
        ) : (
          <>
            <Play size={18} fill="white" />
            Execute Playbook
          </>
        )}
      </button>
    </div>
  );
}

function ExecutionConsole({ playbook, logs }) {
  return (
    <div className="execution-console">
      <div className="console-header">
        <Terminal size={20} />
        <h3>Executing: {playbook.name}</h3>
        <div className="console-status">
          <div className="status-indicator running"></div>
          In Progress
        </div>
      </div>

      <div className="console-output">
        {logs.map((log, idx) => (
          <div key={idx} className={`log-entry ${log.status}`}>
            <span className="log-time">[{log.time}]</span>
            <span className="log-tool">{log.tool}</span>
            <span className="log-action">{log.action}</span>
            {log.status === 'completed' && (
              <CheckCircle size={16} className="success-icon" />
            )}
            {log.status === 'running' && (
              <div className="mini-spinner"></div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default Playbooks;
