from django.template import TemplateSyntaxError, Library
from django.template.base import Parser, Token, Node, NodeList

register = Library()


@register.tag(name='slot')
def slot(parser: Parser, token: Token):
    bits = token.contents.split()
    if len(bits) > 2:
        raise TemplateSyntaxError(f"'slot' tag got unexpected arguments {bits[2:]!r}")
    from django_template_component.components import DEFAULT_SLOT_NAME
    slot_name = DEFAULT_SLOT_NAME
    if len(bits) == 2:
        slot_name = bits[1]

    nodelist = parser.parse(parse_until=['/slot'])
    parser.delete_first_token()

    return SlotNode(name=slot_name, nodelist=nodelist)


class SlotNode(Node):
    def __init__(self, *, name: str, nodelist: NodeList):
        self.name = name
        self.nodelist = nodelist

    def render(self, context):
        return self.nodelist.render(context)

    def __repr__(self):
        return f"<SlotNode name={self.name}>"
