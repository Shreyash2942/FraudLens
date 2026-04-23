from __future__ import annotations

from faker import Faker


def build_faker(seed: int) -> Faker:
    fake = Faker("en_US")
    fake.seed_instance(seed)
    return fake
