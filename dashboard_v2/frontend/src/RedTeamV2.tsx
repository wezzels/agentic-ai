import { useState, useEffect } from 'react';
import './index.css';

interface MITRETechnique {
  id: string;
  name: string;
  tactic: string;
  description: string;
  detection: string;
  platforms: string[];
}

interface RiskScore {
  engagement_id: string;
  risk_score: number;
  risk_level: string;
  risk_factors: Record<string, number>;
  findings_by_severity: Record<string, number>;
}

interface AttackPath {
  path_id: string;
  name: string;
  start_point: string;
  end_point: string;
  total_time_minutes: number;
  visualization: {
    nodes: any[];
    edges: any[];
  };
}

export function RedTeamV2() {
  const [activeTab, setActiveTab] = useState<'mitre' | 'risk' | 'attack-paths'>('mitre');
  const [techniques, setTechniques] = useState<MITRETechnique[]>([]);
  const [selectedTactic, setSelectedTactic] = useState('');
  const [engagementId, setEngagementId] = useState('eng_test');
  const [riskScore, setRiskScore] = useState<RiskScore | null>(null);
  const [attackPaths, setAttackPaths] = useState<AttackPath[]>([]);
  const [loading, setLoading] = useState(false);

  const tactics = [
    'initial_access', 'execution', 'persistence', 'privilege_escalation',
    'defense_evasion', 'credential_access', 'discovery', 'lateral_movement',
    'collection', 'command_and_control', 'exfiltration', 'impact'
  ];

  // Load MITRE techniques
  const loadMITRE = async (tactic?: string) => {
    setLoading(true);
    try {
      const url = tactic
        ? `/api/v2/redteam/mitre?tactic=${tactic}`
        : '/api/v2/redteam/mitre';
      
      const res = await fetch(url);
      const data = await res.json();
      setTechniques(data.techniques || []);
      if (tactic) setSelectedTactic(tactic);
    } catch (err) {
      console.error('Failed to load MITRE techniques', err);
    } finally {
      setLoading(false);
    }
  };

  // Calculate risk
  const calculateRisk = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/v2/redteam/risk', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          engagement_id: engagementId,
          findings: [
            { title: 'SQL Injection', severity: 'critical', mitre_attack: ['T1190'] },
            { title: 'Weak Passwords', severity: 'high', mitre_attack: ['T1110'] },
            { title: 'Missing Patches', severity: 'medium', mitre_attack: ['T1068'] },
          ],
        }),
      });
      
      const data = await res.json();
      setRiskScore(data);
    } catch (err) {
      console.error('Failed to calculate risk', err);
    } finally {
      setLoading(false);
    }
  };

  // Generate attack paths
  const generateAttackPaths = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/v2/redteam/attack-paths', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          engagement_id: engagementId,
          findings: [
            { title: 'External Web App Vulnerability', severity: 'critical', mitre_attack: ['T1190'], target_id: 'web01' },
            { title: 'Credential Dumping', severity: 'high', mitre_attack: ['T1003'], target_id: 'web01' },
            { title: 'Lateral Movement via SMB', severity: 'high', mitre_attack: ['T1021'], target_id: 'dc01' },
          ],
        }),
      });
      
      const data = await res.json();
      setAttackPaths(data.attack_paths || []);
    } catch (err) {
      console.error('Failed to generate attack paths', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMITRE();
  }, []);

  return (
    <div className="demos-page">
      <div className="section-header">
        <h1>⚔️ RedTeam Agent v2</h1>
        <p>MITRE ATT&CK mapping, risk scoring, and attack path visualization</p>
      </div>

      {/* Tabs */}
      <div className="category-filter" style={{ marginBottom: '20px' }}>
        <button
          className={`filter-btn ${activeTab === 'mitre' ? 'active' : ''}`}
          onClick={() => setActiveTab('mitre')}
        >
          📚 MITRE ATT&CK
        </button>
        <button
          className={`filter-btn ${activeTab === 'risk' ? 'active' : ''}`}
          onClick={() => setActiveTab('risk')}
        >
          📊 Risk Scoring
        </button>
        <button
          className={`filter-btn ${activeTab === 'attack-paths' ? 'active' : ''}`}
          onClick={() => setActiveTab('attack-paths')}
        >
          🗺️ Attack Paths
        </button>
      </div>

      {/* MITRE ATT&CK Browser */}
      {activeTab === 'mitre' && (
        <div className="section">
          <h2>📚 MITRE ATT&CK v12 Techniques</h2>
          
          <div style={{ marginBottom: '20px' }}>
            <strong>Filter by Tactic:</strong>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginTop: '10px' }}>
              <button
                className={`filter-btn ${selectedTactic === '' ? 'active' : ''}`}
                onClick={() => loadMITRE()}
                style={{ fontSize: '12px', padding: '6px 12px' }}
              >
                All
              </button>
              {tactics.map(tactic => (
                <button
                  key={tactic}
                  className={`filter-btn ${selectedTactic === tactic ? 'active' : ''}`}
                  onClick={() => loadMITRE(tactic)}
                  style={{ fontSize: '12px', padding: '6px 12px' }}
                >
                  {tactic.replace(/_/g, ' ').toUpperCase()}
                </button>
              ))}
            </div>
          </div>

          {loading && <div style={{ padding: '20px', textAlign: 'center' }}>⏳ Loading techniques...</div>}

          <div className="demo-grid">
            {techniques.map((tech) => (
              <div key={tech.id} className="demo-card">
                <h3>{tech.id}: {tech.name}</h3>
                <div className="demo-meta">
                  <span>🎯 {tech.tactic.replace(/_/g, ' ').toUpperCase()}</span>
                </div>
                <p style={{ fontSize: '14px', marginTop: '10px' }}>{tech.description}</p>
                <div style={{ marginTop: '10px', fontSize: '13px', color: '#666' }}>
                  <strong>🔍 Detection:</strong> {tech.detection}
                </div>
                <div style={{ marginTop: '8px', fontSize: '12px', color: '#888' }}>
                  <strong>Platforms:</strong> {tech.platforms.join(', ')}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Risk Scoring */}
      {activeTab === 'risk' && (
        <div className="section">
          <h2>📊 Engagement Risk Scoring</h2>
          
          <div style={{ marginBottom: '20px' }}>
            <label style={{ marginRight: '20px' }}>
              <strong>Engagement ID:</strong>
              <input
                type="text"
                value={engagementId}
                onChange={(e) => setEngagementId(e.target.value)}
                style={{ marginLeft: '10px', padding: '8px', borderRadius: '4px', border: '1px solid #ccc' }}
              />
            </label>
            <button className="btn primary" onClick={calculateRisk} disabled={loading}>
              {loading ? '⏳ Calculating...' : '📊 Calculate Risk'}
            </button>
          </div>

          {riskScore && (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px' }}>
              {/* Overall Risk */}
              <div className="demo-card" style={{ textAlign: 'center' }}>
                <h3>Overall Risk</h3>
                <div style={{ fontSize: '48px', fontWeight: 'bold', color: riskScore.risk_score >= 80 ? '#d32f2f' : riskScore.risk_score >= 60 ? '#f57c00' : '#388e3c' }}>
                  {riskScore.risk_score}/100
                </div>
                <div style={{ fontSize: '24px', marginTop: '10px' }}>
                  {riskScore.risk_level.toUpperCase()}
                </div>
              </div>

              {/* Risk Factors */}
              <div className="demo-card">
                <h3>Risk Factors</h3>
                {Object.entries(riskScore.risk_factors).map(([factor, score]) => (
                  <div key={factor} style={{ marginBottom: '10px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px' }}>
                      <span>{factor.replace(/_/g, ' ').toUpperCase()}</span>
                      <span>{score} pts</span>
                    </div>
                    <div style={{ background: '#eee', height: '8px', borderRadius: '4px', overflow: 'hidden' }}>
                      <div style={{ width: `${(score / 10) * 100}%`, background: '#2196f3', height: '100%' }} />
                    </div>
                  </div>
                ))}
              </div>

              {/* Findings by Severity */}
              <div className="demo-card">
                <h3>Findings by Severity</h3>
                {Object.entries(riskScore.findings_by_severity).map(([severity, count]) => (
                  <div key={severity} style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid #eee' }}>
                    <span style={{ textTransform: 'capitalize' }}>
                      {severity === 'critical' && '🔴'}
                      {severity === 'high' && '🟠'}
                      {severity === 'medium' && '🟡'}
                      {severity === 'low' && '🟢'}
                      {' '}{severity}
                    </span>
                    <strong>{count}</strong>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Attack Paths */}
      {activeTab === 'attack-paths' && (
        <div className="section">
          <h2>🗺️ Attack Path Visualization</h2>
          
          <div style={{ marginBottom: '20px' }}>
            <button className="btn primary" onClick={generateAttackPaths} disabled={loading}>
              {loading ? '⏳ Generating...' : '🗺️ Generate Attack Paths'}
            </button>
          </div>

          {attackPaths.length > 0 && (
            <div>
              {attackPaths.map((path) => (
                <div key={path.path_id} className="demo-card" style={{ marginBottom: '20px' }}>
                  <h3>{path.name}</h3>
                  <div className="demo-meta">
                    <span>⏱️ {path.total_time_minutes} minutes</span>
                    <span>🎯 {path.start_point} → {path.end_point}</span>
                  </div>
                  
                  <div style={{ marginTop: '20px' }}>
                    <h4>Attack Steps:</h4>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginTop: '10px' }}>
                      {path.visualization.nodes.map((node: any) => (
                        <div
                          key={node.id}
                          style={{
                            padding: '10px',
                            background: node.type === 'start' ? '#e3f2fd' : node.type === 'objective' ? '#ffebee' : '#f5f5f5',
                            borderRadius: '4px',
                            border: '1px solid #ddd',
                            position: 'relative',
                          }}
                        >
                          <strong>{node.name}</strong>
                          {node.target && <span style={{ marginLeft: '10px', color: '#666' }}>({node.target})</span>}
                          {node.time_minutes > 0 && (
                            <span style={{ position: 'absolute', right: '10px', fontSize: '12px', color: '#888' }}>
                              ⏱️ {node.time_minutes} min
                            </span>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {attackPaths.length === 0 && !loading && (
            <div style={{ padding: '40px', textAlign: 'center', color: '#666' }}>
              Click "Generate Attack Paths" to visualize attack scenarios
            </div>
          )}
        </div>
      )}
    </div>
  );
}
