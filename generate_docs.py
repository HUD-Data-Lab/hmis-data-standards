try:
    import mkdocs_gen_files
    USE_MKDOCS = True
except ImportError:
    USE_MKDOCS = False

import yaml
from pathlib import Path
from contextlib import contextmanager
from pathlib import Path

@contextmanager
def open_doc(path):
    if USE_MKDOCS:
        with mkdocs_gen_files.open(path, "w") as f:
            yield f
    else:
        out = Path("docs") / path
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", encoding="utf-8") as f:
            yield f

ELEMENTS_DIR = Path("data/elements/draft")   # change to canonical later
DOCS_DIR = Path("docs/elements")

DOCS_DIR.mkdir(parents=True, exist_ok=True)

def md_escape(value):
    return value if value is not None else ""

count = 0

for path in sorted(ELEMENTS_DIR.glob("*.yaml")):
    element = yaml.safe_load(path.read_text())
    if not element:
        continue

    name = element.get("name", "Unnamed Element")
    hmis_id = element.get("hmis_id")
    description = element.get("description", "")
    element_type = element.get("type")
    status = element.get("status", "unknown")
    sources = element.get("sources", [])
    notes = element.get("notes", {})

    title = f"{hmis_id} — {name}" if hmis_id else name

    md = f"""# {title}

**Status:** {status}

"""

    if description:
        md += f"""## Description
{description}

"""

    if element_type:
        md += f"""## Data Type
`{element_type}`

"""

    if sources:
        md += "## Source (OpenAPI Provenance)\n"
        for s in sources:
            md += (
                f"- `{s.get('openapi_schema')}`."
                f"`{s.get('openapi_field')}`\n"
            )
        md += "\n"

    if notes:
        md += "## Notes\n"
        for key, value in notes.items():
            if value:
                md += f"### {key.capitalize()}\n{value}\n\n"

    # out_path = DOCS_DIR / f"{path.stem}.md"
    # out_path.write_text(md)

    with open_doc(f"elements/{path.stem}.md") as f:
        f.write(md)

    count += 1

print(f"Generated {count} element documentation pages.")
