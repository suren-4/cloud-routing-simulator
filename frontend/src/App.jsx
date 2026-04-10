import React, { useState, useEffect, useCallback } from 'react';
import WorldMap from './components/WorldMap/WorldMap.jsx';
import Controls from './components/Controls/Controls.jsx';
import { LatencyComparisonChart, CostComparisonChart, LatencyBarChart } from './components/LatencyChart/LatencyChart.jsx';
import ComparisonView from './components/ComparisonView/ComparisonView.jsx';
import MonitoringDash from './components/MonitoringDash/MonitoringDash.jsx';
import FailureSimulator from './components/FailureSimulator/FailureSimulator.jsx';
import { USER_LOCATIONS } from './data/constants.js';
import * as api from './services/api.js';
import './App.css';

export default function App() {
  // State
  const [selectedLocationIdx, setSelectedLocationIdx] = useState(0);
  const [routingMode, setRoutingMode] = useState('default');
  const [cdnEnabled, setCdnEnabled] = useState(false);
  const [gaEnabled, setGaEnabled] = useState(false);
  const [contentType, setContentType] = useState('dynamic');
  const [isLoading, setIsLoading] = useState(false);

  // Data
  const [regions, setRegions] = useState([]);
  const [edgeLocations, setEdgeLocations] = useState([]);
  const [simulationResult, setSimulationResult] = useState(null);
  const [batchResult, setBatchResult] = useState(null);
  const [spikeResult, setSpikeResult] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [metricsHistory, setMetricsHistory] = useState([]);
  const [latencyHistory, setLatencyHistory] = useState([]);
  const [recommendation, setRecommendation] = useState(null);
  const [activeTab, setActiveTab] = useState('map');

  const userLocation = USER_LOCATIONS[selectedLocationIdx];

  // Sync routing mode with toggles
  useEffect(() => {
    if (cdnEnabled && gaEnabled) setRoutingMode('optimized');
    else if (cdnEnabled) setRoutingMode('cdn_only');
    else if (gaEnabled) setRoutingMode('global_accelerator');
    else setRoutingMode('default');
  }, [cdnEnabled, gaEnabled]);

  // Fetch regions on mount
  useEffect(() => {
    api.getRegions().then((data) => {
      setRegions(data.regions || []);
      setEdgeLocations(data.edge_locations || []);
    }).catch(console.error);
  }, []);

  // Auto-refresh metrics
  useEffect(() => {
    const interval = setInterval(() => {
      api.getMetrics().then(setMetrics).catch(() => {});
      api.getMetricsHistory().then((d) => setMetricsHistory(d.history || [])).catch(() => {});
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  const handleSimulate = useCallback(async () => {
    setIsLoading(true);
    try {
      const result = await api.simulateRequest(
        userLocation, routingMode, cdnEnabled, contentType
      );
      setSimulationResult(result);

      // Update latency history
      setLatencyHistory((prev) => {
        const next = [...prev, {
          default: routingMode === 'default' ? result.total_latency_ms : prev[prev.length - 1]?.default || 0,
          optimized: routingMode === 'optimized' ? result.total_latency_ms : prev[prev.length - 1]?.optimized || 0,
        }];
        return next.slice(-30);
      });

      // Refresh regions and metrics
      const regData = await api.getRegions();
      setRegions(regData.regions || []);
      const met = await api.getMetrics();
      setMetrics(met);

      // Get AI recommendation
      const rec = await api.getRecommendation(
        userLocation.latitude, userLocation.longitude
      );
      setRecommendation(rec);
    } catch (err) {
      console.error('Simulation error:', err);
    }
    setIsLoading(false);
  }, [userLocation, routingMode, cdnEnabled, contentType]);

  const handleBatchSimulate = useCallback(async () => {
    setIsLoading(true);
    try {
      const result = await api.batchSimulate(userLocation, contentType);
      setBatchResult(result);
      setSimulationResult(result.optimized);

      // Build full latency history entry
      setLatencyHistory((prev) => [
        ...prev,
        {
          default: result.default?.total_latency_ms || 0,
          optimized: result.optimized?.total_latency_ms || 0,
        },
      ].slice(-30));

      const regData = await api.getRegions();
      setRegions(regData.regions || []);
      const met = await api.getMetrics();
      setMetrics(met);

      const rec = await api.getRecommendation(
        userLocation.latitude, userLocation.longitude
      );
      setRecommendation(rec);
    } catch (err) {
      console.error('Batch simulation error:', err);
    }
    setIsLoading(false);
  }, [userLocation, contentType]);

  const handleTrafficSpike = useCallback(async () => {
    setIsLoading(true);
    try {
      const result = await api.simulateTrafficSpike(userLocation, 5);
      setSpikeResult(result);
      const met = await api.getMetrics();
      setMetrics(met);
    } catch (err) {
      console.error('Spike simulation error:', err);
    }
    setIsLoading(false);
  }, [userLocation]);

  const handleToggleRegion = useCallback(async (code) => {
    try {
      await api.toggleRegion(code);
      const regData = await api.getRegions();
      setRegions(regData.regions || []);
    } catch (err) {
      console.error('Toggle region error:', err);
    }
  }, []);

  const routePath = simulationResult?.route_path || [];

  return (
    <div className="app-layout">
      {/* Header */}
      <header className="app-header">
        <div className="header-brand">
          <span className="brand-icon">🌐</span>
          <div>
            <h1 className="brand-title">Cloud Routing Simulator</h1>
            <p className="brand-sub">Multi-Region Load Optimization with AWS Global Accelerator & CloudFront</p>
          </div>
        </div>
        <div className="header-tabs">
          <button className={`tab ${activeTab === 'map' ? 'active' : ''}`} onClick={() => setActiveTab('map')}>
            🗺️ Map View
          </button>
          <button className={`tab ${activeTab === 'monitor' ? 'active' : ''}`} onClick={() => setActiveTab('monitor')}>
            📊 Monitoring
          </button>
          <button className={`tab ${activeTab === 'failure' ? 'active' : ''}`} onClick={() => setActiveTab('failure')}>
            💥 Failure Sim
          </button>
        </div>
      </header>

      <div className="app-body">
        {/* Left Sidebar - Controls */}
        <aside className="app-sidebar">
          <Controls
            selectedLocation={selectedLocationIdx}
            onLocationChange={setSelectedLocationIdx}
            routingMode={routingMode}
            onRoutingModeChange={(mode) => {
              setRoutingMode(mode);
              setCdnEnabled(mode === 'cdn_only' || mode === 'optimized');
              setGaEnabled(mode === 'global_accelerator' || mode === 'optimized');
            }}
            cdnEnabled={cdnEnabled}
            onCdnToggle={() => setCdnEnabled(!cdnEnabled)}
            gaEnabled={gaEnabled}
            onGaToggle={() => setGaEnabled(!gaEnabled)}
            contentType={contentType}
            onContentTypeChange={setContentType}
            onSimulate={handleSimulate}
            onBatchSimulate={handleBatchSimulate}
            onTrafficSpike={handleTrafficSpike}
            isLoading={isLoading}
          />
        </aside>

        {/* Main Content */}
        <main className="app-main">
          {activeTab === 'map' && (
            <>
              {/* World Map */}
              <section className="map-section">
                <WorldMap
                  regions={regions}
                  edgeLocations={edgeLocations}
                  userLocation={userLocation}
                  routePath={routePath}
                  simulationResult={simulationResult}
                  routingMode={routingMode}
                />
              </section>

              {/* Stats Row */}
              {simulationResult && (
                <section className="stats-row animate-fade-in">
                  <div className="glass-card stat-card">
                    <span className="stat-label">Total Latency</span>
                    <span className="stat-value">{simulationResult.total_latency_ms?.toFixed(1)}ms</span>
                  </div>
                  <div className="glass-card stat-card">
                    <span className="stat-label">Cost per Request</span>
                    <span className="stat-value green">${(simulationResult.cost_usd * 1e6).toFixed(2)}μ</span>
                  </div>
                  <div className="glass-card stat-card">
                    <span className="stat-label">Distance</span>
                    <span className="stat-value orange">{simulationResult.distance_km?.toFixed(0)}km</span>
                  </div>
                  <div className="glass-card stat-card">
                    <span className="stat-label">Cache Hit Rate</span>
                    <span className="stat-value">{(simulationResult.cache_hit_rate * 100).toFixed(1)}%</span>
                  </div>
                </section>
              )}

              {/* Charts Row */}
              <section className="charts-row">
                <LatencyComparisonChart history={latencyHistory} />
                {batchResult && <LatencyBarChart batchResult={batchResult} />}
                {batchResult && <CostComparisonChart batchResult={batchResult} />}
              </section>

              {/* Comparison */}
              {batchResult && (
                <section className="comparison-section">
                  <ComparisonView batchResult={batchResult} spikeResult={spikeResult} />
                </section>
              )}
            </>
          )}

          {activeTab === 'monitor' && (
            <MonitoringDash metrics={metrics} metricsHistory={metricsHistory} />
          )}

          {activeTab === 'failure' && (
            <FailureSimulator
              regions={regions}
              onToggleRegion={handleToggleRegion}
              recommendation={recommendation}
            />
          )}
        </main>
      </div>
    </div>
  );
}
