import React from 'react';
import { Cloud, Shield, AlertTriangle, CheckCircle, Server } from 'lucide-react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

const cloudAccounts = [
  { provider: 'AWS', accounts: 3, resources: 245, findings: 8 },
  { provider: 'GCP', accounts: 1, resources: 89, findings: 2 },
  { provider: 'Azure', accounts: 2, resources: 156, findings: 4 },
];

const findingsByService = [
  { service: 'EC2', count: 5 },
  { service: 'S3', count: 3 },
  { service: 'RDS', count: 2 },
  { service: 'IAM', count: 4 },
  { service: 'VPC', count: 1 },
];

const complianceScores = [
  { framework: 'CIS AWS', score: 87 },
  { framework: 'CIS Azure', score: 92 },
  { framework: 'PCI-DSS', score: 94 },
  { framework: 'HIPAA', score: 89 },
  { framework: 'SOC2', score: 91 },
];

const recentFindings = [
  { id: 1, title: 'S3 Bucket Public Access', severity: 'Critical', resource: 's3-customer-data', status: 'Open' },
  { id: 2, title: 'Security Group Open SSH', severity: 'High', resource: 'ec2-web-prod', status: 'Open' },
  { id: 3, title: 'RDS Public Accessible', severity: 'High', resource: 'rds-primary', status: 'In Progress' },
  { id: 4, title: 'IAM User Without MFA', severity: 'Medium', resource: 'iam-dev-user', status: 'Open' },
];

export default function CloudSecurityDashboard() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div><h1 className="text-2xl font-bold text-slate-900">Cloud Security Dashboard</h1><p className="text-slate-600 mt-1">Multi-cloud security posture management</p></div>
        <button className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"><Cloud className="w-5 h-5" />Add Account</button>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-6 rounded-xl border border-slate-200"><div className="flex items-center justify-between"><div><p className="text-sm text-slate-600">Cloud Accounts</p><p className="text-2xl font-bold text-slate-900 mt-1">6</p></div><div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center"><Cloud className="w-6 h-6 text-blue-600" /></div></div><p className="text-sm text-slate-500 mt-2">AWS: 3, GCP: 1, Azure: 2</p></div>
        <div className="bg-white p-6 rounded-xl border border-slate-200"><div className="flex items-center justify-between"><div><p className="text-sm text-slate-600">Total Resources</p><p className="text-2xl font-bold text-slate-900 mt-1">490</p></div><div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center"><Server className="w-6 h-6 text-green-600" /></div></div><p className="text-sm text-slate-500 mt-2">Across all clouds</p></div>
        <div className="bg-white p-6 rounded-xl border border-slate-200"><div className="flex items-center justify-between"><div><p className="text-sm text-slate-600">Open Findings</p><p className="text-2xl font-bold text-slate-900 mt-1">14</p></div><div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center"><AlertTriangle className="w-6 h-6 text-red-600" /></div></div><p className="text-sm text-red-600 mt-2">1 critical</p></div>
        <div className="bg-white p-6 rounded-xl border border-slate-200"><div className="flex items-center justify-between"><div><p className="text-sm text-slate-600">Avg Compliance</p><p className="text-2xl font-bold text-slate-900 mt-1">90.6%</p></div><div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center"><Shield className="w-6 h-6 text-purple-600" /></div></div><p className="text-sm text-green-600 mt-2 flex items-center gap-1"><CheckCircle className="w-4 h-4" />Above target</p></div>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-xl border border-slate-200"><h2 className="text-lg font-semibold text-slate-900 mb-4">Compliance Scores</h2><div className="h-64"><ResponsiveContainer width="100%" height="100%"><BarChart data={complianceScores} layout="horizontal"><CartesianGrid strokeDasharray="3 3" /><XAxis type="number" domain={[0, 100]} /><YAxis dataKey="framework" type="category" width={80} /><Tooltip /><Bar dataKey="score" fill="#3b82f6" /></BarChart></ResponsiveContainer></div></div>
        <div className="bg-white p-6 rounded-xl border border-slate-200"><h2 className="text-lg font-semibold text-slate-900 mb-4">Findings by Service</h2><div className="h-64"><ResponsiveContainer width="100%" height="100%"><PieChart><Pie data={findingsByService} cx="50%" cy="50%" labelLine={false} label={({ service, count }) => `${service}: ${count}`} outerRadius={80} dataKey="count">{findingsByService.map((entry, index) => (<Cell key={`cell-${index}`} fill={['#ef4444', '#f97316', '#f59e0b', '#3b82f6', '#22c55e'][index]} />))}</Pie><Tooltip /></PieChart></ResponsiveContainer></div></div>
        <div className="bg-white p-6 rounded-xl border border-slate-200"><h2 className="text-lg font-semibold text-slate-900 mb-4">Cloud Distribution</h2><div className="space-y-4">{cloudAccounts.map((cloud) => (<div key={cloud.provider} className="border border-slate-200 rounded-lg p-4"><div className="flex items-center justify-between mb-2"><div className="flex items-center gap-2"><Cloud className="w-5 h-5 text-slate-600" /><span className="font-medium text-slate-900">{cloud.provider}</span></div><span className="text-sm text-slate-600">{cloud.accounts} accounts</span></div><div className="flex items-center gap-4 text-sm"><span className="text-slate-600">{cloud.resources} resources</span><span className="text-red-600">{cloud.findings} findings</span></div></div>))}</div></div>
      </div>
      <div className="bg-white p-6 rounded-xl border border-slate-200"><h2 className="text-lg font-semibold text-slate-900 mb-4">Recent Findings</h2><div className="space-y-3">{recentFindings.map((finding) => (<div key={finding.id} className="flex items-center gap-4 p-3 bg-slate-50 rounded-lg"><div className={`w-2 h-2 rounded-full ${finding.severity === 'Critical' ? 'bg-red-500' : finding.severity === 'High' ? 'bg-orange-500' : 'bg-amber-500'}`}></div><div className="flex-1"><p className="text-sm font-medium text-slate-900">{finding.title}</p><p className="text-xs text-slate-500">{finding.resource}</p></div><span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${finding.severity === 'Critical' ? 'bg-red-100 text-red-800' : finding.severity === 'High' ? 'bg-orange-100 text-orange-800' : 'bg-amber-100 text-amber-800'}`}>{finding.severity}</span><span className="text-sm text-slate-600">{finding.status}</span></div>))}</div></div>
    </div>
  );
}
