import React, { useState, useEffect } from 'react';
import { DollarSign, TrendingDown, AlertTriangle, RefreshCw, Play, Download, Sparkles, TrendingUp, Server, Database } from 'lucide-react';
import { PieChart, Pie, Cell, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area } from 'recharts';
import apiService from './services/api';
import { SEVERITY_COLORS, SERVICE_COLORS } from './config';
import './App.css';

function App() {
  const [loading, setLoading] = useState(true);
  const [summary, setSummary] = useState(null);
  const [scans, setScans] = useState([]);
  const [error, setError] = useState(null);
  const [scanning, setScanning] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [summaryData, scansData] = await Promise.all([
        apiService.getSummary(),
        apiService.getScans(30)
      ]);
      setSummary(summaryData);
      setScans(scansData.scans || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleTriggerScan = async () => {
    setScanning(true);
    try {
      await apiService.triggerScan();
      alert('Scan triggered! Refreshing data in 30 seconds...');
      setTimeout(loadData, 30000);
    } catch (err) {
      alert(`Failed to trigger scan: ${err.message}`);
    } finally {
      setScanning(false);
    }
  };

  const exportToCSV = () => {
    if (!summary?.latest_scan?.detailed_results) return;
    
    const findings = summary.latest_scan.detailed_results.flatMap(service => 
      service.findings?.map(f => ({
        Service: service.service,
        ResourceID: f.volume_id || f.instance_id || f.allocation_id || f.snapshot_id,
        Type: service.finding_type,
        MonthlyCost: f.monthly_cost_usd,
        AnnualSavings: f.annual_savings_usd,
        Severity: f.severity,
        Recommendation: f.recommendation
      })) || []
    );

    const csv = [
      Object.keys(findings[0] || {}).join(','),
      ...findings.map(row => Object.values(row).join(','))
    ].join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `cost-optimization-report-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="relative">
            <div className="w-20 h-20 border-4 border-purple-200 border-t-purple-600 rounded-full animate-spin mx-auto mb-6"></div>
            <Sparkles className="w-8 h-8 text-purple-400 absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 animate-pulse" />
          </div>
          <p className="text-white text-lg font-medium">Loading your cost insights...</p>
          <p className="text-purple-300 text-sm mt-2">Analyzing AWS resources</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-red-900 to-slate-900 flex items-center justify-center p-4">
        <div className="bg-white/10 backdrop-blur-lg border border-red-500/20 rounded-2xl p-8 max-w-md w-full">
          <AlertTriangle className="w-16 h-16 text-red-400 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-white mb-3 text-center">Connection Error</h2>
          <p className="text-red-200 mb-6 text-center">{error}</p>
          <button
            onClick={loadData}
            className="w-full bg-gradient-to-r from-red-500 to-red-600 text-white px-6 py-3 rounded-xl hover:from-red-600 hover:to-red-700 transform hover:scale-105 transition-all duration-200 font-semibold shadow-lg"
          >
            Retry Connection
          </button>
        </div>
      </div>
    );
  }

  const latest = summary?.latest_scan;
  const serviceBreakdown = summary?.service_breakdown || [];
  const insights = summary?.insights || [];
  const trends = summary?.trends || {};

  const trendData = scans.slice(0, 14).reverse().map(scan => ({
    date: new Date(scan.timestamp).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    savings: scan.monthly_savings_usd,
    findings: scan.total_findings
  }));

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Animated Background Elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl animate-pulse delay-1000"></div>
      </div>

      {/* Header */}
      <header className="relative bg-white/5 backdrop-blur-md border-b border-white/10 shadow-2xl">
        <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <div className="bg-gradient-to-r from-purple-500 to-blue-500 p-2 rounded-xl">
                  <Sparkles className="w-8 h-8 text-white" />
                </div>
                <div>
                  <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-400 via-pink-400 to-blue-400 bg-clip-text text-transparent">
                    AWS Cost Optimizer
                  </h1>
                  <p className="text-sm text-purple-300 mt-1">
                    💰 Last scan: {latest?.timestamp ? new Date(latest.timestamp).toLocaleString() : 'No scans yet'}
                  </p>
                </div>
              </div>
            </div>
            <div className="flex flex-wrap gap-3">
              <button
                onClick={loadData}
                className="flex items-center gap-2 px-5 py-2.5 bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl hover:bg-white/20 text-white transform hover:scale-105 transition-all duration-200 shadow-lg"
              >
                <RefreshCw className="w-4 h-4" />
                <span className="font-medium">Refresh</span>
              </button>
              <button
                onClick={handleTriggerScan}
                disabled={scanning}
                className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-purple-500 to-blue-500 text-white rounded-xl hover:from-purple-600 hover:to-blue-600 disabled:from-gray-500 disabled:to-gray-600 transform hover:scale-105 transition-all duration-200 font-semibold shadow-xl"
              >
                <Play className="w-4 h-4" />
                {scanning ? 'Scanning...' : 'Run Scan'}
              </button>
              <button
                onClick={exportToCSV}
                className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-green-500 to-emerald-500 text-white rounded-xl hover:from-green-600 hover:to-emerald-600 transform hover:scale-105 transition-all duration-200 font-semibold shadow-xl"
              >
                <Download className="w-4 h-4" />
                Export
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="relative max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <SummaryCard
            icon={<AlertTriangle className="w-7 h-7" />}
            title="Total Findings"
            value={latest?.total_findings || 0}
            subtitle={`${trends.avg_findings_per_scan?.toFixed(1) || 0} avg per scan`}
            gradient="from-red-500 to-orange-500"
            iconBg="from-red-500/20 to-orange-500/20"
          />
          <SummaryCard
            icon={<DollarSign className="w-7 h-7" />}
            title="Monthly Savings"
            value={`$${(latest?.monthly_savings_usd || 0).toFixed(2)}`}
            subtitle={`$${trends.avg_monthly_savings?.toFixed(2) || 0} average`}
            gradient="from-green-500 to-emerald-500"
            iconBg="from-green-500/20 to-emerald-500/20"
          />
          <SummaryCard
            icon={<TrendingDown className="w-7 h-7" />}
            title="Annual Savings"
            value={`$${(latest?.annual_savings_usd || 0).toFixed(2)}`}
            subtitle={`${trends.total_scans || 0} total scans`}
            gradient="from-purple-500 to-blue-500"
            iconBg="from-purple-500/20 to-blue-500/20"
          />
        </div>

        {/* Insights Panel */}
        {insights.length > 0 && (
          <div className="bg-white/5 backdrop-blur-lg rounded-2xl border border-white/10 p-6 mb-8 shadow-2xl">
            <div className="flex items-center gap-2 mb-4">
              <Sparkles className="w-6 h-6 text-yellow-400" />
              <h2 className="text-2xl font-bold text-white">AI Insights</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {insights.map((insight, idx) => (
                <InsightCard key={idx} insight={insight} />
              ))}
            </div>
          </div>
        )}

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Service Breakdown Chart */}
          <div className="bg-white/5 backdrop-blur-lg rounded-2xl border border-white/10 p-6 shadow-2xl">
            <div className="flex items-center gap-2 mb-4">
              <Server className="w-6 h-6 text-purple-400" />
              <h2 className="text-xl font-bold text-white">Savings by Service</h2>
            </div>
            {serviceBreakdown.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={serviceBreakdown}
                    dataKey="monthly_savings_usd"
                    nameKey="service"
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    label={(entry) => `$${entry.monthly_savings_usd.toFixed(0)}`}
                    labelLine={false}
                  >
                    {serviceBreakdown.map((entry, index) => (
                      <Cell key={index} fill={SERVICE_COLORS[entry.service] || '#8884d8'} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ background: 'rgba(15, 23, 42, 0.9)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px' }}
                    labelStyle={{ color: '#fff' }}
                  />
                  <Legend wrapperStyle={{ color: '#fff' }} />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-[300px] flex items-center justify-center">
                <p className="text-purple-300">No data available</p>
              </div>
            )}
          </div>

          {/* Savings Trend Chart */}
          <div className="bg-white/5 backdrop-blur-lg rounded-2xl border border-white/10 p-6 shadow-2xl">
            <div className="flex items-center gap-2 mb-4">
              <TrendingUp className="w-6 h-6 text-blue-400" />
              <h2 className="text-xl font-bold text-white">Savings Trend</h2>
            </div>
            {trendData.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={trendData}>
                  <defs>
                    <linearGradient id="colorSavings" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.8}/>
                      <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                  <XAxis dataKey="date" stroke="#9ca3af" />
                  <YAxis stroke="#9ca3af" />
                  <Tooltip 
                    contentStyle={{ background: 'rgba(15, 23, 42, 0.9)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px' }}
                    labelStyle={{ color: '#fff' }}
                  />
                  <Area type="monotone" dataKey="savings" stroke="#8b5cf6" strokeWidth={3} fillOpacity={1} fill="url(#colorSavings)" name="Savings ($)" />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-[300px] flex items-center justify-center">
                <p className="text-purple-300">Run more scans to see trends</p>
              </div>
            )}
          </div>
        </div>

        {/* Findings Table */}
        {latest?.detailed_results && <FindingsTable results={latest.detailed_results} />}

        {/* Scan History */}
        <ScanHistory scans={scans} />
      </main>
    </div>
  );
}

// Enhanced Summary Card Component
function SummaryCard({ icon, title, value, subtitle, gradient, iconBg }) {
  return (
    <div className="bg-white/5 backdrop-blur-lg rounded-2xl border border-white/10 p-6 shadow-2xl transform hover:scale-105 transition-all duration-300 hover:shadow-purple-500/20">
      <div className="flex items-start justify-between mb-4">
        <div className={`bg-gradient-to-br ${iconBg} p-3 rounded-xl backdrop-blur-sm`}>
          <div className={`bg-gradient-to-r ${gradient} bg-clip-text text-transparent`}>
            {icon}
          </div>
        </div>
      </div>
      <p className="text-sm text-purple-300 mb-1 font-medium">{title}</p>
      <p className="text-4xl font-bold text-white mb-1">{value}</p>
      <p className="text-xs text-purple-400">{subtitle}</p>
    </div>
  );
}

// Enhanced Insight Card
function InsightCard({ insight }) {
  const severityConfig = {
    HIGH: { bg: 'from-red-500/20 to-orange-500/20', border: 'border-red-500/30', text: 'text-red-300', icon: '🔥' },
    MEDIUM: { bg: 'from-yellow-500/20 to-orange-500/20', border: 'border-yellow-500/30', text: 'text-yellow-300', icon: '⚠️' },
    LOW: { bg: 'from-blue-500/20 to-purple-500/20', border: 'border-blue-500/30', text: 'text-blue-300', icon: 'ℹ️' }
  };

  const config = severityConfig[insight.severity] || severityConfig.LOW;

  return (
    <div className={`bg-gradient-to-br ${config.bg} backdrop-blur-sm border ${config.border} rounded-xl p-4 transform hover:scale-105 transition-all duration-200`}>
      <div className="flex items-start gap-3">
        <span className="text-2xl">{config.icon}</span>
        <div className="flex-1">
          <p className={`font-semibold ${config.text} mb-1`}>
            {insight.type.replace(/_/g, ' ')}
          </p>
          <p className="text-sm text-white/80">{insight.message}</p>
        </div>
      </div>
    </div>
  );
}

// Enhanced Findings Table
function FindingsTable({ results }) {
  const [filter, setFilter] = useState('all');
  const [search, setSearch] = useState('');

  const allFindings = results.flatMap(service =>
    (service.findings || []).map(f => ({
      ...f,
      service: service.service,
      finding_type: service.finding_type
    }))
  );

  const filtered = allFindings.filter(f => {
    const matchesFilter = filter === 'all' || f.service === filter;
    const matchesSearch = search === '' || 
      Object.values(f).some(v => 
        String(v).toLowerCase().includes(search.toLowerCase())
      );
    return matchesFilter && matchesSearch;
  });

  const services = [...new Set(results.map(r => r.service))];

  return (
    <div className="bg-white/5 backdrop-blur-lg rounded-2xl border border-white/10 p-6 mb-8 shadow-2xl">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
        <div className="flex items-center gap-2">
          <Database className="w-6 h-6 text-purple-400" />
          <h2 className="text-xl font-bold text-white">
            Detailed Findings <span className="text-purple-400">({filtered.length})</span>
          </h2>
        </div>
        <div className="flex gap-3">
          <input
            type="text"
            placeholder="🔍 Search..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="px-4 py-2 bg-white/10 border border-white/20 rounded-xl text-white placeholder-purple-300 focus:outline-none focus:ring-2 focus:ring-purple-500 backdrop-blur-sm"
          />
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="px-4 py-2 bg-white/10 border border-white/20 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-purple-500 backdrop-blur-sm"
          >
            <option value="all">All Services</option>
            {services.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
        </div>
      </div>

      <div className="overflow-x-auto rounded-xl">
        <table className="w-full">
          <thead className="bg-white/10 backdrop-blur-sm">
            <tr>
              <th className="px-4 py-3 text-left text-sm font-semibold text-purple-300">Service</th>
              <th className="px-4 py-3 text-left text-sm font-semibold text-purple-300">Resource</th>
              <th className="px-4 py-3 text-left text-sm font-semibold text-purple-300">Type</th>
              <th className="px-4 py-3 text-right text-sm font-semibold text-purple-300">Monthly</th>
              <th className="px-4 py-3 text-right text-sm font-semibold text-purple-300">Annual</th>
              <th className="px-4 py-3 text-left text-sm font-semibold text-purple-300">Severity</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {filtered.map((f, idx) => (
              <tr key={idx} className="hover:bg-white/5 transition-colors duration-150">
                <td className="px-4 py-3 text-sm text-white">{f.service}</td>
                <td className="px-4 py-3 text-sm font-mono text-xs text-purple-300">
                  {f.volume_id || f.instance_id || f.allocation_id || f.snapshot_id}
                </td>
                <td className="px-4 py-3 text-sm text-white">{f.finding_type}</td>
                <td className="px-4 py-3 text-sm text-right text-white">${f.monthly_cost_usd?.toFixed(2)}</td>
                <td className="px-4 py-3 text-sm text-right font-semibold text-green-400">${f.annual_savings_usd?.toFixed(2)}</td>
                <td className="px-4 py-3">
                  <span className={`px-3 py-1 text-xs rounded-full font-medium ${
                    f.severity === 'HIGH' ? 'bg-red-500/20 text-red-300 border border-red-500/30' :
                    f.severity === 'MEDIUM' ? 'bg-yellow-500/20 text-yellow-300 border border-yellow-500/30' :
                    'bg-blue-500/20 text-blue-300 border border-blue-500/30'
                  }`}>
                    {f.severity}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// Enhanced Scan History
function ScanHistory({ scans }) {
  return (
    <div className="bg-white/5 backdrop-blur-lg rounded-2xl border border-white/10 p-6 shadow-2xl">
      <div className="flex items-center gap-2 mb-4">
        <RefreshCw className="w-6 h-6 text-purple-400" />
        <h2 className="text-xl font-bold text-white">Recent Scans</h2>
      </div>
      <div className="overflow-x-auto rounded-xl">
        <table className="w-full">
          <thead className="bg-white/10 backdrop-blur-sm">
            <tr>
              <th className="px-4 py-3 text-left text-sm font-semibold text-purple-300">Timestamp</th>
              <th className="px-4 py-3 text-right text-sm font-semibold text-purple-300">Findings</th>
              <th className="px-4 py-3 text-right text-sm font-semibold text-purple-300">Monthly</th>
              <th className="px-4 py-3 text-right text-sm font-semibold text-purple-300">Annual</th>
              <th className="px-4 py-3 text-left text-sm font-semibold text-purple-300">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {scans.slice(0, 10).map((scan, idx) => (
              <tr key={idx} className="hover:bg-white/5 transition-colors duration-150">
                <td className="px-4 py-3 text-sm text-white">{new Date(scan.timestamp).toLocaleString()}</td>
                <td className="px-4 py-3 text-sm text-right text-white">{scan.total_findings}</td>
                <td className="px-4 py-3 text-sm text-right text-white">${scan.monthly_savings_usd?.toFixed(2)}</td>
                <td className="px-4 py-3 text-sm text-right font-semibold text-green-400">${scan.annual_savings_usd?.toFixed(2)}</td>
                <td className="px-4 py-3">
                  <span className="px-3 py-1 text-xs rounded-full font-medium bg-green-500/20 text-green-300 border border-green-500/30">
                    {scan.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default App;