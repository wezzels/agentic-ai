import React from 'react';
import { FileCheck, CheckCircle, AlertCircle, Clock, FileText } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const auditEngagements = [
  { id: 1, title: 'SOC2 Type II Audit 2026', type: 'IT General', status: 'In Progress', progress: 65, auditor: 'external-auditor@auditfirm.com', startDate: '2026-04-01' },
  { id: 2, title: 'ISO27001 Surveillance', type: 'Compliance', status: 'Scheduled', progress: 0, auditor: 'iso-auditor@certbody.com', startDate: '2026-05-15' },
  { id: 3, title: 'PCI-DSS Annual', type: 'Compliance', status: 'Completed', progress: 100, auditor: 'pci-auditor@qsacompany.com', startDate: '2026-02-01' },
];

const controlEffectiveness = [
  { principle: 'Security', effective: 42, partial: 5, ineffective: 2 },
  { principle: 'Availability', effective: 28, partial: 3, ineffective: 1 },
  { principle: 'Confidentiality', effective: 18, partial: 2, ineffective: 0 },
];

const findingsBySeverity = [
  { severity: 'Critical', count: 0, color: '#ef4444' },
  { severity: 'High', count: 2, color: '#f97316' },
  { severity: 'Medium', count: 8, color: '#f59e0b' },
  { severity: 'Low', count: 12, color: '#3b82f6' },
];

export default function AuditDashboard() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div><h1 className="text-2xl font-bold text-slate-900">Audit Dashboard</h1><p className="text-slate-600 mt-1">Audit engagements, controls, and findings</p></div>
        <button className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"><FileCheck className="w-5 h-5" />New Audit</button>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-6 rounded-xl border border-slate-200"><div className="flex items-center justify-between"><div><p className="text-sm text-slate-600">Active Audits</p><p className="text-2xl font-bold text-slate-900 mt-1">3</p></div><div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center"><FileCheck className="w-6 h-6 text-blue-600" /></div></div><p className="text-sm text-slate-500 mt-2">1 in fieldwork</p></div>
        <div className="bg-white p-6 rounded-xl border border-slate-200"><div className="flex items-center justify-between"><div><p className="text-sm text-slate-600">Controls Tested</p><p className="text-2xl font-bold text-slate-900 mt-1">89</p></div><div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center"><CheckCircle className="w-6 h-6 text-green-600" /></div></div><p className="text-sm text-green-600 mt-2">92% effective</p></div>
        <div className="bg-white p-6 rounded-xl border border-slate-200"><div className="flex items-center justify-between"><div><p className="text-sm text-slate-600">Open Findings</p><p className="text-2xl font-bold text-slate-900 mt-1">22</p></div><div className="w-12 h-12 bg-amber-100 rounded-lg flex items-center justify-center"><AlertCircle className="w-6 h-6 text-amber-600" /></div></div><p className="text-sm text-amber-600 mt-2">0 critical</p></div>
        <div className="bg-white p-6 rounded-xl border border-slate-200"><div className="flex items-center justify-between"><div><p className="text-sm text-slate-600">Evidence Items</p><p className="text-2xl font-bold text-slate-900 mt-1">156</p></div><div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center"><FileText className="w-6 h-6 text-purple-600" /></div></div><p className="text-sm text-slate-500 mt-2">89% reviewed</p></div>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-xl border border-slate-200"><h2 className="text-lg font-semibold text-slate-900 mb-4">Control Effectiveness by Principle</h2><div className="h-64"><ResponsiveContainer width="100%" height="100%"><BarChart data={controlEffectiveness}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="principle" /><YAxis /><Tooltip /><Legend /><Bar dataKey="effective" stackId="a" fill="#22c55e" /><Bar dataKey="partial" stackId="a" fill="#f59e0b" /><Bar dataKey="ineffective" stackId="a" fill="#ef4444" /></BarChart></ResponsiveContainer></div></div>
        <div className="bg-white p-6 rounded-xl border border-slate-200"><h2 className="text-lg font-semibold text-slate-900 mb-4">Findings by Severity</h2><div className="h-64"><ResponsiveContainer width="100%" height="100%"><PieChart><Pie data={findingsBySeverity} cx="50%" cy="50%" labelLine={false} label={({ severity, count }) => `${severity}: ${count}`} outerRadius={80} dataKey="count">{findingsBySeverity.map((entry, index) => (<Cell key={`cell-${index}`} fill={entry.color} />))}</Pie><Tooltip /></PieChart></ResponsiveContainer></div></div>
      </div>
      <div className="bg-white p-6 rounded-xl border border-slate-200"><h2 className="text-lg font-semibold text-slate-900 mb-4">Audit Engagements</h2><div className="space-y-4">{auditEngagements.map((audit) => (<div key={audit.id} className="border border-slate-200 rounded-lg p-4"><div className="flex items-center justify-between mb-2"><h3 className="font-medium text-slate-900">{audit.title}</h3><span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${audit.status === 'Completed' ? 'bg-green-100 text-green-800' : audit.status === 'In Progress' ? 'bg-blue-100 text-blue-800' : 'bg-slate-100 text-slate-800'}`}>{audit.status}</span></div><p className="text-sm text-slate-600">{audit.type} • {audit.auditor}</p><div className="mt-3"><div className="flex items-center justify-between text-sm mb-1"><span className="text-slate-600">Progress</span><span className="font-medium text-slate-900">{audit.progress}%</span></div><div className="w-full bg-slate-200 rounded-full h-2"><div className="bg-blue-600 h-2 rounded-full" style={{ width: `${audit.progress}%` }}></div></div></div></div>))}</div></div>
    </div>
  );
}
