from django_template_component import Component, Library


register = Library()


@register.component
class Hr(Component):
    def get_context_data(self, filled_slots):
        return {}


@register.component
class Button(Component):
    def get_context_data(self, filled_slots, value):
        return {'value': value}


@register.component
class Section(Component):
    def get_context_data(self, filled_slots):
        return {}
