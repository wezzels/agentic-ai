import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Activity, 
  Shield, 
  FileCheck, 
  Cloud, 
  Brain, 
  AlertTriangle,
  Server
} from 'lucide-react';

// Import dashboard pages
import OverviewDashboard from './pages/OverviewDashboard';
import ChaosDashboard from './pages/ChaosDashboard';
import VendorRiskDashboard from './pages/VendorRiskDashboard';
import AuditDashboard from './pages/AuditDashboard';
import CloudSecurityDashboard from './pages/CloudSecurityDashboard';
import MLOpsDashboard from './pages/MLOpsDashboard';

// Navigation component
function Navigation() {
  const location = useLocation();
  
  const navItems = [
    { path: '/', label: 'Overview', icon: LayoutDashboard },
    { path: '/chaos', label: 'Chaos Monkey', icon: Activity },
    { path: '/vendor-risk', label: 'Vendor Risk', icon: Shield },
    { path: '/audit', label: 'Audit', icon: FileCheck },
    { path: '/cloud-security', label: 'Cloud Security', icon: Cloud },
    { path: '/mlops', label: 'ML Ops', icon: Brain },
  ];
  
  return (
    <nav className="bg-slate-900 text-white w-64 min-h-screen p-4">
      <div className="mb-8">
        <h1 className="text-xl font-bold flex items-center gap-2">
          <Server className="w-6 h-6" />
          Agentic AI
        </h1>
        <p className="text-slate-400 text-sm mt-1">Dashboard</p>
      </div>
      
      <ul className="space-y-2">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;
          
          return (
            <li key={item.path}>
              <Link
                to={item.path}
                className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
                  isActive
                    ? 'bg-blue-600 text-white'
                    : 'text-slate-300 hover:bg-slate-800'
                }`}
              >
                <Icon className="w-5 h-5" />
                <span>{item.label}</span>
              </Link>
            </li>
          );
        })}
      </ul>
      
      <div className="mt-8 pt-8 border-t border-slate-700">
        <div className="flex items-center gap-2 text-slate-400 text-sm">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          <span>System Online</span>
        </div>
        <p className="text-slate-500 text-xs mt-2">v1.0.0</p>
      </div>
    </nav>
  );
}

// Alert notification component
function AlertBanner() {
  // Mock alerts - would come from API
  const alerts = [
    { id: 1, type: 'critical', message: 'Chaos experiment aborted: Error rate threshold breached' },
    { id: 2, type: 'warning', message: 'Vendor assessment overdue: CloudData Analytics' },
  ];
  
  if (alerts.length === 0) return null;
  
  return (
    <div className="bg-white border-b border-slate-200 p-4">
      <div className="flex items-start gap-3">
        <AlertTriangle className="w-5 h-5 text-amber-500 flex-shrink-0 mt-0.5" />
        <div className="flex-1">
          <h3 className="font-semibold text-slate-900">Active Alerts</h3>
          <ul className="mt-1 space-y-1">
            {alerts.map(alert => (
              <li key={alert.id} className="text-sm text-slate-600">
                <span className={`inline-block w-2 h-2 rounded-full mr-2 ${
                  alert.type === 'critical' ? 'bg-red-500' : 'bg-amber-500'
                }`}></span>
                {alert.message}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}

// Main app component
function App() {
  return (
    <Router>
      <div className="flex min-h-screen bg-slate-50">
        <Navigation />
        
        <main className="flex-1">
          <AlertBanner />
          
          <div className="p-8">
            <Routes>
              <Route path="/" element={<OverviewDashboard />} />
              <Route path="/chaos" element={<ChaosDashboard />} />
              <Route path="/vendor-risk" element={<VendorRiskDashboard />} />
              <Route path="/audit" element={<AuditDashboard />} />
              <Route path="/cloud-security" element={<CloudSecurityDashboard />} />
              <Route path="/mlops" element={<MLOpsDashboard />} />
            </Routes>
          </div>
        </main>
      </div>
    </Router>
  );
}

export default App;
