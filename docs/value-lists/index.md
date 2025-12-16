# Value Lists

These reusable lists define legal values for certain fields:

| List | Description |
|------|-------------|
{% for file in site.pages %}
{% if 'value-lists/' in file.url %}
| [{{ file.title }}]({{ file.url }}) | <!-- Placeholder --> |
{% endif %}
{% endfor %}
