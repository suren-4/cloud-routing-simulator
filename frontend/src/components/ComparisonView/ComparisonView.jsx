import React from 'react';
import { motion } from 'framer-motion';
import { MODE_COLORS } from '../../data/constants';
import './ComparisonView.css';

export default function ComparisonView({ batchResult, spikeResult }) {
  if (!batchResult) return null;

  const modes = [
    { key: 'default', label: 'Default DNS', icon: '🌐' },
    { key: 'global_accelerator', label: 'Global Accelerator', icon: '🚀' },
    { key: 'cdn_only', label: 'CDN Only', icon: '📦' },
    { key: 'optimized', label: 'Fully Optimized', icon: '⚡' },
  ];

  return (
    <motion.div
      className="comparison-view glass-card"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
    >
      <h3 className="comparison-title">
        <span>📈</span> Performance Comparison
      </h3>

      {/* Summary Stats */}
      <div className="comparison-summary">
        <div className="summary-card improvement">
          <span className="summary-label">Latency Reduction</span>
          <span className="summary-value green">
            {batchResult.latency_reduction_pct?.toFixed(1)}%
          </span>
          <span className="summary-sub">with full optimization</span>
        </div>
        <div className="summary-card savings">
          <span className="summary-label">Cost Savings</span>
          <span className="summary-value" style={{ color: '#00d4ff' }}>
            {batchResult.cost_savings_pct?.toFixed(1)}%
          </span>
          <span className="summary-sub">vs default routing</span>
        </div>
      </div>

      {/* Mode-by-mode comparison */}
      <div className="comparison-table">
        <div className="comparison-header">
          <span>Mode</span>
          <span>Latency</span>
          <span>Cost</span>
          <span>Cache</span>
          <span>Hops</span>
        </div>
        {modes.map((mode, i) => {
          const data = batchResult[mode.key];
          if (!data) return null;
          return (
            <motion.div
              key={mode.key}
              className="comparison-row"
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.08 }}
            >
              <span className="mode-name">
                <span className="mode-indicator" style={{ background: MODE_COLORS[mode.key] }}></span>
                {mode.icon} {mode.label}
              </span>
              <span className="latency-val" style={{ color: MODE_COLORS[mode.key] }}>
                {data.total_latency_ms?.toFixed(1)}ms
              </span>
              <span className="cost-val">
                ${(data.cost_usd * 1e6).toFixed(2)}μ
              </span>
              <span className={`cache-val ${data.cache_hit ? 'hit' : 'miss'}`}>
                {data.cache_hit ? '✅ HIT' : '❌ MISS'}
              </span>
              <span className="hops-val">{data.num_hops}</span>
            </motion.div>
          );
        })}
      </div>

      {/* Flow visualization */}
      <div className="flow-diagram">
        <h4 className="flow-title">Optimized Request Flow</h4>
        <div className="flow-steps">
          {['👤 User', '🌍 Global Accelerator', '📦 CloudFront Edge', '⚖️ Load Balancer', '🖥️ Server'].map((step, i) => (
            <React.Fragment key={i}>
              <motion.div
                className="flow-step"
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: i * 0.1 }}
              >
                {step}
              </motion.div>
              {i < 4 && <span className="flow-arrow">→</span>}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* Traffic Spike Results */}
      {spikeResult && (
        <div className="spike-results">
          <h4 className="spike-title">⚡ Traffic Spike Results</h4>
          <div className="spike-grid">
            <div className="spike-stat">
              <span className="spike-label">Peak RPS</span>
              <span className="spike-value">{spikeResult.peak_rps}</span>
            </div>
            <div className="spike-stat">
              <span className="spike-label">Auto-Scaled</span>
              <span className="spike-value" style={{ color: spikeResult.auto_scaled ? '#00ff88' : '#ff6b35' }}>
                {spikeResult.auto_scaled ? 'Yes ✓' : 'No'}
              </span>
            </div>
            <div className="spike-stat">
              <span className="spike-label">Latency (spike)</span>
              <span className="spike-value" style={{ color: '#ff3355' }}>
                {spikeResult.latency_during_spike?.toFixed(1)}ms
              </span>
            </div>
            <div className="spike-stat">
              <span className="spike-label">Latency (after scale)</span>
              <span className="spike-value" style={{ color: '#00ff88' }}>
                {spikeResult.latency_after_scaling?.toFixed(1)}ms
              </span>
            </div>
          </div>
        </div>
      )}
    </motion.div>
  );
}
