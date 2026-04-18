import React, { useState } from 'react';
import { Search, Filter, Terminal, Shield, Bug, Key, WiFi, Database, HardDrive, Eye, Radio, AlertTriangle } from 'lucide-react';

function Tools() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');

  const categories = [
    { id: 'all', label: 'All Tools', icon: Terminal, count: 52 },
    { id: 'reconnaissance', label: 'Reconnaissance', icon: Eye, count: 10 },
    { id: 'web_application', label: 'Web Application', icon: Globe, count: 11 },
    { id: 'password', label: 'Password Attacks', icon: Key, count: 8 },
    { id: 'wireless', label: 'Wireless', icon: WiFi, count: 5 },
    { id: 'post_exploitation', label: 'Post-Exploit', icon: Database, count: 4 },
    { id: 'forensics', label: 'Forensics', icon: HardDrive, count: 4 },
    { id: 'exploitation', label: 'Exploitation', icon: AlertTriangle, count: 3 },
    { id: 'vulnerability_analysis', label: 'Vulnerability', icon: Bug, count: 3 },
    { id: 'sniffing_spoofing', label: 'Sniffing', icon: Radio, count: 2 },
  ];

  const tools = [
    { name: 'Nmap', category: 'reconnaissance', description: 'Network exploration and security auditing', auth: 'BASIC', command: 'nmap' },
    { name: 'Masscan', category: 'reconnaissance', description: 'Fastest port scanner', auth: 'BASIC', command: 'masscan' },
    { name: 'theHarvester', category: 'reconnaissance', description: 'Email and subdomain harvesting', auth: 'BASIC', command: 'theHarvester' },
    { name: 'Amass', category: 'reconnaissance', description: 'Advanced attack surface mapping', auth: 'BASIC', command: 'amass' },
    { name: 'Subfinder', category: 'reconnaissance', description: 'Subdomain discovery tool', auth: 'BASIC', command: 'subfinder' },
    { name: 'DNSrecon', category: 'reconnaissance', description: 'DNS enumeration tool', auth: 'BASIC', command: 'dnsrecon' },
    { name: 'Shodan', category: 'reconnaissance', description: 'IoT search engine CLI', auth: 'BASIC', command: 'shodan' },
    { name: 'SpiderFoot', category: 'reconnaissance', description: 'Automated OSINT collection', auth: 'BASIC', command: 'spiderfoot-cli' },
    { name: 'SQLMap', category: 'web_application', description: 'SQL injection tool', auth: 'ADVANCED', command: 'sqlmap' },
    { name: 'BurpSuite', category: 'web_application', description: 'Web application security testing', auth: 'ADVANCED', command: 'burpsuite' },
    { name: 'Nikto', category: 'web_application', description: 'Web server scanner', auth: 'BASIC', command: 'nikto' },
    { name: 'Gobuster', category: 'web_application', description: 'Directory/DNS brute-forcer', auth: 'BASIC', command: 'gobuster' },
    { name: 'WPScan', category: 'web_application', description: 'WordPress security scanner', auth: 'BASIC', command: 'wpscan' },
    { name: 'FFuf', category: 'web_application', description: 'Fast web fuzzer', auth: 'BASIC', command: 'ffuf' },
    { name: 'John', category: 'password', description: 'John the Ripper password cracker', auth: 'ADVANCED', command: 'john' },
    { name: 'Hashcat', category: 'password', description: 'Advanced password recovery', auth: 'ADVANCED', command: 'hashcat' },
    { name: 'Hydra', category: 'password', description: 'Network login cracker', auth: 'ADVANCED', command: 'hydra' },
    { name: 'Medusa', category: 'password', description: 'Parallel brute forcer', auth: 'ADVANCED', command: 'medusa' },
    { name: 'Aircrack-ng', category: 'wireless', description: 'WiFi security auditing', auth: 'ADVANCED', command: 'aircrack-ng' },
    { name: 'Reaver', category: 'wireless', description: 'WPS brute force attack', auth: 'ADVANCED', command: 'reaver' },
    { name: 'Wifite', category: 'wireless', description: 'Automated wireless auditor', auth: 'ADVANCED', command: 'wifite' },
    { name: 'Metasploit', category: 'exploitation', description: 'Metasploit Framework', auth: 'CRITICAL', command: 'msfconsole' },
    { name: 'BloodHound', category: 'post_exploitation', description: 'Active Directory reconnaissance', auth: 'CRITICAL', command: 'bloodhound-python' },
    { name: 'Volatility', category: 'forensics', description: 'Memory forensics', auth: 'BASIC', command: 'volatility' },
    { name: 'ExifTool', category: 'forensics', description: 'Metadata extraction', auth: 'BASIC', command: 'exiftool' },
  ];

  const filtered = tools.filter(tool => {
    const matchesSearch = tool.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         tool.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || tool.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const getAuthColor = (auth) => {
    switch(auth) {
      case 'BASIC': return '#3b82f6';
      case 'ADVANCED': return '#f59e0b';
      case 'CRITICAL': return '#ef4444';
      default: return '#6b7280';
    }
  };

  return (
    <div className="tools-page">
      <div className="page-header">
        <h1>Tool Arsenal</h1>
        <p className="subtitle">52 Kali Linux tools at your disposal</p>
      </div>

      <div className="tools-layout">
        <aside className="categories-sidebar">
          <h3>Categories</h3>
          <div className="category-list-nav">
            {categories.map(cat => (
              <button
                key={cat.id}
                className={`category-btn ${selectedCategory === cat.id ? 'active' : ''}`}
                onClick={() => setSelectedCategory(cat.id)}
              >
                <cat.icon size={18} />
                <span>{cat.label}</span>
                <span className="count">{cat.count}</span>
              </button>
            ))}
          </div>
        </aside>

        <main className="tools-main">
          <div className="tools-header">
            <div className="search-box-large">
              <Search size={20} />
              <input
                type="text"
                placeholder="Search tools by name or description..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <div className="results-count">
              Showing <strong>{filtered.length}</strong> tools
            </div>
          </div>

          <div className="tools-grid">
            {filtered.map((tool, idx) => (
              <ToolCard key={idx} tool={tool} authColor={getAuthColor(tool.auth)} />
            ))}
          </div>
        </main>
      </div>
    </div>
  );
}

function ToolCard({ tool, authColor }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div 
      className="tool-card"
      onClick={() => setExpanded(!expanded)}
    >
      <div className="tool-header">
        <div className="tool-name-icon">
          <Terminal size={24} style={{ color: authColor }} />
          <h4>{tool.name}</h4>
        </div>
        <span 
          className="auth-badge-small"
          style={{ background: authColor }}
        >
          {tool.auth}
        </span>
      </div>

      <p className="tool-description">{tool.description}</p>

      <div className="tool-command">
        <code>{tool.command}</code>
      </div>

      {expanded && (
        <div className="tool-details">
          <div className="detail-row">
            <span className="label">Category:</span>
            <span className="value">{tool.category.replace('_', ' ')}</span>
          </div>
          <div className="detail-row">
            <span className="label">Authorization:</span>
            <span className="value">{tool.auth}</span>
          </div>
          <div className="detail-row">
            <span className="label">Usage:</span>
            <code className="usage-example">{tool.command} --help</code>
          </div>
          <button className="execute-tool-btn">
            <Play size={16} />
            Execute Tool
          </button>
        </div>
      )}
    </div>
  );
}

export default Tools;
