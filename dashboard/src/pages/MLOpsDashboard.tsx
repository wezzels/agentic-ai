import React from 'react';
import { Brain, TrendingUp, AlertTriangle, Server, Database } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, Legend, PieChart, Pie, Cell } from 'recharts';

const models = [
  { id: 1, name: 'Churn Predictor v2.3', framework: 'XGBoost', stage: 'Production', accuracy: 92.0, status: 'healthy' },
  { id: 2, name: 'Fraud Detector v1.8', framework: 'TensorFlow', stage: 'Production', accuracy: 94.5, status: 'warning' },
  { id: 3, name: 'Recommendation Engine v3.1', framework: 'PyTorch', stage: 'Staging', accuracy: 88.2, status: 'healthy' },
  { id: 4, name: 'NLP Classifier v2.0', framework: 'TensorFlow', stage: 'Development', accuracy: 85.7, status: 'healthy' },
];

const driftMetrics = [
  { time: '00:00', accuracy: 92.5, drift: 0.02 },
  { time: '04:00', accuracy: 92.3, drift: 0.03 },
  { time: '08:00', accuracy: 91.8, drift: 0.05 },
  { time: '12:00', accuracy: 91.2, drift: 0.08 },
  { time: '16:00', accuracy: 90.5, drift: 0.12 },
  { time: '20:00', accuracy: 90.1, drift: 0.15 },
];

const experimentStatus = [
  { status: 'Completed', count: 28 },
  { status: 'Running', count: 3 },
  { status: 'Failed', count: 2 },
];

const deployments = [
  { environment: 'Production', count: 8, status: 'healthy' },
  { environment: 'Staging', count: 5, status: 'healthy' },
  { environment: 'Development', count: 12, status: 'healthy' },
];

export default function MLOpsDashboard() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div><h1 className="text-2xl font-bold text-slate-900">ML Ops Dashboard</h1><p className="text-slate-600 mt-1">Model lifecycle, experiments, and monitoring</p></div>
        <button className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"><Brain className="w-5 h-5" />Register Model</button>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-6 rounded-xl border border-slate-200"><div className="flex items-center justify-between"><div><p className="text-sm text-slate-600">Models</p><p className="text-2xl font-bold text-slate-900 mt-1">25</p></div><div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center"><Brain className="w-6 h-6 text-blue-600" /></div></div><p className="text-sm text-slate-500 mt-2">8 in production</p></div>
        <div className="bg-white p-6 rounded-xl border border-slate-200"><div className="flex items-center justify-between"><div><p className="text-sm text-slate-600">Experiments</p><p className="text-2xl font-bold text-slate-900 mt-1">156</p></div><div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center"><TrendingUp className="w-6 h-6 text-green-600" /></div></div><p className="text-sm text-green-600 mt-2">93% success rate</p></div>
        <div className="bg-white p-6 rounded-xl border border-slate-200"><div className="flex items-center justify-between"><div><p className="text-sm text-slate-600">Drift Alerts</p><p className="text-2xl font-bold text-slate-900 mt-1">3</p></div><div className="w-12 h-12 bg-amber-100 rounded-lg flex items-center justify-center"><AlertTriangle className="w-6 h-6 text-amber-600" /></div></div><p className="text-sm text-amber-600 mt-2">Require attention</p></div>
        <div className="bg-white p-6 rounded-xl border border-slate-200"><div className="flex items-center justify-between"><div><p className="text-sm text-slate-600">Deployments</p><p className="text-2xl font-bold text-slate-900 mt-1">25</p></div><div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center"><Server className="w-6 h-6 text-purple-600" /></div></div><p className="text-sm text-slate-500 mt-2">All healthy</p></div>
      </div>
      <div className="bg-white p-6 rounded-xl border border-slate-200"><h2 className="text-lg font-semibold text-slate-900 mb-4">Production Models</h2><table className="w-full"><thead className="bg-slate-50"><tr><th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase">Model</th><th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase">Framework</th><th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase">Stage</th><th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase">Accuracy</th><th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase">Status</th></tr></thead><tbody className="divide-y divide-slate-200">{models.map((model) => (<tr key={model.id} className="hover:bg-slate-50"><td className="px-6 py-4 font-medium text-slate-900">{model.name}</td><td className="px-6 py-4 text-sm text-slate-600">{model.framework}</td><td className="px-6 py-4"><span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${model.stage === 'Production' ? 'bg-green-100 text-green-800' : model.stage === 'Staging' ? 'bg-blue-100 text-blue-800' : 'bg-slate-100 text-slate-800'}`}>{model.stage}</span></td><td className="px-6 py-4"><div className="flex items-center gap-2"><div className="w-24 bg-slate-200 rounded-full h-2"><div className={`h-2 rounded-full ${model.accuracy >= 90 ? 'bg-green-500' : model.accuracy >= 85 ? 'bg-amber-500' : 'bg-red-500'}`} style={{ width: `${model.accuracy}%` }}></div></div><span className="text-sm text-slate-600">{model.accuracy}%</span></div></td><td className="px-6 py-4"><span className={`inline-flex items-center gap-1 text-sm ${model.status === 'healthy' ? 'text-green-600' : 'text-amber-600'}`}>{model.status === 'healthy' ? <TrendingUp className="w-4 h-4" /> : <AlertTriangle className="w-4 h-4" />}{model.status}</span></td></tr>))}</tbody></table></div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-xl border border-slate-200"><h2 className="text-lg font-semibold text-slate-900 mb-4">Model Drift (24h)</h2><div className="h-64"><ResponsiveContainer width="100%" height="100%"><LineChart data={driftMetrics}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="time" /><YAxis yAxisId="left" /><YAxis yAxisId="right" orientation="right" /><Tooltip /><Legend /><Line yAxisId="left" type="monotone" dataKey="accuracy" stroke="#22c55e" name="Accuracy %" /><Line yAxisId="right" type="monotone" dataKey="drift" stroke="#ef4444" name="Drift Score" /></LineChart></ResponsiveContainer></div></div>
        <div className="bg-white p-6 rounded-xl border border-slate-200"><h2 className="text-lg font-semibold text-slate-900 mb-4">Experiments</h2><div className="h-64"><ResponsiveContainer width="100%" height="100%"><PieChart><Pie data={experimentStatus} cx="50%" cy="50%" labelLine={false} label={({ status, count }) => `${status}: ${count}`} outerRadius={80} dataKey="count">{experimentStatus.map((entry, index) => (<Cell key={`cell-${index}`} fill={['#22c55e', '#3b82f6', '#ef4444'][index]} />))}</Pie><Tooltip /></PieChart></ResponsiveContainer></div></div>
      </div>
    </div>
  );
}
