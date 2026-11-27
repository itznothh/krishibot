"""Small process-local sliding-window limiter for provider-backed Flask routes."""
from collections import OrderedDict, deque
from functools import wraps
import hashlib
import ipaddress
import os
import threading
import time

from flask import jsonify, request


class SlidingWindowLimiter:
    """Thread-safe limiter; state is intentionally local to one app process."""

    def __init__(self, max_buckets=50_000, clock=time.monotonic):
        self._buckets = OrderedDict()
        self._lock = threading.Lock()
        self._max_buckets = max_buckets
        self._clock = clock

    def clear(self):
        with self._lock:
            self._buckets.clear()

    def check(self, key, limit, window_seconds=60):
        now = self._clock()
        cutoff = now - window_seconds
        with self._lock:
            events = self._buckets.pop(key, deque())
            while events and events[0] <= cutoff:
                events.popleft()
            if len(events) >= limit:
                retry_after = max(1, int(events[0] + window_seconds - now + 0.999))
                self._buckets[key] = events
                return retry_after
            events.append(now)
            self._buckets[key] = events
            while len(self._buckets) > self._max_buckets:
                self._buckets.popitem(last=False)
        return None


limiter = SlidingWindowLimiter()

# Environment variable -> safe default requests per client per rolling minute.
LIMITS = {
    "chat": ("RATE_LIMIT_CHAT_PER_MINUTE", 20),
    "image": ("RATE_LIMIT_IMAGE_PER_MINUTE", 5),
    "schemes": ("RATE_LIMIT_SCHEMES_PER_MINUTE", 5),
    "weather": ("RATE_LIMIT_WEATHER_PER_MINUTE", 15),
    "mandi_markets": ("RATE_LIMIT_MANDI_MARKETS_PER_MINUTE", 20),
    "mandi_prices": ("RATE_LIMIT_MANDI_PRICES_PER_MINUTE", 30),
    "whatsapp": ("RATE_LIMIT_WHATSAPP_PER_MINUTE", 15),
}


def _positive_env_int(name, default):
    try:
        return max(1, min(100_000, int(os.environ.get(name, default))))
    except (TypeError, ValueError):
        return default


def _trusted_proxy_hops():
    try:
        return max(0, min(20, int(os.environ.get("RATE_LIMIT_TRUSTED_PROXY_HOPS", "0"))))
    except (TypeError, ValueError):
        return 0


def _client_address():
    """Use the socket peer unless an explicit trusted proxy hop count is set."""
    peer = request.remote_addr or "unknown"
    hops = _trusted_proxy_hops()
    if not hops:
        return peer

    forwarded = request.headers.get("X-Forwarded-For", "")
    try:
        chain = [str(ipaddress.ip_address(part.strip())) for part in forwarded.split(",")]
        # A hop count is an explicit deployment trust setting. Select the
        # address immediately before the configured trusted proxy hops.
        index = len(chain) - hops
        if index >= 0:
            return chain[index]
    except ValueError:
        pass
    return peer


def enforce_limit(endpoint, identity=None):
    env_name, default = LIMITS[endpoint]
    address = _client_address()
    client_id = identity if isinstance(identity, str) and identity else address
    client_fingerprint = hashlib.sha256(client_id.encode("utf-8", "replace")).hexdigest()
    retry_after = limiter.check(
        (endpoint, client_fingerprint),
        _positive_env_int(env_name, default),
    )
    if retry_after is None:
        return None
    response = jsonify({
        "status": "error",
        "error": "rate_limit_exceeded",
        "message": "Too many requests. Please wait before trying again.",
    })
    response.status_code = 429
    response.headers["Retry-After"] = str(retry_after)
    return response


def rate_limit(endpoint):
    """Apply an endpoint-specific request limit before entering route logic."""
    def decorate(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            limited = enforce_limit(endpoint)
            return limited if limited is not None else view(*args, **kwargs)
        return wrapped
    return decorate
