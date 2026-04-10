import React, { useState, useCallback } from 'react';
import {
  ComposableMap,
  Geographies,
  Geography,
  Marker,
  Line,
  ZoomableGroup,
} from 'react-simple-maps';
import { motion, AnimatePresence } from 'framer-motion';
import { HOP_COLORS, MODE_COLORS } from '../../data/constants';
import './WorldMap.css';

const GEO_URL = 'https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json';

export default function WorldMap({
  regions = [],
  edgeLocations = [],
  userLocation,
  routePath = [],
  simulationResult,
  onMapClick,
  routingMode = 'default',
}) {
  const [tooltipContent, setTooltipContent] = useState('');
  const [tooltipPos, setTooltipPos] = useState({ x: 0, y: 0 });
  const [showTooltip, setShowTooltip] = useState(false);

  const handleMapClick = useCallback((e) => {
    // Get coordinate from map projection (not supported directly — use preset locations)
  }, [onMapClick]);

  const getStatusColor = (status) => {
    if (status === 'healthy') return '#00ff88';
    if (status === 'degraded') return '#ff6b35';
    return '#ff3355';
  };

  const routeColor = MODE_COLORS[routingMode] || '#00d4ff';

  return (
    <div className="world-map-container">
      <div className="map-legend">
        <div className="legend-item">
          <span className="legend-dot" style={{ background: '#00ff88' }}></span>
          <span>Healthy Region</span>
        </div>
        <div className="legend-item">
          <span className="legend-dot" style={{ background: '#ff6b35' }}></span>
          <span>Degraded</span>
        </div>
        <div className="legend-item">
          <span className="legend-dot" style={{ background: '#ff3355' }}></span>
          <span>Down</span>
        </div>
        <div className="legend-item">
          <span className="legend-dot" style={{ background: '#a855f7', width: '6px', height: '6px' }}></span>
          <span>Edge Location</span>
        </div>
        <div className="legend-item">
          <span className="legend-dot" style={{ background: '#00d4ff' }}></span>
          <span>User</span>
        </div>
      </div>

      <ComposableMap
        projectionConfig={{ rotate: [-10, 0, 0], scale: 147 }}
        width={800}
        height={400}
        style={{ width: '100%', height: '100%' }}
      >
        <ZoomableGroup>
          {/* World geography */}
          <Geographies geography={GEO_URL}>
            {({ geographies }) =>
              geographies.map((geo) => (
                <Geography
                  key={geo.rsmKey}
                  geography={geo}
                  className="map-geography"
                />
              ))
            }
          </Geographies>

          {/* Edge locations (small dots) */}
          {edgeLocations.map((edge) => (
            <Marker key={edge.code} coordinates={[edge.longitude, edge.latitude]}>
              <circle r={2} fill="#a855f7" opacity={0.5} />
            </Marker>
          ))}

          {/* Route path lines */}
          <AnimatePresence>
            {routePath.length > 1 && routePath.map((hop, i) => {
              if (i === 0) return null;
              const prev = routePath[i - 1];
              return (
                <Line
                  key={`route-${i}`}
                  from={[prev.longitude, prev.latitude]}
                  to={[hop.longitude, hop.latitude]}
                  stroke={routeColor}
                  strokeWidth={2}
                  strokeLinecap="round"
                  className="route-line"
                  strokeOpacity={0.8}
                />
              );
            })}
          </AnimatePresence>

          {/* Route hops */}
          <AnimatePresence>
            {routePath.map((hop, i) => (
              <Marker key={`hop-${i}`} coordinates={[hop.longitude, hop.latitude]}>
                <motion.g
                  initial={{ scale: 0, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  transition={{ delay: i * 0.15, type: 'spring', stiffness: 200 }}
                >
                  {/* Pulse ring */}
                  <circle
                    r={hop.type === 'user' ? 12 : 8}
                    fill={HOP_COLORS[hop.type] || '#00d4ff'}
                    opacity={0.15}
                    className="pulse-ring"
                  />
                  {/* Main dot */}
                  <circle
                    r={hop.type === 'user' ? 5 : 3.5}
                    fill={HOP_COLORS[hop.type] || '#00d4ff'}
                    stroke="white"
                    strokeWidth={1}
                  />
                  {/* Label */}
                  <text
                    textAnchor="middle"
                    y={-12}
                    style={{
                      fontFamily: 'Inter, sans-serif',
                      fontSize: '7px',
                      fontWeight: 600,
                      fill: '#f1f5f9',
                      pointerEvents: 'none',
                    }}
                  >
                    {hop.name}
                  </text>
                </motion.g>
              </Marker>
            ))}
          </AnimatePresence>

          {/* AWS Regions */}
          {regions.map((region) => (
            <Marker
              key={region.code}
              coordinates={[region.longitude, region.latitude]}
              className="region-marker"
              onMouseEnter={() => {
                setTooltipContent(`${region.name} (${region.code})\nStatus: ${region.status}\nLoad: ${(region.current_load * 100).toFixed(0)}%\nRequests: ${region.request_count}`);
                setShowTooltip(true);
              }}
              onMouseLeave={() => setShowTooltip(false)}
            >
              <g>
                {/* Outer glow */}
                <circle
                  r={10}
                  fill={getStatusColor(region.status)}
                  opacity={0.12}
                  className={region.status === 'healthy' ? 'pulse-ring' : ''}
                />
                {/* Main circle */}
                <circle
                  r={5}
                  fill={getStatusColor(region.status)}
                  stroke="rgba(255,255,255,0.3)"
                  strokeWidth={1.5}
                />
                {/* Region label */}
                <text
                  textAnchor="middle"
                  y={-14}
                  style={{
                    fontFamily: 'Inter, sans-serif',
                    fontSize: '6.5px',
                    fontWeight: 600,
                    fill: getStatusColor(region.status),
                    pointerEvents: 'none',
                  }}
                >
                  {region.city}
                </text>
              </g>
            </Marker>
          ))}

          {/* User location */}
          {userLocation && (
            <Marker coordinates={[userLocation.longitude, userLocation.latitude]}>
              <motion.g
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: 'spring', stiffness: 300 }}
              >
                <circle r={14} fill="#00d4ff" opacity={0.1} className="pulse-ring" />
                <circle r={7} fill="#00d4ff" opacity={0.3} />
                <circle r={4} fill="#00d4ff" stroke="white" strokeWidth={2} />
                <text
                  textAnchor="middle"
                  y={-18}
                  style={{
                    fontFamily: 'Inter, sans-serif',
                    fontSize: '8px',
                    fontWeight: 700,
                    fill: '#00d4ff',
                  }}
                >
                  📍 {userLocation.label || 'You'}
                </text>
              </motion.g>
            </Marker>
          )}
        </ZoomableGroup>
      </ComposableMap>

      {/* Latency overlay */}
      {simulationResult && (
        <motion.div
          className="map-latency-overlay"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <div className="overlay-stat">
            <span className="overlay-label">Latency</span>
            <span className="overlay-value" style={{ color: routeColor }}>
              {simulationResult.total_latency_ms?.toFixed(1)}ms
            </span>
          </div>
          <div className="overlay-stat">
            <span className="overlay-label">Region</span>
            <span className="overlay-value">{simulationResult.selected_region}</span>
          </div>
          <div className="overlay-stat">
            <span className="overlay-label">Cache</span>
            <span className="overlay-value" style={{ color: simulationResult.cache_hit ? '#00ff88' : '#ff3355' }}>
              {simulationResult.cache_hit ? 'HIT' : 'MISS'}
            </span>
          </div>
        </motion.div>
      )}
    </div>
  );
}
