from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import random
import string

from faker import Faker


class SequenceIdGenerator:
    def __init__(self, prefix: str, width: int = 8) -> None:
        self.prefix = prefix
        self.width = width
        self.current = 0

    def next(self) -> str:
        self.current += 1
        return f"{self.prefix}{self.current:0{self.width}d}"


def isoformat_utc(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    value = value.astimezone(timezone.utc)
    return value.strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_isoformat(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def random_datetime_between(rng: random.Random, start: datetime, end: datetime, off_hours: bool = False) -> datetime:
    total_seconds = int((end - start).total_seconds())
    moment = start + timedelta(seconds=rng.randint(0, max(total_seconds, 1)))
    if off_hours:
        hour = rng.choice([0, 1, 2, 3, 4, 5, 22, 23])
    else:
        hour = rng.choices([8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], weights=[4, 6, 8, 8, 7, 7, 8, 8, 8, 7, 5, 4, 3])[0]
    minute = rng.randint(0, 59)
    second = rng.randint(0, 59)
    return moment.replace(hour=hour, minute=minute, second=second, microsecond=0)


def random_datetime_on_due_day(
    rng: random.Random,
    start: datetime,
    end: datetime,
    due_day: int,
    business_hour: bool = True,
) -> datetime:
    month_candidates = []
    cursor = datetime(start.year, start.month, 1, tzinfo=start.tzinfo)
    while cursor <= end:
        month_candidates.append(cursor)
        if cursor.month == 12:
            cursor = datetime(cursor.year + 1, 1, 1, tzinfo=cursor.tzinfo)
        else:
            cursor = datetime(cursor.year, cursor.month + 1, 1, tzinfo=cursor.tzinfo)
    chosen_month = rng.choice(month_candidates)
    day = min(due_day, 28)
    chosen = chosen_month.replace(day=day)
    if chosen < start:
        chosen = start + timedelta(days=rng.randint(0, 2))
    if chosen > end:
        chosen = end - timedelta(days=rng.randint(0, 2))
    hour = rng.randint(8, 20) if business_hour else rng.choice([0, 1, 2, 22, 23])
    return chosen.replace(hour=hour, minute=rng.randint(0, 59), second=rng.randint(0, 59), microsecond=0)


def bounded_normal_amount(rng: random.Random, center: float, spread: float, floor: float = 1.0) -> float:
    value = max(floor, rng.gauss(center, spread))
    return round(value, 2)


def random_session_id(rng: random.Random, fake: Faker | None = None, prefix: str = "SES") -> str:
    if fake is not None:
        token = fake.bothify(text="??##-??##-########").upper()
        return f"{prefix}_{token}"
    token = "".join(rng.choice(string.ascii_uppercase + string.digits) for _ in range(12))
    return f"{prefix}_{token}"


def ensure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def weighted_pick(rng: random.Random, items: list[str], weights: list[float]) -> str:
    return rng.choices(items, weights=weights, k=1)[0]


def as_bool_string(value: bool) -> str:
    return "true" if value else "false"
