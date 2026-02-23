"""Session-based rate limiter for SkillVector Engine."""

import time
from collections import defaultdict


class RateLimiter:
    """Simple in-memory rate limiter for Streamlit sessions.

    Tracks request timestamps per session and enforces a maximum
    number of requests within a sliding time window.
    """

    def __init__(self, max_requests: int = 10, window_seconds: int = 3600) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: dict[str, list[float]] = defaultdict(list)

    def check(self, session_id: str) -> tuple[bool, str]:
        """Check if a session is within rate limits.

        Args:
            session_id: Unique identifier for the session.

        Returns:
            Tuple of (is_allowed, error_message). error_message is empty if allowed.
        """
        now = time.time()
        window_start = now - self.window_seconds

        # Clean old entries outside the window
        self._requests[session_id] = [
            t for t in self._requests[session_id] if t > window_start
        ]

        if len(self._requests[session_id]) >= self.max_requests:
            remaining = int(self._requests[session_id][0] + self.window_seconds - now)
            minutes = max(1, remaining // 60)
            return False, (
                f"Rate limit reached ({self.max_requests} analyses per hour). "
                f"Please try again in ~{minutes} minute(s)."
            )

        self._requests[session_id].append(now)
        return True, ""

    def remaining(self, session_id: str) -> int:
        """Return how many requests are remaining for this session."""
        now = time.time()
        window_start = now - self.window_seconds
        recent = [t for t in self._requests.get(session_id, []) if t > window_start]
        return max(0, self.max_requests - len(recent))
