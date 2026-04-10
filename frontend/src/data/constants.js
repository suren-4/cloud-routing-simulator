/**
 * Pre-defined user locations for the dropdown.
 */
export const USER_LOCATIONS = [
  { label: 'New York, USA', latitude: 40.7128, longitude: -74.0060 },
  { label: 'London, UK', latitude: 51.5074, longitude: -0.1278 },
  { label: 'Tokyo, Japan', latitude: 35.6762, longitude: 139.6503 },
  { label: 'Sydney, Australia', latitude: -33.8688, longitude: 151.2093 },
  { label: 'Mumbai, India', latitude: 19.0760, longitude: 72.8777 },
  { label: 'São Paulo, Brazil', latitude: -23.5505, longitude: -46.6333 },
  { label: 'Dubai, UAE', latitude: 25.2048, longitude: 55.2708 },
  { label: 'Singapore', latitude: 1.3521, longitude: 103.8198 },
  { label: 'Cape Town, South Africa', latitude: -33.9249, longitude: 18.4241 },
  { label: 'Frankfurt, Germany', latitude: 50.1109, longitude: 8.6821 },
  { label: 'Seoul, South Korea', latitude: 37.5665, longitude: 126.9780 },
  { label: 'Toronto, Canada', latitude: 43.6532, longitude: -79.3832 },
  { label: 'Paris, France', latitude: 48.8566, longitude: 2.3522 },
  { label: 'Los Angeles, USA', latitude: 34.0522, longitude: -118.2437 },
  { label: 'Beijing, China', latitude: 39.9042, longitude: 116.4074 },
];

export const ROUTING_MODES = [
  { value: 'default', label: 'Default (DNS)', color: '#ff3355', description: 'Standard DNS-based routing over public internet' },
  { value: 'global_accelerator', label: 'Global Accelerator', color: '#ff6b35', description: 'AWS Anycast routing via private backbone' },
  { value: 'cdn_only', label: 'CDN Only', color: '#a855f7', description: 'CloudFront edge caching without backbone optimization' },
  { value: 'optimized', label: 'Fully Optimized', color: '#00ff88', description: 'Global Accelerator + CloudFront CDN combined' },
];

export const HOP_COLORS = {
  user: '#00d4ff',
  edge: '#a855f7',
  accelerator: '#ff6b35',
  alb: '#fbbf24',
  server: '#00ff88',
};

export const MODE_COLORS = {
  default: '#ff3355',
  global_accelerator: '#ff6b35',
  cdn_only: '#a855f7',
  optimized: '#00ff88',
};
