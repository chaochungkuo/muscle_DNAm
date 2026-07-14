from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / "figures/main"
target = ROOT / "figures/web"
target.mkdir(parents=True, exist_ok=True)

for path in sorted(source.glob("*.tiff")):
    image = Image.open(path).convert("RGB")
    image.thumbnail((2200, 2200), Image.Resampling.LANCZOS)
    output = target / f"{path.stem}.png"
    image.save(output, format="PNG", optimize=True)
    print(f"{path.name} -> {output.name} ({image.width}x{image.height})")
