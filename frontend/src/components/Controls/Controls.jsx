import React from 'react';
import { motion } from 'framer-motion';
import { USER_LOCATIONS, ROUTING_MODES } from '../../data/constants';
import './Controls.css';

export default function Controls({
  selectedLocation,
  onLocationChange,
  routingMode,
  onRoutingModeChange,
  cdnEnabled,
  onCdnToggle,
  gaEnabled,
  onGaToggle,
  contentType,
  onContentTypeChange,
  onSimulate,
  onBatchSimulate,
  onTrafficSpike,
  isLoading,
}) {
  return (
    <motion.div
      className="controls-panel glass-card"
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
    >
      <div className="controls-header">
        <h2 className="controls-title">
          <span className="title-icon">🎛️</span>
          Control Panel
        </h2>
      </div>

      {/* Location Selector */}
      <div className="control-group">
        <label className="control-label">📍 User Location</label>
        <select
          className="select"
          value={selectedLocation}
          onChange={(e) => onLocationChange(parseInt(e.target.value))}
          id="location-select"
        >
          {USER_LOCATIONS.map((loc, i) => (
            <option key={loc.label} value={i}>{loc.label}</option>
          ))}
        </select>
      </div>

      {/* Routing Mode */}
      <div className="control-group">
        <label className="control-label">🌐 Routing Mode</label>
        <div className="routing-modes">
          {ROUTING_MODES.map((mode) => (
            <button
              key={mode.value}
              className={`mode-btn ${routingMode === mode.value ? 'active' : ''}`}
              onClick={() => onRoutingModeChange(mode.value)}
              style={{
                '--mode-color': mode.color,
                borderColor: routingMode === mode.value ? mode.color : 'transparent'
              }}
              id={`mode-${mode.value}`}
              title={mode.description}
            >
              <span className="mode-dot" style={{ background: mode.color }}></span>
              {mode.label}
            </button>
          ))}
        </div>
      </div>

      {/* Toggles */}
      <div className="control-group">
        <label className="control-label">⚙️ Features</label>
        <div className="toggles-grid">
          <div className="toggle-wrapper" onClick={onCdnToggle}>
            <div className={`toggle ${cdnEnabled ? 'active' : ''}`}>
              <div className="toggle-knob"></div>
            </div>
            <span className="toggle-label">CloudFront CDN</span>
          </div>
          <div className="toggle-wrapper" onClick={onGaToggle}>
            <div className={`toggle ${gaEnabled ? 'active' : ''}`}>
              <div className="toggle-knob"></div>
            </div>
            <span className="toggle-label">Global Accelerator</span>
          </div>
        </div>
      </div>

      {/* Content Type */}
      <div className="control-group">
        <label className="control-label">📄 Content Type</label>
        <div className="tab-group">
          <button
            className={`tab ${contentType === 'static' ? 'active' : ''}`}
            onClick={() => onContentTypeChange('static')}
          >Static</button>
          <button
            className={`tab ${contentType === 'dynamic' ? 'active' : ''}`}
            onClick={() => onContentTypeChange('dynamic')}
          >Dynamic</button>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="control-actions">
        <button
          className="btn btn-primary w-full"
          onClick={onSimulate}
          disabled={isLoading}
          id="simulate-btn"
        >
          {isLoading ? (
            <span className="btn-loading">⏳ Simulating...</span>
          ) : (
            <>🚀 Send Request</>
          )}
        </button>
        <button
          className="btn btn-outline w-full"
          onClick={onBatchSimulate}
          disabled={isLoading}
          id="batch-simulate-btn"
        >
          📊 Compare All Modes
        </button>
        <button
          className="btn btn-danger w-full btn-sm"
          onClick={onTrafficSpike}
          disabled={isLoading}
          id="spike-btn"
        >
          ⚡ Simulate Traffic Spike
        </button>
      </div>
    </motion.div>
  );
}
