from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_required_scaffold_exists():
    required = [
        "pixi.toml", "config/analysis.yml", "config/paths.example.yml",
        "R", "python", "scripts", "metadata", "data",
    ]
    for relative in required:
        assert (ROOT / relative).exists(), relative


def test_reviewer_parameter_grid():
    config = yaml.safe_load((ROOT / "config/analysis.yml").read_text())
    sensitivity = config["tsne"]["sensitivity"]
    assert sensitivity["initial_dims"] == [10, 20, 30, 50, 72]
    assert sensitivity["perplexities"] == [5, 10, 15, 20]
    assert len(sensitivity["seeds"]) >= 5
