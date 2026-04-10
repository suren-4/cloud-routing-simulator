import React from 'react';
import { motion } from 'framer-motion';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
  ResponsiveContainer, Tooltip,
} from 'recharts';
import './MonitoringDash.css';

export default function MonitoringDash({ metrics, metricsHistory = [] }) {
  if (!metrics) return null;

  const historyData = metricsHistory.slice(-30).map((m, i) => ({
    time: `T-${30 - i}`,
    latency: m.avg_latency_ms || 0,
    rps: m.requests_per_second || 0,
    cacheHit: (m.cache_hit_ratio || 0) * 100,
  }));

  return (
    <motion.div
      className="monitoring-dash glass-card"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3 }}
    >
      <div className="monitoring-header">
        <h3>
          <span>📊</span> Monitoring Dashboard
        </h3>
        <span className="badge badge-healthy">LIVE</span>
      </div>

      {/* Key Metrics Grid */}
      <div className="metrics-grid">
        <div className="metric-card">
          <span className="metric-label">Total Requests</span>
          <span className="metric-value cyan">{metrics.total_requests}</span>
        </div>
        <div className="metric-card">
          <span className="metric-label">Avg Latency</span>
          <span className="metric-value">{metrics.avg_latency_ms?.toFixed(1)}ms</span>
        </div>
        <div className="metric-card">
          <span className="metric-label">P95 Latency</span>
          <span className="metric-value orange">{metrics.p95_latency_ms?.toFixed(1)}ms</span>
        </div>
        <div className="metric-card">
          <span className="metric-label">P99 Latency</span>
          <span className="metric-value red">{metrics.p99_latency_ms?.toFixed(1)}ms</span>
        </div>
        <div className="metric-card">
          <span className="metric-label">Cache Hit Rate</span>
          <span className="metric-value green">
            {(metrics.cache_hit_ratio * 100).toFixed(1)}%
          </span>
        </div>
        <div className="metric-card">
          <span className="metric-label">RPS</span>
          <span className="metric-value cyan">{metrics.requests_per_second?.toFixed(1)}</span>
        </div>
        <div className="metric-card">
          <span className="metric-label">Total Cost</span>
          <span className="metric-value">${metrics.total_cost_usd?.toFixed(6)}</span>
        </div>
        <div className="metric-card">
          <span className="metric-label">Active Regions</span>
          <span className="metric-value cyan">{metrics.active_regions}</span>
        </div>
      </div>

      {/* Latency Time Series */}
      {historyData.length > 2 && (
        <div className="monitoring-chart">
          <h4 className="monitoring-chart-title">Latency Over Time</h4>
          <ResponsiveContainer width="100%" height={120}>
            <AreaChart data={historyData}>
              <defs>
                <linearGradient id="monLatGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#00d4ff" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#00d4ff" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
              <XAxis dataKey="time" tick={{ fontSize: 8, fill: '#64748b' }} />
              <YAxis tick={{ fontSize: 8, fill: '#64748b' }} />
              <Tooltip
                contentStyle={{
                  background: 'rgba(10,14,26,0.95)',
                  border: '1px solid rgba(255,255,255,0.1)',
                  borderRadius: '8px',
                  fontSize: '11px',
                }}
              />
              <Area
                type="monotone" dataKey="latency" name="Avg Latency (ms)"
                stroke="#00d4ff" fill="url(#monLatGrad)" strokeWidth={2} dot={false}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Per-Region Load */}
      {metrics.regions_metrics?.length > 0 && (
        <div className="region-loads">
          <h4 className="monitoring-chart-title">Region Load</h4>
          <div className="load-bars">
            {metrics.regions_metrics.map((r) => (
              <div key={r.code} className="load-bar-item">
                <div className="load-bar-header">
                  <span className="load-bar-label">{r.code}</span>
                  <span className="load-bar-value">{(r.load * 100).toFixed(0)}%</span>
                </div>
                <div className="load-bar-track">
                  <motion.div
                    className="load-bar-fill"
                    initial={{ width: 0 }}
                    animate={{ width: `${Math.min(r.load * 100, 100)}%` }}
                    transition={{ duration: 0.5 }}
                    style={{
                      background: r.load > 0.8 ? 'var(--accent-red)' :
                                  r.load > 0.5 ? 'var(--accent-orange)' :
                                  'var(--accent-cyan)',
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </motion.div>
  );
}
