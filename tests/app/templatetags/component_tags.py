from django_slots import Component, Library


register = Library()


@register.component
class Hr(Component):
    pass


@register.component
class Button(Component):
    pass


@register.block_component
class Details(Component):
    pass


@register.inline_component
class Alert(Component):
    def get_context_data(self, filled_slots, message: str):
        return {'message': message}


@register.component
class Section(Component):
    def get_context_data(self, filled_slots):
        return {}
