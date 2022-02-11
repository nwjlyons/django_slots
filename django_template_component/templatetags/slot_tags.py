from django.template import TemplateSyntaxError, Library
from django.template.base import Parser, Token, Node, NodeList


register = Library()


def get_slot(context, name):
    if 'component' in context and (slot := context['component']['_slots'].get(name, None)):
        return slot


@register.tag(name='slot/')
def inline_slot(parser: Parser, token: Token):
    bits = token.contents.split()
    if len(bits) > 2:
        raise TemplateSyntaxError(f"'slot' tag got unexpected arguments {bits[2:]!r}")
    from django_template_component.components import DEFAULT_SLOT_NAME
    slot_name = DEFAULT_SLOT_NAME
    if len(bits) == 2:
        slot_name = bits[1]

    return SlotInlineNode(name=slot_name)


class SlotInlineNode(Node):
    def __init__(self, *, name: str):
        self.name = name

    def render(self, context):
        if slot := get_slot(context, self.name):
            return slot
        return ""

    def __repr__(self):
        return f"<SlotInlineNode name={self.name}>"


@register.tag(name='slot')
def block_slot(parser: Parser, token: Token):
    bits = token.contents.split()
    if len(bits) > 2:
        raise TemplateSyntaxError(f"'slot' tag got unexpected arguments {bits[2:]!r}")
    from django_template_component.components import DEFAULT_SLOT_NAME
    slot_name = DEFAULT_SLOT_NAME
    if len(bits) == 2:
        slot_name = bits[1]

    nodelist = parser.parse(parse_until=['/slot'])
    parser.delete_first_token()

    return SlotBlockNode(name=slot_name, nodelist=nodelist)


class SlotBlockNode(Node):
    def __init__(self, *, name: str, nodelist: NodeList):
        self.name = name
        self.nodelist = nodelist

    def render(self, context):
        if slot := get_slot(context, self.name):
            return slot
        return self.nodelist.render(context)

    def __repr__(self):
        return f"<SlotBlockNode name={self.name}>"
