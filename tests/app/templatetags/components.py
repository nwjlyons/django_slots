from django_slots import Component, Library

register = Library()


@register.inline_component
class Hr(Component):
    pass


@register.block_component
class Details(Component):
    pass


@register.component
class Button(Component):
    pass
