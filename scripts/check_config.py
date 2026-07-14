#!/usr/bin/env python3
"""Validate committed configuration without requiring private data."""

from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    analysis = yaml.safe_load((ROOT / "config/analysis.yml").read_text())
    paths = yaml.safe_load((ROOT / "config/paths.example.yml").read_text())
    assert analysis["project"]["sample_count"] == 73
    assert analysis["project"]["patient_count"] == 72
    assert analysis["project"]["post_qc_probe_count"] == 771381
    assert analysis["tsne"]["baseline"]["initial_dims"] == 50
    assert "bias_metadata" in paths
    print("Configuration schema check passed.")


if __name__ == "__main__":
    main()
