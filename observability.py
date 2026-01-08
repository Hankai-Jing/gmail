"""
Lightweight observability utilities: structured logging, metrics, and request IDs.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import logging
import threading
import time
import uuid
from collections import defaultdict
from typing import Dict, Optional, Tuple

try:
    from flask import g, request
except Exception:  # pragma: no cover - used outside Flask contexts
    g = None
    request = None


def _utc_now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def configure_logging() -> logging.Logger:
    logger = logging.getLogger("gmail")
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


LOGGER = configure_logging()


def hash_email(email_address: Optional[str]) -> Optional[str]:
    if not email_address:
        return None
    normalized = email_address.strip().lower().encode("utf-8")
    return hashlib.sha256(normalized).hexdigest()


def get_request_id() -> Optional[str]:
    if g is None:
        return None
    return getattr(g, "request_id", None)


def set_request_id() -> Optional[str]:
    if request is None or g is None:
        return None
    request_id = request.headers.get("X-Request-Id") or str(uuid.uuid4())
    g.request_id = request_id
    return request_id


def request_fields() -> Dict[str, Optional[str]]:
    if request is None:
        return {}
    return {
        "path": request.path,
        "method": request.method,
        "remote_addr": request.remote_addr,
    }


def log_event(logger: logging.Logger, event: str, **fields) -> None:
    payload = {
        "event": event,
        "ts": _utc_now_iso(),
        **fields,
    }
    logger.info(json.dumps(payload, sort_keys=True))


def _label_key(labels: Optional[Dict[str, str]]) -> Tuple[Tuple[str, str], ...]:
    if not labels:
        return tuple()
    return tuple(sorted(labels.items()))


class MetricsRegistry:
    """Simple in-memory metrics registry for counters and duration summaries."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._counters = defaultdict(int)
        self._durations = defaultdict(lambda: {"count": 0, "sum": 0.0, "max": 0.0})

    def inc_counter(self, name: str, labels: Optional[Dict[str, str]] = None, value: int = 1) -> None:
        key = (name, _label_key(labels))
        with self._lock:
            self._counters[key] += value

    def observe_duration(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        key = (name, _label_key(labels))
        with self._lock:
            entry = self._durations[key]
            entry["count"] += 1
            entry["sum"] += value
            if value > entry["max"]:
                entry["max"] = value

    def render_prometheus(self) -> str:
        lines = []
        with self._lock:
            for (name, labels), value in sorted(self._counters.items()):
                lines.append(f"# TYPE {name} counter")
                lines.append(f"{name}{_format_labels(labels)} {value}")
            for (name, labels), entry in sorted(self._durations.items()):
                lines.append(f"# TYPE {name} summary")
                lines.append(f"{name}_count{_format_labels(labels)} {entry['count']}")
                lines.append(f"{name}_sum{_format_labels(labels)} {entry['sum']}")
                lines.append(f"{name}_max{_format_labels(labels)} {entry['max']}")
        return "\n".join(lines) + "\n"


def _format_labels(labels: Tuple[Tuple[str, str], ...]) -> str:
    if not labels:
        return ""
    label_pairs = ",".join([f'{key}="{value}"' for key, value in labels])
    return "{" + label_pairs + "}"


METRICS = MetricsRegistry()


class Timer:
    """Context manager for duration observations."""

    def __init__(self, name: str, labels: Optional[Dict[str, str]] = None) -> None:
        self._name = name
        self._labels = labels
        self._start = 0.0

    def __enter__(self) -> "Timer":
        self._start = time.monotonic()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        duration = time.monotonic() - self._start
        METRICS.observe_duration(self._name, duration, self._labels)
