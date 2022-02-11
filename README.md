# django_template_component

django_template_component = inclusion tag + blocks

### Examples

- [Button example](#button-example)
- [Form example](#form-example)

## Button example

`app/templatetags/component_tags.py`

```python
from django_template_component import Library, Component


register = Library()


@register.component
class Button(Component):
    def get_context_data(self, filled_slots):
        return {}
```

`app/templates/components/button.html`

```html+django
{% load slot_tags %}
<button>
    {% slot/ %}
</button>
```

### Usage

```html+django
{% load component_tags %}
{% button %}
    <div>Save</div>
    <small>and add another</small>
{% /button %}
```

## Form example

### Python

`app/templatetags/component_tags.py`

```python
from django_template_component.components import Library, Component


register = Library()


@register.component
class Button(Component):
    STYLE_CHOICES = ['green', 'red']

    def get_context_data(self, filled_slots, type='submit', name='', value='Submit', style='green'):
        if value and 'slot' in filled_slots:
            raise self.validation_error("use value keyword argument or slot tag. Not both.")

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
    def get_context_data(self, filled_slots, errors):
        return {
            'errors': errors,
        }


@register.inline_component
class FormField(Component):
    def get_context_data(self, filled_slots, field):
        return {
            'field': field,
        }


@register.component
class Form(Component):
    def get_context_data(self, filled_slots, form, action='', method='post', csrf_token='', csrf_exempt=False):

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

`app/templates/components/button.html`

```html+django
{% load slot_tags %}
<button {% if type %} type="{{ type }}"{% endif %}{% if name %} name="{{ name }}"{% endif %}
    class="btn{% if style == "green" %} btn--green{% elif style == "red" %}btn--red{% endif %}">
    {% slot %}{{ value }}{% /slot %}
</button>
```

`app/templates/components/form_errors.html`

```html+django
{% if errors %}
<div>
    {% for error in errors %}
    <div>{{ error }}</div>
    {% endfor %}
</div>
{% endif %}
```

`app/templates/components/form_field.html`

```html+django
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

`app/templates/components/form.html`

```html+django
{% load slot_tags %}
{% load component_tags %}
<form action="{{ action }}" method="{{ method }}"{% if form.is_multipart %} enctype="multipart/form-data"{% endif %}>

{% if csrf_token %}<input type="hidden" name="csrfmiddlewaretoken" value="{{ csrf_token }}">{% endif %}
{% for field in form.hidden_fields %}{{ field }}{% endfor %}

{% slot/ hidden_fields %}
    
{% form_errors/ errors=form.non_field_errors %}

{% slot visible_fields %}
    {% for field in form.visible_fields %}
        {% form_field/ field=field %}
    {% endfor %}
{% /slot %}

{% slot buttons %}
    {% button/ text=_("Submit") %}
{% /slot %}
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
