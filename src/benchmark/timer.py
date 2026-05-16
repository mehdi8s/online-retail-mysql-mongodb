import time
from dataclasses import dataclass


@dataclass
class TimedResult:
    test_name: str
    database: str
    operations: int
    duration_sec: float

    @property
    def throughput(self) -> float:
        if self.duration_sec <= 0:
            return 0.0
        return self.operations / self.duration_sec


def measure(test_name: str, database: str, operations: int, fn):
    start = time.perf_counter()
    fn()
    duration = time.perf_counter() - start
    return TimedResult(test_name, database, operations, duration)
