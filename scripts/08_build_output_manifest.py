from pathlib import Path
import hashlib
import pandas as pd

root=Path(__file__).resolve().parents[1]
rows=[]
for base in (root/'figures/main',root/'figures/supplementary'):
    for p in sorted(base.glob('*')):
        if p.is_file():
            h=hashlib.sha256(p.read_bytes()).hexdigest()
            rows.append({'file':str(p.relative_to(root)),'format':p.suffix.lstrip('.'),
                'bytes':p.stat().st_size,'sha256':h})
pd.DataFrame(rows).to_csv(root/'results/tables/generated_figure_files.tsv',sep='\t',index=False)
print(f"Manifested {len(rows)} figure files")
