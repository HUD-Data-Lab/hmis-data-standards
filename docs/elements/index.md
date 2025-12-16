# Data Elements

The following data elements are defined in the HMIS standard:

| Element | Description |
|----------|-------------|
{% for file in site.pages %}
{% if 'elements/' in file.url %}
| [{{ file.title }}]({{ file.url }}) | <!-- Placeholder; you can script descriptions later --> |
{% endif %}
{% endfor %}
