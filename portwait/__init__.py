"""Wait until a TCP host and port accept connections."""

from __future__ import annotations

import math
import socket
import time

__all__ = ["wait_for_port"]


def wait_for_port(host: str, port: int, timeout: float = 30.0, interval: float = 0.5) -> bool:
    """Return whether a TCP connection can be made before ``timeout`` expires.

    One connection attempt is always made, including when timeout is zero.
    DNS resolution time is controlled by the operating system and may extend
    beyond the requested timeout.
    """
    if not isinstance(host, str) or not host.strip():
        raise ValueError("host must be a non-empty string")
    if isinstance(port, bool) or not isinstance(port, int) or not 1 <= port <= 65535:
        raise ValueError("port must be an integer from 1 to 65535")
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not math.isfinite(timeout) or timeout < 0:
        raise ValueError("timeout must be a finite non-negative number")
    if isinstance(interval, bool) or not isinstance(interval, (int, float)) or not math.isfinite(interval) or interval <= 0:
        raise ValueError("interval must be a finite positive number")

    deadline = time.monotonic() + timeout
    while True:
        remaining = deadline - time.monotonic()
        connect_timeout = min(1.0, max(0.05, remaining))
        try:
            with socket.create_connection((host, port), timeout=connect_timeout):
                return True
        except OSError:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return False
            time.sleep(min(interval, remaining))
