import React from 'react';
import { Shield, AlertTriangle, CheckCircle, TrendingUp, Building, FileText } from 'lucide-react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

const vendorData = [
  { name: 'Tier 1', value: 5, color: '#ef4444' },
  { name: 'Tier 2', value: 8, color: '#f59e0b' },
  { name: 'Tier 3', value: 7, color: '#3b82f6' },
  { name: 'Tier 4', value: 3, color: '#22c55e' },
];

const assessmentStatus = [
  { status: 'Completed', count: 15 },
  { status: 'In Progress', count: 5 },
  { status: 'Scheduled', count: 8 },
  { status: 'Overdue', count: 2 },
];

const findingsData = [
  { severity: 'Critical', count: 1 },
  { severity: 'High', count: 4 },
  { severity: 'Medium', count: 12 },
  { severity: 'Low', count: 8 },
];

const recentVendors = [
  { id: 1, name: 'CloudData Analytics', tier: 'Tier 1', status: 'Assessment Due', risk: 72, lastAssessment: '2025-04-15' },
  { id: 2, name: 'API Gateway Inc', tier: 'Tier 1', status: 'Active Monitoring', risk: 45, lastAssessment: '2026-01-20' },
  { id: 3, name: 'SaaS Vendor LLC', tier: 'Tier 2', status: 'Active', risk: 38, lastAssessment: '2026-02-10' },
  { id: 4, name: 'CloudProvider Inc', tier: 'Tier 1', status: 'Active', risk: 52, lastAssessment: '2026-03-05' },
];

export default function VendorRiskDashboard() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Vendor Risk Dashboard</h1>
          <p className="text-slate-600 mt-1">Third-party risk management and assessments</p>
        </div>
        <button className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
          <Building className="w-5 h-5" />
          Add Vendor
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-6 rounded-xl border border-slate-200">
          <div className="flex items-center justify-between">
            <div><p className="text-sm text-slate-600">Total Vendors</p><p className="text-2xl font-bold text-slate-900 mt-1">23</p></div>
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center"><Building className="w-6 h-6 text-blue-600" /></div>
          </div>
          <p className="text-sm text-slate-500 mt-2">Across all tiers</p>
        </div>
        <div className="bg-white p-6 rounded-xl border border-slate-200">
          <div className="flex items-center justify-between">
            <div><p className="text-sm text-slate-600">Assessments Due</p><p className="text-2xl font-bold text-slate-900 mt-1">8</p></div>
            <div className="w-12 h-12 bg-amber-100 rounded-lg flex items-center justify-center"><FileText className="w-6 h-6 text-amber-600" /></div>
          </div>
          <p className="text-sm text-amber-600 mt-2">2 overdue</p>
        </div>
        <div className="bg-white p-6 rounded-xl border border-slate-200">
          <div className="flex items-center justify-between">
            <div><p className="text-sm text-slate-600">Open Findings</p><p className="text-2xl font-bold text-slate-900 mt-1">25</p></div>
            <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center"><AlertTriangle className="w-6 h-6 text-red-600" /></div>
          </div>
          <p className="text-sm text-red-600 mt-2">1 critical</p>
        </div>
        <div className="bg-white p-6 rounded-xl border border-slate-200">
          <div className="flex items-center justify-between">
            <div><p className="text-sm text-slate-600">Avg Risk Score</p><p className="text-2xl font-bold text-slate-900 mt-1">52</p></div>
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center"><Shield className="w-6 h-6 text-green-600" /></div>
          </div>
          <p className="text-sm text-green-600 mt-2 flex items-center gap-1"><TrendingUp className="w-4 h-4" />Improving</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-xl border border-slate-200 lg:col-span-2">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">Vendor Distribution by Tier</h2>
          <div className="h-64"><ResponsiveContainer width="100%" height="100%"><PieChart><Pie data={vendorData} cx="50%" cy="50%" labelLine={false} label={({ name, value }) => `${name}: ${value}`} outerRadius={80} dataKey="value">{vendorData.map((entry, index) => (<Cell key={`cell-${index}`} fill={entry.color} />))}</Pie><Tooltip /></PieChart></ResponsiveContainer></div>
        </div>
        <div className="bg-white p-6 rounded-xl border border-slate-200">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">Assessment Status</h2>
          <div className="h-64"><ResponsiveContainer width="100%" height="100%"><BarChart data={assessmentStatus}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="status" /><YAxis /><Tooltip /><Bar dataKey="count" fill="#3b82f6" /></BarChart></ResponsiveContainer></div>
        </div>
      </div>

      <div className="bg-white p-6 rounded-xl border border-slate-200">
        <h2 className="text-lg font-semibold text-slate-900 mb-4">Critical Vendors</h2>
        <table className="w-full"><thead className="bg-slate-50"><tr><th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase">Vendor</th><th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase">Tier</th><th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase">Status</th><th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase">Risk Score</th><th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase">Last Assessment</th></tr></thead><tbody className="divide-y divide-slate-200">{recentVendors.map((vendor) => (<tr key={vendor.id} className="hover:bg-slate-50"><td className="px-6 py-4 font-medium text-slate-900">{vendor.name}</td><td className="px-6 py-4"><span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${vendor.tier === 'Tier 1' ? 'bg-red-100 text-red-800' : 'bg-amber-100 text-amber-800'}`}>{vendor.tier}</span></td><td className="px-6 py-4"><span className="text-sm text-slate-600">{vendor.status}</span></td><td className="px-6 py-4"><div className="flex items-center gap-2"><div className="w-24 bg-slate-200 rounded-full h-2"><div className={`h-2 rounded-full ${vendor.risk > 70 ? 'bg-red-500' : vendor.risk > 50 ? 'bg-amber-500' : 'bg-green-500'}`} style={{ width: `${vendor.risk}%` }}></div></div><span className="text-sm text-slate-600">{vendor.risk}</span></div></td><td className="px-6 py-4 text-sm text-slate-600">{vendor.lastAssessment}</td></tr>))}</tbody></table>
      </div>
    </div>
  );
}
