# django_slots

django_slots = inclusion tag + blocks

```shell
pip install django-slots
```

```python
INSTALLED_APPS = [
    # ...
    
    'django_slots',
]
```

### Examples

- [Button example](#button-example)
- [Details example](#details-example)
- [Form example](#form-example)

## Button example

```python
# app/templatetags/component_tags.py
from django_slots import Library, Component

register = Library()


@register.component
class Button(Component):
    pass
```

```html+django
{# app/templates/components/button.html #}
<button>{{ slot }}</button>
```

### Usage

```html+django
{% load component_tags %}
{% button %}
    <div>Save</div>
    <small>and add another</small>
{% /button %}
```

## Details example

```python
# app/templatetags/component_tags.py
from django_slots import Library, Component

register = Library()


@register.block_component
class Details(Component):
    pass
```

```html+django
{# app/templates/components/details.html #}
<details>
  <summary>{{ slots.summary }}</summary>
  {{ slot }}
</details>
```

### Usage

```html+django
{% load component_tags %}
{% load slot_tags %}

{% details %}
    {% slot summary %}the summary{% /slot %}
    the default slot
{% /details %}
```


## Form example

### Python

```python
# app/templatetags/component_tags.py
from django.forms.utils import ErrorList
from django.forms import Form

from django_slots.components import Library, Component, DEFAULT_SLOT_NAME


register = Library()


@register.component
class Button(Component):
    STYLE_CHOICES = ['green', 'red']
    TYPE_CHOICES = ['submit', 'reset', '']

    def get_context_data(
        self, 
        filled_slots: list[str], 
        *,
        type: str = 'submit', 
        name: str ='', 
        value: str = 'Submit', 
        style: str = 'green'
    ):
        if value and DEFAULT_SLOT_NAME in filled_slots:
            raise self.validation_error("use value keyword argument or slot tag.")

        if type not in self.TYPE_CHOICES:
            raise self.validation_error(f"type='{type}' must be one of {self.TYPE_CHOICES!r}")
        
        if style not in self.STYLE_CHOICES:
            raise self.validation_error(f"style='{style}' must be one of {self.STYLE_CHOICES!r}")

        return {
            'type': type,
            'name': name,
            'value': value,
            'style': style,
        }
        

@register.inline_component
class FormErrors(Component):
    def get_context_data(self, filled_slots: list[str], *, errors: ErrorList):
        return {
            'errors': errors,
        }


@register.inline_component
class FormField(Component):
    def get_context_data(self, filled_slots: list[str], *, field):
        return {
            'field': field,
        }


@register.component
class Form(Component):
    def get_context_data(
        self, 
        filled_slots: list[str],
        *,
        form: Form, 
        action: str = '', 
        method: str = 'post', 
        csrf_token: str = '', 
        csrf_exempt: bool = False
    ):
        if csrf_exempt is False and method == 'post' and csrf_token == '':
            raise self.validation_error(
                "csrf_token keyword argument is required when method is post and csrf_exempt is false"
            )
        
        return {
            'form': form,
            'action': action,
            'method': method,
            'csrf_token': csrf_token,
        }
```

### HTML

```html+django
{# app/templates/components/button.html #}
{% load slot_tags %}
<button {% if type %} type="{{ type }}"{% endif %}{% if name %} name="{{ name }}"{% endif %}
    class="btn{% if style == "green" %} btn--green{% elif style == "red" %}btn--red{% endif %}">
    {% if value %}{{ value }}{% else %}{{ slot }}{% endif %}
</button>
```

```html+django
{# app/templates/components/form_errors.html #}
{% if errors %}
<div>
    {% for error in errors %}
    <div>{{ error }}</div>
    {% endfor %}
</div>
{% endif %}
```

```html+django
{# app/templates/components/form_field.html #}
{% load component_tags %}
<div class="field">
    {% if field.label %}
        <label for="{{ field.id_for_label }}">{{ field.label }}</label>
    {% endif %}
    {% form_errors/ errors=field.errors %}
    <div>
        {{ field }}
    </div>
    {% if field.help_text %}
        <small>{{ field.help_text }}</small>
    {% endif %}
</div>

```

```html+django
{# app/templates/components/form.html #}
{% load component_tags %}
<form action="{{ action }}" method="{{ method }}"{% if form.is_multipart %} enctype="multipart/form-data"{% endif %}>
    {% if csrf_token %}<input type="hidden" name="csrfmiddlewaretoken" value="{{ csrf_token }}">{% endif %}
    {% for field in form.hidden_fields %}{{ field }}{% endfor %}
    
    {{ slots.hidden_fields }}
        
    {% form_errors/ errors=form.non_field_errors %}
    
    {% if slots.visible_fields %}
        {{ slots.visible_fields }}
    {% else %}
        {% for field in form.visible_fields %}
            {% form_field/ field=field %}
        {% endfor %}
    {% endif %}
    
    {% if slots.buttons %}
        {{ slots.buttons }}
    {% else %}
        {% button/ value=_("Submit") %}
    {% endif %}
</form>
```

### Usage

```html+django
{% load slot_tags %}
{% load component_tags %}


<!-- inline use -->
{% form/ form=form csrf_token=csrf_token %}

<!-- block use -->
{% form/ form=form csrf_token=csrf_token %}

    <!-- override visible_fields slot in base template -->
    {% slot visible_fields %}
        {% form_field/ field=form.title %}
    {% /slot %}

    <!-- override buttons slot in base template -->
    {% slot buttons %}
        {% button %}Delete{% /button %}
    {% /slot %}
{% /form %}
```
