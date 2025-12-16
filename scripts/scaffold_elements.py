import yaml
from pathlib import Path
import re

SOURCE_FILE = Path("data/sources/hmis_api_ld_0.5.yaml")
OUTPUT_DIR = Path("data/elements/draft")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

with SOURCE_FILE.open() as f:
    spec = yaml.safe_load(f)

schemas = spec.get("components", {}).get("schemas", {})

def safe_filename(text):
    return re.sub(r"[^a-zA-Z0-9._-]", "_", text)

# Load existing draft elements, indexed by name
existing_elements = {}

for path in OUTPUT_DIR.glob("*.yaml"):
    data = yaml.safe_load(path.read_text())
    if not data:
        continue
    name = data.get("name")
    if name:
        existing_elements[name] = {
            "path": path,
            "data": data
        }

created = 0
amended = 0

for schema_name, schema in schemas.items():
    properties = schema.get("properties")
    if not properties:
        continue

    for field_name, field in properties.items():
        # Check if this element already exists
        if field_name in existing_elements:
            entry = existing_elements[field_name]
            element = entry["data"]

            sources = element.setdefault("sources", [])

            new_source = {
                "openapi_schema": schema_name,
                "openapi_field": field_name
            }

            if new_source not in sources:
                sources.append(new_source)
                entry["path"].write_text(
                    yaml.dump(
                        element,
                        sort_keys=False,
                        allow_unicode=True
                    )
                )
                amended += 1

            continue

        # Otherwise create a new draft element
        filename = safe_filename(field_name) + ".yaml"
        out_path = OUTPUT_DIR / filename

        # Extremely defensive: never overwrite
        if out_path.exists():
            continue

        element = {
            "status": "draft",
            "hmis_id": None,
            "name": field_name,
            "description": field.get("description", ""),
            "type": field.get("type"),
            "sources": [
                {
                    "openapi_schema": schema_name,
                    "openapi_field": field_name
                }
            ],
            "notes": {
                "curation": ""
            }
        }

        out_path.write_text(
            yaml.dump(
                element,
                sort_keys=False,
                allow_unicode=True
            )
        )

        # Register it so later schemas can match it
        existing_elements[field_name] = {
            "path": out_path,
            "data": element
        }

        created += 1

print(f"Created {created} new draft elements.")
print(f"Amended {amended} existing draft elements.")
