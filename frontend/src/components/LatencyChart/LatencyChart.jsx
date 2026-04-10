import React from 'react';
import {
  AreaChart, Area, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Legend,
} from 'recharts';
import { motion } from 'framer-motion';
import { MODE_COLORS } from '../../data/constants';
import './LatencyChart.css';

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="chart-tooltip">
      <p className="chart-tooltip-label">{label}</p>
      {payload.map((entry, i) => (
        <p key={i} style={{ color: entry.color }}>
          {entry.name}: {typeof entry.value === 'number' ? entry.value.toFixed(2) : entry.value}
          {entry.name.includes('Latency') ? 'ms' : entry.name.includes('Cost') ? ' USD' : ''}
        </p>
      ))}
    </div>
  );
};

export function LatencyComparisonChart({ history = [] }) {
  const data = history.slice(-20).map((entry, i) => ({
    name: `#${i + 1}`,
    Default: entry.default || 0,
    Optimized: entry.optimized || 0,
  }));

  return (
    <motion.div
      className="chart-card glass-card"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.1 }}
    >
      <h3 className="chart-title">
        <span className="chart-icon">⚡</span>
        Latency Comparison
      </h3>
      <div className="chart-wrapper">
        <ResponsiveContainer width="100%" height={200}>
          <AreaChart data={data}>
            <defs>
              <linearGradient id="gradDefault" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={MODE_COLORS.default} stopOpacity={0.3} />
                <stop offset="95%" stopColor={MODE_COLORS.default} stopOpacity={0} />
              </linearGradient>
              <linearGradient id="gradOptimized" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={MODE_COLORS.optimized} stopOpacity={0.3} />
                <stop offset="95%" stopColor={MODE_COLORS.optimized} stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
            <XAxis dataKey="name" tick={{ fontSize: 10, fill: '#64748b' }} />
            <YAxis tick={{ fontSize: 10, fill: '#64748b' }} />
            <Tooltip content={<CustomTooltip />} />
            <Legend wrapperStyle={{ fontSize: '11px' }} />
            <Area
              type="monotone" dataKey="Default" name="Default Latency"
              stroke={MODE_COLORS.default} fill="url(#gradDefault)"
              strokeWidth={2} dot={false}
            />
            <Area
              type="monotone" dataKey="Optimized" name="Optimized Latency"
              stroke={MODE_COLORS.optimized} fill="url(#gradOptimized)"
              strokeWidth={2} dot={false}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </motion.div>
  );
}

export function CostComparisonChart({ batchResult }) {
  if (!batchResult) return null;

  const data = [
    {
      name: 'Default',
      Cost: (batchResult.default?.cost_usd || 0) * 1e6,
      fill: MODE_COLORS.default,
    },
    {
      name: 'GA',
      Cost: (batchResult.global_accelerator?.cost_usd || 0) * 1e6,
      fill: MODE_COLORS.global_accelerator,
    },
    {
      name: 'CDN',
      Cost: (batchResult.cdn_only?.cost_usd || 0) * 1e6,
      fill: MODE_COLORS.cdn_only,
    },
    {
      name: 'Optimized',
      Cost: (batchResult.optimized?.cost_usd || 0) * 1e6,
      fill: MODE_COLORS.optimized,
    },
  ];

  return (
    <motion.div
      className="chart-card glass-card"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
    >
      <h3 className="chart-title">
        <span className="chart-icon">💰</span>
        Cost per Request (μ$)
      </h3>
      <div className="chart-wrapper">
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
            <XAxis dataKey="name" tick={{ fontSize: 10, fill: '#64748b' }} />
            <YAxis tick={{ fontSize: 10, fill: '#64748b' }} />
            <Tooltip content={<CustomTooltip />} />
            <Bar dataKey="Cost" name="Cost (μ$)" radius={[6, 6, 0, 0]}>
              {data.map((entry, i) => (
                <rect key={i} fill={entry.fill} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </motion.div>
  );
}

export function LatencyBarChart({ batchResult }) {
  if (!batchResult) return null;

  const data = [
    { name: 'Default', Latency: batchResult.default?.total_latency_ms || 0, fill: MODE_COLORS.default },
    { name: 'GA', Latency: batchResult.global_accelerator?.total_latency_ms || 0, fill: MODE_COLORS.global_accelerator },
    { name: 'CDN', Latency: batchResult.cdn_only?.total_latency_ms || 0, fill: MODE_COLORS.cdn_only },
    { name: 'Optimized', Latency: batchResult.optimized?.total_latency_ms || 0, fill: MODE_COLORS.optimized },
  ];

  return (
    <motion.div
      className="chart-card glass-card"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.15 }}
    >
      <h3 className="chart-title">
        <span className="chart-icon">📊</span>
        Latency by Mode (ms)
      </h3>
      <div className="chart-wrapper">
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
            <XAxis dataKey="name" tick={{ fontSize: 10, fill: '#64748b' }} />
            <YAxis tick={{ fontSize: 10, fill: '#64748b' }} />
            <Tooltip content={<CustomTooltip />} />
            <Bar dataKey="Latency" name="Latency (ms)" radius={[6, 6, 0, 0]}>
              {data.map((entry, i) => (
                <rect key={i} fill={entry.fill} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </motion.div>
  );
}
