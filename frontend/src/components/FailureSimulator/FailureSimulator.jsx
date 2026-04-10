import React from 'react';
import { motion } from 'framer-motion';
import './FailureSimulator.css';

export default function FailureSimulator({ regions = [], onToggleRegion, recommendation }) {
  return (
    <motion.div
      className="failure-sim glass-card"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.4 }}
    >
      <h3 className="failure-title">
        <span>💥</span> Region Failure Simulator
      </h3>

      <div className="region-cards">
        {regions.map((region) => (
          <div key={region.code} className={`region-card ${region.status}`}>
            <div className="region-card-header">
              <span className="region-city">{region.city}</span>
              <span className={`badge badge-${region.status}`}>{region.status}</span>
            </div>
            <div className="region-card-code">{region.code}</div>
            <div className="region-card-stats">
              <span>Reqs: {region.request_count}</span>
              <span>Avg: {region.avg_latency_ms?.toFixed(0)}ms</span>
            </div>
            <button
              className={`btn btn-sm w-full ${region.status === 'down' ? 'btn-success' : 'btn-danger'}`}
              onClick={() => onToggleRegion(region.code)}
            >
              {region.status === 'down' ? '🔄 Recover' : '💀 Fail Region'}
            </button>
          </div>
        ))}
      </div>

      {/* AI Recommendation */}
      {recommendation && (
        <div className="ai-recommendation">
          <h4 className="ai-title">
            <span>🧠</span> AI Recommendation
          </h4>
          <div className="ai-strategy">
            <span className="ai-label">Recommended Strategy</span>
            <span className="ai-value">{recommendation.recommended_strategy?.replace('_', ' ')}</span>
          </div>
          <div className="ai-confidence">
            <span className="ai-label">Confidence</span>
            <div className="confidence-bar">
              <motion.div
                className="confidence-fill"
                initial={{ width: 0 }}
                animate={{ width: `${(recommendation.confidence || 0) * 100}%` }}
                transition={{ duration: 0.6 }}
              />
            </div>
            <span className="ai-pct">{((recommendation.confidence || 0) * 100).toFixed(0)}%</span>
          </div>
          <div className="ai-savings-grid">
            <div className="ai-saving">
              <span className="ai-label">Latency Savings</span>
              <span className="ai-saving-value green">{recommendation.latency_savings_pct}%</span>
            </div>
            <div className="ai-saving">
              <span className="ai-label">Cost Savings</span>
              <span className="ai-saving-value cyan">{recommendation.cost_savings_pct}%</span>
            </div>
          </div>
          {recommendation.reasoning?.length > 0 && (
            <div className="ai-reasoning">
              {recommendation.reasoning.map((r, i) => (
                <p key={i} className="reasoning-item">💡 {r}</p>
              ))}
            </div>
          )}
        </div>
      )}
    </motion.div>
  );
}
