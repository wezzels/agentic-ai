import React from 'react';
import { Activity, Target, AlertTriangle, CheckCircle } from 'lucide-react';

function Dashboard() {
  const stats = [
    { label: 'Total Tools', value: '52', icon: Activity, color: 'blue' },
    { label: 'Active Engagements', value: '3', icon: Target, color: 'green' },
    { label: 'Findings', value: '127', icon: AlertTriangle, color: 'orange' },
    { label: 'Reports Generated', value: '45', icon: CheckCircle, color: 'purple' },
  ];

  const recentEngagements = [
    { id: 'eng-001', name: 'Q2 Pentest', status: 'In Progress', progress: 65 },
    { id: 'eng-002', name: 'Web App Audit', status: 'Completed', progress: 100 },
    { id: 'eng-003', name: 'Network Recon', status: 'Planning', progress: 15 },
  ];

  return (
    <div className="dashboard">
      <div className="stats-grid">
        {stats.map((stat) => (
          <div key={stat.label} className={`stat-card ${stat.color}`}>
            <stat.icon size={24} />
            <div className="stat-info">
              <h3>{stat.value}</h3>
              <p>{stat.label}</p>
            </div>
          </div>
        ))}
      </div>

      <div className="dashboard-grid">
        <div className="card">
          <h3>Recent Engagements</h3>
          <div className="engagement-list">
            {recentEngagements.map((eng) => (
              <div key={eng.id} className="engagement-item">
                <div className="engagement-header">
                  <span className="engagement-name">{eng.name}</span>
                  <span className={`status ${eng.status.toLowerCase().replace(' ', '-')}`}>
                    {eng.status}
                  </span>
                </div>
                <div className="progress-bar">
                  <div 
                    className="progress-fill" 
                    style={{ width: `${eng.progress}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <h3>Tool Categories</h3>
          <div className="category-list">
            <div className="category-item">
              <span>Web Application</span>
              <span className="count">11</span>
            </div>
            <div className="category-item">
              <span>Reconnaissance</span>
              <span className="count">10</span>
            </div>
            <div className="category-item">
              <span>Password Attacks</span>
              <span className="count">8</span>
            </div>
            <div className="category-item">
              <span>Wireless</span>
              <span className="count">5</span>
            </div>
            <div className="category-item">
              <span>Post-Exploitation</span>
              <span className="count">4</span>
            </div>
          </div>
        </div>

        <div className="card full-width">
          <h3>Quick Actions</h3>
          <div className="quick-actions">
            <button className="action-btn primary">
              <Play size={18} />
              New Recon Engagement
            </button>
            <button className="action-btn">
              <Play size={18} />
              Web Audit
            </button>
            <button className="action-btn">
              <Play size={18} />
              Password Crack
            </button>
            <button className="action-btn">
              <FileText size={18} />
              Generate Report
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
