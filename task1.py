import time
import random
from collections import OrderedDict
from typing import List, Tuple


class LRUCache:
    def __init__(self, capacity: int = 1000):
        self.capacity = capacity
        self.store: "OrderedDict[Tuple[int, int], int]" = OrderedDict()

    def get(self, key: Tuple[int, int]) -> int:
        if key not in self.store:
            return -1
        self.store.move_to_end(key)
        return self.store[key]

    def put(self, key: Tuple[int, int], value: int) -> None:
        if key in self.store:
            self.store.move_to_end(key)
            self.store[key] = value
            return
        self.store[key] = value
        if len(self.store) > self.capacity:
            self.store.popitem(last=False)

    def keys_snapshot(self):
        return list(self.store.keys())

    def invalidate_key(self, key: Tuple[int, int]) -> None:
        if key in self.store:
            del self.store[key]


def make_queries(n: int, q: int, hot_pool: int = 30, p_hot: float = 0.95, p_update: float = 0.03):
    hot = [(random.randint(0, n // 2), random.randint(n // 2, n - 1)) for _ in range(hot_pool)]
    queries = []
    for _ in range(q):
        if random.random() < p_update:
            idx = random.randint(0, n - 1)
            val = random.randint(1, 100)
            queries.append(("Update", idx, val))
        else:
            if random.random() < p_hot:
                left, right = random.choice(hot)
            else:
                left = random.randint(0, n - 1)
                right = random.randint(left, n - 1)
            queries.append(("Range", left, right))
    return queries


def range_sum_no_cache(array: List[int], left: int, right: int) -> int:
    return sum(array[left:right + 1])


def update_no_cache(array: List[int], index: int, value: int) -> None:
    array[index] = value


def range_sum_with_cache(array: List[int], left: int, right: int, cache: LRUCache) -> int:
    key = (left, right)
    cached = cache.get(key)
    if cached != -1:
        return cached
    s = sum(array[left:right + 1])
    cache.put(key, s)
    return s


def update_with_cache(array: List[int], index: int, value: int, cache: LRUCache) -> None:
    array[index] = value
    for key in cache.keys_snapshot():
        L, R = key
        if L <= index <= R:
            cache.invalidate_key(key)


def run_benchmark(n: int = 100_000, q: int = 50_000, capacity: int = 1000, seed: int = 42):
    random.seed(seed)
    array = [random.randint(1, 100) for _ in range(n)]
    queries = make_queries(n, q)

    arr_no_cache = array[:]
    t0 = time.perf_counter()
    for op in queries:
        if op[0] == "Range":
            _, L, R = op
            range_sum_no_cache(arr_no_cache, L, R)
        else:
            _, idx, val = op
            update_no_cache(arr_no_cache, idx, val)
    no_cache_time = time.perf_counter() - t0

    arr_cache = array[:]
    cache = LRUCache(capacity=capacity)
    t0 = time.perf_counter()
    for op in queries:
        if op[0] == "Range":
            _, L, R = op
            range_sum_with_cache(arr_cache, L, R, cache)
        else:
            _, idx, val = op
            update_with_cache(arr_cache, idx, val, cache)
    with_cache_time = time.perf_counter() - t0

    speedup = no_cache_time / with_cache_time if with_cache_time > 0 else float("inf")
    
    print(f"Без кешу : {no_cache_time:6.2f} c")
    print(f"LRU-кеш  : {with_cache_time:6.2f} c  (прискорення ×{speedup:.1f})")


if __name__ == "__main__":
    run_benchmark()