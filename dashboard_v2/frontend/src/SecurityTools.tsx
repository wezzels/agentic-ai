import { useState } from 'react';
import './index.css';

interface ToolRecommendation {
  name: string;
  category: string;
  description: string;
  authorization: number;
  tags: string[];
  reason: string;
}

interface CVEMatch {
  cve: string;
  found: boolean;
  exploit: {
    exploit_name: string;
    metasploit_module: string;
    reliability: string;
    rank: number;
    description: string;
  } | null;
}

interface RemediationPlan {
  critical: any[];
  high: any[];
  medium: any[];
  low: any[];
  estimated_effort: string;
  total_findings: number;
}

export function SecurityTools() {
  const [activeTab, setActiveTab] = useState<'cve' | 'recommend' | 'remediation'>('recommend');
  const [cveInput, setCveInput] = useState('');
  const [cveResult, setCveResult] = useState<CVEMatch | null>(null);
  const [targetType, setTargetType] = useState('web_server');
  const [recommendations, setRecommendations] = useState<ToolRecommendation[]>([]);
  const [findingsInput, setFindingsInput] = useState('[{"title": "SQL Injection", "severity": "critical"}]');
  const [remediationPlan, setRemediationPlan] = useState<RemediationPlan | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // CVE Matching
  const handleCVEMatch = async () => {
    if (!cveInput) return;
    
    setLoading(true);
    setError('');
    
    try {
      const res = await fetch('/api/v2/kali/cve/match', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cve_id: cveInput }),
      });
      
      const data = await res.json();
      setCveResult(data);
    } catch (err) {
      setError('Failed to match CVE');
    } finally {
      setLoading(false);
    }
  };

  // Tool Recommendations
  const handleRecommend = async () => {
    setLoading(true);
    setError('');
    
    try {
      const res = await fetch('/api/v2/kali/tools/recommend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          target_type: targetType,
          os: 'linux',
          services: targetType === 'web_server' ? [{ name: 'http', port: 80 }] : [],
        }),
      });
      
      const data = await res.json();
      setRecommendations(data.recommendations || []);
    } catch (err) {
      setError('Failed to get recommendations');
    } finally {
      setLoading(false);
    }
  };

  // Remediation Plan
  const handleRemediation = async () => {
    setLoading(true);
    setError('');
    
    try {
      const findings = JSON.parse(findingsInput);
      const res = await fetch('/api/v2/kali/remediation/plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ findings }),
      });
      
      const data = await res.json();
      setRemediationPlan(data);
    } catch (err) {
      setError('Invalid JSON or failed to generate plan');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="demos-page">
      <div className="section-header">
        <h1>🛡️ Security Tools v2</h1>
        <p>AI-powered security automation with KaliAgent v2</p>
      </div>

      {/* Tabs */}
      <div className="category-filter" style={{ marginBottom: '20px' }}>
        <button
          className={`filter-btn ${activeTab === 'recommend' ? 'active' : ''}`}
          onClick={() => setActiveTab('recommend')}
        >
          🤖 Tool Recommendations
        </button>
        <button
          className={`filter-btn ${activeTab === 'cve' ? 'active' : ''}`}
          onClick={() => setActiveTab('cve')}
        >
          🎯 CVE → Exploit Matcher
        </button>
        <button
          className={`filter-btn ${activeTab === 'remediation' ? 'active' : ''}`}
          onClick={() => setActiveTab('remediation')}
        >
          🔧 Remediation Planner
        </button>
      </div>

      {error && (
        <div className="alert" style={{ background: '#fee', border: '1px solid #f99', padding: '10px', borderRadius: '4px', marginBottom: '20px' }}>
          ❌ {error}
        </div>
      )}

      {/* Tool Recommendations */}
      {activeTab === 'recommend' && (
        <div className="section">
          <h2>🤖 AI-Powered Tool Recommendations</h2>
          
          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', marginBottom: '10px' }}>
              <strong>Target Type:</strong>
              <select
                value={targetType}
                onChange={(e) => setTargetType(e.target.value)}
                style={{ marginLeft: '10px', padding: '8px', borderRadius: '4px', border: '1px solid #ccc' }}
              >
                <option value="web_server">Web Server</option>
                <option value="active_directory">Active Directory</option>
                <option value="cloud_aws">AWS Cloud</option>
                <option value="cloud_azure">Azure Cloud</option>
                <option value="container">Containers/Kubernetes</option>
                <option value="network">Network Infrastructure</option>
              </select>
            </label>
            
            <button className="btn primary" onClick={handleRecommend} disabled={loading}>
              {loading ? '⏳ Analyzing...' : '🚀 Get Recommendations'}
            </button>
          </div>

          {recommendations.length > 0 && (
            <div className="demo-grid">
              {recommendations.map((rec, i) => (
                <div key={i} className="demo-card">
                  <h3>{rec.name}</h3>
                  <p>{rec.description}</p>
                  <div className="demo-meta">
                    <span>📂 {rec.category}</span>
                    <span>🏷️ {rec.tags.slice(0, 3).join(', ')}</span>
                  </div>
                  <div style={{ marginTop: '10px', fontSize: '14px', color: '#888' }}>
                    <strong>Why:</strong> {rec.reason}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* CVE Matcher */}
      {activeTab === 'cve' && (
        <div className="section">
          <h2>🎯 CVE → Exploit Matcher</h2>
          
          <div style={{ marginBottom: '20px' }}>
            <input
              type="text"
              placeholder="CVE-2021-44228"
              value={cveInput}
              onChange={(e) => setCveInput(e.target.value)}
              style={{ padding: '10px', width: '300px', borderRadius: '4px', border: '1px solid #ccc', marginRight: '10px' }}
            />
            <button className="btn primary" onClick={handleCVEMatch} disabled={loading}>
              {loading ? '🔍 Matching...' : '🎯 Match Exploit'}
            </button>
          </div>

          {cveResult && (
            <div className="terminal-output" style={{ padding: '20px', borderRadius: '4px' }}>
              {cveResult.found ? (
                <>
                  <div style={{ fontSize: '18px', marginBottom: '10px' }}>
                    ✅ <strong>{cveResult.cve}</strong> - Exploit Found!
                  </div>
                  <div style={{ marginLeft: '20px' }}>
                    <p><strong>Exploit:</strong> {cveResult.exploit?.exploit_name}</p>
                    <p><strong>Metasploit Module:</strong> {cveResult.exploit?.metasploit_module}</p>
                    <p><strong>Reliability:</strong> {cveResult.exploit?.reliability} (Rank: {cveResult.exploit?.rank}/5)</p>
                    <p><strong>Description:</strong> {cveResult.exploit?.description}</p>
                  </div>
                </>
              ) : (
                <div style={{ fontSize: '18px' }}>
                  ❌ <strong>{cveResult.cve}</strong> - No exploit found in database
                </div>
              )}
            </div>
          )}

          <div style={{ marginTop: '20px', padding: '15px', background: '#f9f9f9', borderRadius: '4px' }}>
            <h3>📚 Supported CVEs:</h3>
            <ul style={{ marginLeft: '20px', fontSize: '14px' }}>
              <li>CVE-2017-0144 (EternalBlue)</li>
              <li>CVE-2021-44228 (Log4Shell)</li>
              <li>CVE-2019-0708 (BlueKeep)</li>
              <li>CVE-2021-34473 (ProxyShell)</li>
              <li>CVE-2024-1709 (ScreenConnect Auth Bypass)</li>
            </ul>
          </div>
        </div>
      )}

      {/* Remediation Planner */}
      {activeTab === 'remediation' && (
        <div className="section">
          <h2>🔧 Automatic Remediation Planning</h2>
          
          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', marginBottom: '10px' }}>
              <strong>Findings (JSON):</strong>
            </label>
            <textarea
              value={findingsInput}
              onChange={(e) => setFindingsInput(e.target.value)}
              rows={8}
              style={{ width: '100%', padding: '10px', borderRadius: '4px', border: '1px solid #ccc', fontFamily: 'monospace' }}
              placeholder='[{"title": "SQL Injection", "severity": "critical"}]'
            />
            <button className="btn primary" onClick={handleRemediation} disabled={loading} style={{ marginTop: '10px' }}>
              {loading ? '⏳ Generating...' : '📋 Generate Plan'}
            </button>
          </div>

          {remediationPlan && (
            <div className="terminal-output" style={{ padding: '20px', borderRadius: '4px' }}>
              <div style={{ fontSize: '18px', marginBottom: '10px' }}>
                📊 Remediation Plan
              </div>
              <div style={{ marginLeft: '20px' }}>
                <p><strong>Total Findings:</strong> {remediationPlan.total_findings}</p>
                <p><strong>Estimated Effort:</strong> {remediationPlan.estimated_effort}</p>
                
                {remediationPlan.critical.length > 0 && (
                  <>
                    <h4 style={{ color: '#d32f2f', marginTop: '20px' }}>🔴 Critical ({remediationPlan.critical.length})</h4>
                    <ul>
                      {remediationPlan.critical.map((item, i) => (
                        <li key={i}>
                          <strong>{item.finding}</strong>: {item.remediation}
                        </li>
                      ))}
                    </ul>
                  </>
                )}
                
                {remediationPlan.high.length > 0 && (
                  <>
                    <h4 style={{ color: '#f57c00', marginTop: '20px' }}>🟠 High ({remediationPlan.high.length})</h4>
                    <ul>
                      {remediationPlan.high.map((item, i) => (
                        <li key={i}>
                          <strong>{item.finding}</strong>: {item.remediation}
                        </li>
                      ))}
                    </ul>
                  </>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
