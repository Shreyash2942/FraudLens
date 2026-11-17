from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable

import yaml


DEFAULT_MAPPING = Path(__file__).with_name("fraudlens_metrics_mapping.yaml")


def load_mapping(path: Path = DEFAULT_MAPPING) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def iter_events(paths: Iterable[Path]) -> Iterable[dict[str, Any]]:
    for path in paths:
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                yield json.loads(line)


def _label_value(value: Any) -> str:
    return str(value).replace("\\", "\\\\").replace('"', '\\"')


def _event_labels(event: dict[str, Any], mapping: dict[str, Any]) -> dict[str, str]:
    label_config = mapping["labels"]
    labels = dict(label_config.get("defaults", {}))
    allowed_labels = set(label_config["allowed"])
    for label in sorted(allowed_labels):
        if label in event and event[label] not in (None, ""):
            labels[label] = str(event[label])
    return labels


def _format_labels(labels: dict[str, str]) -> str:
    if not labels:
        return ""
    rendered = ",".join(f'{key}="{_label_value(labels[key])}"' for key in sorted(labels))
    return "{" + rendered + "}"


def render_events(events: Iterable[dict[str, Any]], mapping: dict[str, Any]) -> str:
    metric_mapping = mapping["metrics"]
    self_metrics = mapping["self_metrics"]
    parsed_events = 0
    skipped_events = 0
    lines: list[str] = []
    emitted_headers: set[str] = set()

    for event in events:
        metric_name = event.get("metric_name")
        config = metric_mapping.get(metric_name)
        if config is None:
            skipped_events += 1
            continue

        prometheus_name = config["prometheus_name"]
        if prometheus_name not in emitted_headers:
            lines.append(f"# HELP {prometheus_name} {config['help']}")
            lines.append(f"# TYPE {prometheus_name} {config['type']}")
            emitted_headers.add(prometheus_name)

        labels = _event_labels(event, mapping)
        lines.append(f"{prometheus_name}{_format_labels(labels)} {event['metric_value']}")
        parsed_events += 1

    for key, value in [
        ("parsed_events_total", parsed_events),
        ("skipped_events_total", skipped_events),
    ]:
        config = self_metrics[key]
        prometheus_name = config["prometheus_name"]
        lines.append(f"# HELP {prometheus_name} {config['help']}")
        lines.append(f"# TYPE {prometheus_name} {config['type']}")
        lines.append(f"{prometheus_name} {value}")

    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render FraudLens metric JSONL as Prometheus exposition text.")
    parser.add_argument("events", nargs="+", type=Path, help="Metric event JSONL files.")
    parser.add_argument("--mapping", type=Path, default=DEFAULT_MAPPING, help="Metric mapping YAML file.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    mapping = load_mapping(args.mapping)
    print(render_events(iter_events(args.events), mapping), end="")


if __name__ == "__main__":
    main()

