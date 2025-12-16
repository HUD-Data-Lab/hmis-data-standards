import yaml
from pathlib import Path
import re

SOURCE_FILE = Path("data/sources/hmis_api_ld_0.5.yaml")
ELEMENT_DIR = Path("data/elements/draft")
VALUE_LIST_DIR = Path("data/value_lists/draft")

ELEMENT_DIR.mkdir(parents=True, exist_ok=True)
VALUE_LIST_DIR.mkdir(parents=True, exist_ok=True)

with SOURCE_FILE.open() as f:
    spec = yaml.safe_load(f)

schemas = spec.get("components", {}).get("schemas", {})
value_lists = {}

def safe_filename(text):
    return re.sub(r"[^a-zA-Z0-9._-]", "_", text)

value_lists = {}

for schema_name, schema in schemas.items():
    one_of = schema.get("oneOf")
    if not one_of:
        continue

    values = []
    for entry in one_of:
        if "const" in entry:
            values.append({
                "value": entry.get("const"),
                "label": entry.get("title"),
                "description": entry.get("description")
            })

    if not values:
        continue

    value_list_id = schema_name.replace("_list", "")

    value_lists[schema_name] = value_list_id

    out_path = VALUE_LIST_DIR / f"{value_list_id}.yaml"
    if out_path.exists():
        continue

    value_list = {
        "status": "draft",
        "id": value_list_id,
        "description": schema.get("description", ""),
        "type": schema.get("type"),
        "values": values,
        "source": {
            "openapi_schema": schema_name
        },
        "notes": {
            "curation": ""
        }
    }

    out_path.write_text(
        yaml.dump(value_list, sort_keys=False, allow_unicode=True)
    )

# Load existing draft elements, indexed by name
existing_elements = {}

for path in ELEMENT_DIR.glob("*.yaml"):
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
        value_list_ref = None

        one_of = field.get("oneOf")
        if one_of:
            for option in one_of:
                ref = option.get("$ref")
                if ref and ref.startswith("#/components/schemas/"):
                    ref_name = ref.split("/")[-1]
                    if ref_name in value_lists:
                        value_list_ref = value_lists[ref_name]

        
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
        out_path = ELEMENT_DIR / filename

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

        if value_list_ref:
            element["value_list"] = value_list_ref

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
