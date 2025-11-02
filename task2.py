import random
import time
from typing import Dict
from collections import deque


class SlidingWindowRateLimiter:
    def __init__(self, window_size: int = 10, max_requests: int = 1):
        self.window_size = window_size
        self.max_requests = max_requests
        self.history: Dict[str, deque] = {}

    def _cleanup_window(self, user_id: str, current_time: float) -> None:
        dq = self.history.get(user_id)
        if dq is None:
            return
        threshold = current_time - self.window_size
        while dq and dq[0] <= threshold:
            dq.popleft()
        if not dq:
            self.history.pop(user_id, None)

    def can_send_message(self, user_id: str) -> bool:
        now = time.time()
        dq = self.history.get(user_id)
        if dq is None:
            return True
        self._cleanup_window(user_id, now)
        dq = self.history.get(user_id)
        if dq is None:
            return True
        return len(dq) < self.max_requests

    def record_message(self, user_id: str) -> bool:
        now = time.time()
        self._cleanup_window(user_id, now)
        if not self.can_send_message(user_id):
            return False
        dq = self.history.setdefault(user_id, deque())
        dq.append(now)
        return True

    def time_until_next_allowed(self, user_id: str) -> float:
        now = time.time()
        dq = self.history.get(user_id)
        if dq is None or len(dq) < self.max_requests:
            return 0.0
        self._cleanup_window(user_id, now)
        dq = self.history.get(user_id)
        if dq is None or len(dq) < self.max_requests:
            return 0.0
        oldest = dq[0]
        wait = (oldest + self.window_size) - now
        return max(0.0, wait)


def test_rate_limiter():
    limiter = SlidingWindowRateLimiter(window_size=10, max_requests=1)

    print("\n=== Симуляція потоку повідомлень ===")
    for message_id in range(1, 11):
        user_id = message_id % 5 + 1
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))
        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}")
        time.sleep(random.uniform(0.1, 1.0))

    print("\nОчікуємо 4 секунди...")
    time.sleep(4)

    print("\n=== Нова серія повідомлень після очікування ===")
    for message_id in range(11, 21):
        user_id = message_id % 5 + 1
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))
        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}")
        time.sleep(random.uniform(0.1, 1.0))


if __name__ == "__main__":
    test_rate_limiter()