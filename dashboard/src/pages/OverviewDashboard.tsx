import React from 'react';
import { 
  Activity, 
  Shield, 
  FileCheck, 
  Cloud, 
  Brain, 
  Server,
  AlertTriangle,
  CheckCircle,
  TrendingUp,
  Users,
  Target
} from 'lucide-react';
import { 
  PieChart, Pie, Cell, 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line, Legend
} from 'recharts';

const agentStats = [
  { name: 'Chaos Monkey', experiments: 47, status: 'healthy', icon: Activity },
  { name: 'Vendor Risk', vendors: 23, status: 'healthy', icon: Shield },
  { name: 'Audit', audits: 5, status: 'in_progress', icon: FileCheck },
  { name: 'Cloud Security', findings: 12, status: 'warning', icon: Cloud },
  { name: 'ML Ops', models: 8, status: 'healthy', icon: Brain },
  { name: 'SOC', incidents: 3, status: 'healthy', icon: Server },
];

const experimentData = [
  { name: 'Mon', experiments: 4, successful: 3 },
  { name: 'Tue', experiments: 6, successful: 5 },
  { name: 'Wed', experiments: 8, successful: 7 },
  { name: 'Thu', experiments: 5, successful: 5 },
  { name: 'Fri', experiments: 7, successful: 6 },
  { name: 'Sat', experiments: 3, successful: 3 },
  { name: 'Sun', experiments: 2, successful: 2 },
];

const vendorTierData = [
  { name: 'Tier 1', value: 5, color: '#ef4444' },
  { name: 'Tier 2', value: 8, color: '#f59e0b' },
  { name: 'Tier 3', value: 7, color: '#3b82f6' },
  { name: 'Tier 4', value: 3, color: '#22c55e' },
];

const recentActivity = [
  { id: 1, agent: 'Chaos Monkey', action: 'Experiment completed', time: '2 min ago', type: 'success' },
  { id: 2, agent: 'Vendor Risk', action: 'Assessment overdue alert', time: '15 min ago', type: 'warning' },
  { id: 3, agent: 'Cloud Security', action: 'New finding detected', time: '1 hour ago', type: 'error' },
  { id: 4, agent: 'Audit', action: 'Evidence collected', time: '2 hours ago', type: 'success' },
  { id: 5, agent: 'ML Ops', action: 'Model drift detected', time: '3 hours ago', type: 'warning' },
];

export default function OverviewDashboard() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Overview Dashboard</h1>
        <p className="text-slate-600 mt-1">System-wide status across all Agentic AI agents</p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-6 rounded-xl border border-slate-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-slate-600">Active Agents</p>
              <p className="text-2xl font-bold text-slate-900 mt-1">33</p>
            </div>
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <Server className="w-6 h-6 text-blue-600" />
            </div>
          </div>
          <p className="text-sm text-green-600 mt-2 flex items-center gap-1">
            <CheckCircle className="w-4 h-4" />
            All systems operational
          </p>
        </div>

        <div className="bg-white p-6 rounded-xl border border-slate-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-slate-600">Active Experiments</p>
              <p className="text-2xl font-bold text-slate-900 mt-1">3</p>
            </div>
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <Activity className="w-6 h-6 text-green-600" />
            </div>
          </div>
          <p className="text-sm text-slate-500 mt-2">Across all agents</p>
        </div>

        <div className="bg-white p-6 rounded-xl border border-slate-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-slate-600">Open Alerts</p>
              <p className="text-2xl font-bold text-slate-900 mt-1">7</p>
            </div>
            <div className="w-12 h-12 bg-amber-100 rounded-lg flex items-center justify-center">
              <AlertTriangle className="w-6 h-6 text-amber-600" />
            </div>
          </div>
          <p className="text-sm text-amber-600 mt-2">2 require attention</p>
        </div>

        <div className="bg-white p-6 rounded-xl border border-slate-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-slate-600">Avg Resiliency</p>
              <p className="text-2xl font-bold text-slate-900 mt-1">88.0</p>
            </div>
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
              <TrendingUp className="w-6 h-6 text-purple-600" />
            </div>
          </div>
          <p className="text-sm text-green-600 mt-2 flex items-center gap-1">
            <TrendingUp className="w-4 h-4" />
            +2.3 from last week
          </p>
        </div>
      </div>

      {/* Agent Status Grid */}
      <div className="bg-white p-6 rounded-xl border border-slate-200">
        <h2 className="text-lg font-semibold text-slate-900 mb-4">Agent Status</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {agentStats.map((agent) => {
            const Icon = agent.icon;
            return (
              <div key={agent.name} className="border border-slate-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                <div className="flex items-center justify-between mb-2">
                  <Icon className="w-6 h-6 text-slate-600" />
                  <div className={`w-2 h-2 rounded-full ${
                    agent.status === 'healthy' ? 'bg-green-500' :
                    agent.status === 'warning' ? 'bg-amber-500' : 'bg-blue-500'
                  }`}></div>
                </div>
                <p className="font-medium text-slate-900 text-sm">{agent.name}</p>
                <p className="text-xs text-slate-500 mt-1">
                  {agent.experiments || agent.vendors || agent.audits || agent.findings || agent.models || agent.incidents} active
                </p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Experiment Trends */}
        <div className="bg-white p-6 rounded-xl border border-slate-200">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">Experiment Trends</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={experimentData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="experiments" fill="#3b82f6" name="Total" />
                <Bar dataKey="successful" fill="#22c55e" name="Successful" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Vendor Distribution */}
        <div className="bg-white p-6 rounded-xl border border-slate-200">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">Vendor Distribution</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={vendorTierData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value }) => `${name}: ${value}`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {vendorTierData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white p-6 rounded-xl border border-slate-200">
        <h2 className="text-lg font-semibold text-slate-900 mb-4">Recent Activity</h2>
        <div className="space-y-3">
          {recentActivity.map((activity) => (
            <div key={activity.id} className="flex items-center gap-4 p-3 bg-slate-50 rounded-lg">
              <div className={`w-2 h-2 rounded-full ${
                activity.type === 'success' ? 'bg-green-500' :
                activity.type === 'warning' ? 'bg-amber-500' : 'bg-red-500'
              }`}></div>
              <div className="flex-1">
                <p className="text-sm font-medium text-slate-900">{activity.action}</p>
                <p className="text-xs text-slate-500">{activity.agent} • {activity.time}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
