from __future__ import annotations

from dataclasses import dataclass, field
from time import perf_counter


@dataclass
class ProgressReporter:
    enabled: bool = True
    _last_counts: dict[str, int] = field(default_factory=dict)

    def info(self, message: str) -> None:
        if not self.enabled:
            return
        print(f"[progress] {message}", flush=True)

    def stage_start(self, label: str) -> float:
        started_at = perf_counter()
        self.info(f"{label}...")
        return started_at

    def stage_end(self, label: str, started_at: float, detail: str = "") -> None:
        elapsed = perf_counter() - started_at
        suffix = f" | {detail}" if detail else ""
        self.info(f"{label} complete in {elapsed:.2f}s{suffix}")

    def tick(self, key: str, current: int, total: int, label: str, every: int | None = None) -> None:
        if not self.enabled or total <= 0:
            return
        interval = every if every is not None else _default_interval(total)
        last = self._last_counts.get(key, 0)
        should_log = current == total or current == 1 or current - last >= interval
        if not should_log:
            return
        self._last_counts[key] = current
        percent = (current / total) * 100
        self.info(f"{label}: {current:,}/{total:,} ({percent:.1f}%)")


def _default_interval(total: int) -> int:
    if total <= 250:
        return 25
    if total <= 2_500:
        return 250
    if total <= 25_000:
        return 2_500
    if total <= 100_000:
        return 10_000
    return 20_000
