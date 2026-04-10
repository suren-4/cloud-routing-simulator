/**
 * API service layer for communicating with the backend.
 */

const API_BASE = '/api';

async function fetchJSON(url, options = {}) {
  const res = await fetch(`${API_BASE}${url}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) throw new Error(`API Error: ${res.status}`);
  return res.json();
}

/* ---- Simulation ---- */
export async function simulateRequest(userLocation, routingMode, cdnEnabled, contentType = 'dynamic') {
  return fetchJSON('/simulate', {
    method: 'POST',
    body: JSON.stringify({
      user_location: userLocation,
      routing_mode: routingMode,
      cdn_enabled: cdnEnabled,
      content_type: contentType,
      num_requests: 1,
    }),
  });
}

export async function batchSimulate(userLocation, contentType = 'dynamic') {
  return fetchJSON('/simulate/batch', {
    method: 'POST',
    body: JSON.stringify({
      user_location: userLocation,
      routing_mode: 'default',
      cdn_enabled: false,
      content_type: contentType,
      num_requests: 1,
    }),
  });
}

export async function simulateTrafficSpike(userLocation, spikeMultiplier = 5) {
  return fetchJSON('/simulate/traffic-spike', {
    method: 'POST',
    body: JSON.stringify({
      user_location: userLocation,
      spike_multiplier: spikeMultiplier,
      duration_seconds: 30,
    }),
  });
}

/* ---- Regions ---- */
export async function getRegions() {
  return fetchJSON('/regions');
}

export async function toggleRegion(code) {
  return fetchJSON(`/regions/${code}/toggle`, { method: 'POST' });
}

export async function degradeRegion(code, factor = 2.0) {
  return fetchJSON(`/regions/${code}/degrade?factor=${factor}`, { method: 'POST' });
}

export async function recoverRegion(code) {
  return fetchJSON(`/regions/${code}/recover`, { method: 'POST' });
}

/* ---- Metrics ---- */
export async function getMetrics() {
  return fetchJSON('/metrics');
}

export async function getMetricsHistory() {
  return fetchJSON('/metrics/history');
}

/* ---- Recommendations ---- */
export async function getRecommendation(latitude, longitude, trafficRps = 100) {
  return fetchJSON('/recommend', {
    method: 'POST',
    body: JSON.stringify({ latitude, longitude, traffic_rps: trafficRps }),
  });
}

export async function getSavingsPrediction(rps = 100) {
  return fetchJSON(`/recommend/savings?rps=${rps}`);
}
