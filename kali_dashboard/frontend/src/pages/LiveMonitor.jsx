import React, { useState, useEffect } from 'react';
import { Activity, Terminal, Clock, CheckCircle, AlertCircle, Play, Pause, Square } from 'lucide-react';

function LiveMonitor() {
  const [isRunning, setIsRunning] = useState(false);
  const [currentTool, setCurrentTool] = useState(null);
  const [executionQueue, setExecutionQueue] = useState([]);
  const [completedTools, setCompletedTools] = useState([]);
  const [liveOutput, setLiveOutput] = useState([]);
  const [metrics, setMetrics] = useState({
    toolsExecuted: 0,
    findingsDiscovered: 0,
    elapsedTime: 0,
    successRate: 100,
  });

  // Simulate live execution
  useEffect(() => {
    if (!isRunning) return;

    const interval = setInterval(() => {
      setMetrics(prev => ({
        ...prev,
        elapsedTime: prev.elapsedTime + 1,
      }));
    }, 1000);

    return () => clearInterval(interval);
  }, [isRunning]);

  const handleStart = () => {
    setIsRunning(true);
    setExecutionQueue([
      { name: 'Nmap', status: 'pending', progress: 0 },
      { name: 'theHarvester', status: 'pending', progress: 0 },
      { name: 'Gobuster', status: 'pending', progress: 0 },
      { name: 'Nikto', status: 'pending', progress: 0 },
      { name: 'SQLMap', status: 'pending', progress: 0 },
    ]);
  };

  const handleStop = () => {
    setIsRunning(false);
  };

  return (
    <div className="live-monitor-page">
      <div className="page-header">
        <h1>Live Execution Monitor</h1>
        <div className="monitor-controls">
          <button 
            className={`btn ${isRunning ? 'danger' : 'primary'}`}
            onClick={isRunning ? handleStop : handleStart}
          >
            {isRunning ? (
              <>
                <Square size={18} fill="white" />
                Stop Execution
              </>
            ) : (
              <>
                <Play size={18} fill="white" />
                Start Monitoring
              </>
            )}
          </button>
        </div>
      </div>

      <div className="metrics-dashboard">
        <MetricCard
          icon={Activity}
          label="Tools Executed"
          value={metrics.toolsExecuted}
          color="#3b82f6"
        />
        <MetricCard
          icon={AlertCircle}
          label="Findings"
          value={metrics.findingsDiscovered}
          color="#f59e0b"
        />
        <MetricCard
          icon={Clock}
          label="Elapsed Time"
          value={formatTime(metrics.elapsedTime)}
          color="#10b981"
        />
        <MetricCard
          icon={CheckCircle}
          label="Success Rate"
          value={`${metrics.successRate}%`}
          color="#8b5cf6"
        />
      </div>

      <div className="monitor-grid">
        <div className="execution-status">
          <h3>Execution Status</h3>
          <div className="status-list">
            {executionQueue.map((tool, idx) => (
              <ExecutionItem key={idx} tool={tool} isRunning={isRunning} />
            ))}
            {completedTools.map((tool, idx) => (
              <ExecutionItem key={`completed-${idx}`} tool={tool} completed />
            ))}
          </div>
        </div>

        <div className="live-output">
          <h3>
            <Terminal size={20} />
            Live Output
          </h3>
          <div className="output-console">
            {liveOutput.map((line, idx) => (
              <div key={idx} className={`console-line ${line.type}`}>
                <span className="timestamp">[{line.time}]</span>
                <span className="message">{line.message}</span>
              </div>
            ))}
            {liveOutput.length === 0 && (
              <div className="console-empty">
                No output yet. Start execution to see live logs.
              </div>
            )}
          </div>
        </div>

        <div className="performance-chart">
          <h3>Tool Performance</h3>
          <PerformanceChart tools={completedTools} />
        </div>

        <div className="findings-feed">
          <h3>Live Findings</h3>
          <FindingsFeed />
        </div>
      </div>
    </div>
  );
}

function MetricCard({ icon: Icon, label, value, color }) {
  return (
    <div className="metric-card" style={{ '--accent': color }}>
      <div className="metric-icon" style={{ background: `${color}20` }}>
        <Icon size={24} style={{ color }} />
      </div>
      <div className="metric-info">
        <h4>{value}</h4>
        <p>{label}</p>
      </div>
    </div>
  );
}

function ExecutionItem({ tool, completed, isRunning }) {
  const statusColors = {
    pending: '#6b7280',
    running: '#3b82f6',
    completed: '#10b981',
    failed: '#ef4444',
  };

  return (
    <div className={`execution-item ${completed ? 'completed' : ''}`}>
      <div className="execution-header">
        <span className="tool-name">{tool.name}</span>
        <span 
          className="status-badge"
          style={{ background: statusColors[tool.status || 'pending'] }}
        >
          {tool.status || 'pending'}
        </span>
      </div>
      <div className="progress-bar-small">
        <div 
          className="progress-fill-small"
          style={{ 
            width: `${tool.progress || 0}%`,
            background: statusColors[tool.status || 'pending']
          }}
        ></div>
      </div>
    </div>
  );
}

function PerformanceChart({ tools }) {
  const maxDuration = Math.max(...tools.map(t => t.duration || 1));

  return (
    <div className="performance-chart-container">
      {tools.map((tool, idx) => (
        <div key={idx} className="chart-bar-row">
          <span className="bar-label">{tool.name}</span>
          <div className="bar-container">
            <div 
              className="bar-fill"
              style={{ 
                width: `${(tool.duration / maxDuration) * 100}%`,
                background: tool.status === 'completed' ? '#10b981' : '#ef4444'
              }}
            ></div>
          </div>
          <span className="bar-value">{tool.duration?.toFixed(1)}s</span>
        </div>
      ))}
      {tools.length === 0 && (
        <div className="chart-empty">
          No performance data yet
        </div>
      )}
    </div>
  );
}

function FindingsFeed() {
  const findings = [
    { severity: 'high', message: 'Open port 22 (SSH) detected', time: '10:23:45' },
    { severity: 'medium', message: 'Directory listing enabled on /admin/', time: '10:24:12' },
    { severity: 'low', message: 'Missing X-Frame-Options header', time: '10:24:38' },
  ];

  const severityColors = {
    critical: '#ef4444',
    high: '#f59e0b',
    medium: '#3b82f6',
    low: '#10b981',
  };

  return (
    <div className="findings-list">
      {findings.map((finding, idx) => (
        <div key={idx} className="finding-item">
          <div 
            className="severity-indicator"
            style={{ background: severityColors[finding.severity] }}
          ></div>
          <div className="finding-info">
            <span className="finding-message">{finding.message}</span>
            <span className="finding-time">{finding.time}</span>
          </div>
        </div>
      ))}
    </div>
  );
}

function formatTime(seconds) {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

export default LiveMonitor;
