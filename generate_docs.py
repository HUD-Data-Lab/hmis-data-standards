import yaml
from pathlib import Path

DATA_DIR = Path("data/elements")
DOCS_DIR = Path("docs/elements")
DOCS_DIR.mkdir(parents=True, exist_ok=True)

for path in DATA_DIR.glob("*.yaml"):
    element = yaml.safe_load(path.read_text())

    md = f"""# {element['id']} — {element['name']}

## Description
{element.get('description', '')}

## Collection Stages
{", ".join(element.get('collection_stages', []))}

## Fields
"""

    for f in element.get("fields", []):
        md += f"- **{f['name']}** ({f['type']})\n"

    md += f"""

## Reporting
{", ".join(element.get("appears_in", []))}

## Manual Notes
{element.get("notes", {}).get("manual", "")}
"""

    (DOCS_DIR / f"{element['id']}.md").write_text(md)
