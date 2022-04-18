# django_slots

Allows multiline strings to be captured and passed to template tags.

## Demo

1. Register a component
  
```python
# app/templatetags/component_tags.py
from django_slots import Library, Component

register = Library()


@register.block_component
class Details(Component):
    pass
```

2. Create a template

```html+django
{# app/templates/components/details.html #}
<details>
    <summary>{{ summary|default:slots.summary }}</summary>
    {{ slot }}
</details>
```

Usage:

```html+django
{% load component_tags %}
{% load slot_tags %}

{% details summary="the summary" %}
      the default slot
{% /details %}

{% details %}
    {% slot summary %}the <b>summary</b>{% /slot %}
    the default slot
{% /details %}
```

## Installation

```shell
pip install django-slots
```

```python
INSTALLED_APPS = [
    # ...
    
    'django_slots',
]
```

## Slots

Use `{% slot name %}{% /slot %}` to capture and name a slot. These slots will be available in the template in a dictionary called `slots`. eg `{{ slots.name }}`.

Any lines not surrounded by a slot tag will be available in the component template as `{{ slot }}`.

## Template

The default the template path is `components/<component_name>.html`.

Use `template_name` attribute or `get_template_name()` method to override.

## Change name

By default, the template tag name will be the Component class name converted to snake case. Use the `name` attribute to override.

eg:

```python
from django_slots import Component, Library

register = Library()


@register.inline_component
class Button(Component):
    name = 'btn'
```

```html+django
{% btn %}
```

## Change name format

By default, inline tags are named `"{name}/"` and block tags are named `"{name}", "/{name}"`. To change this format specify `inline_tag_name` and `block_tag_names` attributes.

eg:

```python
from django_slots import Component, Library

register = Library()


class AppComponent(Component):
    inline_tag_name = "{name}end"
    block_tag_names = "{name}", "end{name}"    

    
@register.component
class Button(AppComponent):
    pass
```

```html+django
{% buttonend %}

{% button %}{% endbutton %}
```

## Inline only template tag

Use `@register.inline_component` to only allow `{% inline/ %}` use.

## Block only template tag

Use `@register.block_component` to only allow `{% block %}{% /block %}` use.

## Validate arguments

Implement `def get_content_data(slots, **kwargs)` to validate arguments. 

eg:

```python
from django_slots import Component, Library

register = Library()


@register.component
class Button(Component):
    STYLE = ["primary", "secondary"]
    def get_context_data(self, slots, *, style: str):
        if style not in self.STYLE:
            raise self.validation_error(f"style {style!r} not in {self.STYLE!r}")
        return super().get_context_data(slots, style=style)
```

## Namespace components

Components can be namespaced which is useful for creating a third party app.

```python
from django_slots import Library, Component

register = Library()


class NHSUKComponent(Component):
    namespace = 'nhsuk'


@register.component
class Button(NHSUKComponent):
    pass
```

```html+django
{% nhsuk:button %}
  Save and continue
{% /nhsuk:button %}
```

See https://github.com/nwjlyons/nhsuk-components
