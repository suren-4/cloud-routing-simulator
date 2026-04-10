"""Application configuration and constants."""

# --- Latency Model Constants ---
INTERNET_SPEED_FACTOR = 0.012  # ms per km over public internet
BACKBONE_SPEED_FACTOR = 0.005  # ms per km over AWS backbone (optimized)
BASE_PROCESSING_LATENCY = 8  # ms for server processing
EDGE_PROCESSING_LATENCY = 3  # ms at edge/CDN
JITTER_RANGE_INTERNET = (0, 18)  # random jitter range for public internet
JITTER_RANGE_BACKBONE = (0, 5)   # jitter on AWS backbone
HOP_PENALTY_INTERNET = 15  # additional ms for internet hops
HOP_PENALTY_BACKBONE = 3   # fewer hops on AWS backbone

# --- CDN (CloudFront) Constants ---
DEFAULT_CACHE_HIT_RATE = 0.78  # 78% cache hit rate
CACHE_HIT_LATENCY_RANGE = (2, 12)  # ms for CDN cache hit
CDN_TTL_SECONDS = 86400  # 24 hour TTL

# --- Cost Model Constants (per request in USD) ---
COST_COMPUTE_PER_REQUEST = 0.0000004  # ~Lambda pricing
COST_DATA_TRANSFER_PER_GB = 0.09
COST_CDN_PER_GB = 0.085
COST_GLOBAL_ACCELERATOR_PER_GB = 0.015
COST_ALB_PER_LCU_HOUR = 0.008
AVG_REQUEST_SIZE_KB = 50  # average request/response size
CDN_COST_SAVINGS_FACTOR = 0.60  # 60% savings on data transfer when cached

# --- Global Accelerator Constants ---
GA_LATENCY_REDUCTION_FACTOR = 0.45  # 45-60% latency reduction
GA_HEALTH_CHECK_INTERVAL = 10  # seconds

# --- Traffic Simulation ---
DEFAULT_REQUESTS_PER_SECOND = 100
SPIKE_MULTIPLIER = 5
AUTO_SCALE_THRESHOLD = 0.80  # 80% load triggers scaling
