from django.template import Library, TemplateSyntaxError
from django.template.base import Node, NodeList, Parser, Token
from django.template.context import Context

register = Library()


@register.tag(name="slot")
def slot(parser: Parser, token: Token) -> "SlotNode":
    bits = token.contents.split()
    if len(bits) > 2:
        raise TemplateSyntaxError(f"'slot' tag got unexpected arguments {bits[2:]!r}")
    from django_slots.components import DEFAULT_SLOT_NAME

    slot_name = DEFAULT_SLOT_NAME
    if len(bits) == 2:
        slot_name = bits[1]

    nodelist = parser.parse(parse_until=["/slot"])
    parser.delete_first_token()

    return SlotNode(name=slot_name, nodelist=nodelist)


class SlotNode(Node):
    def __init__(self, *, name: str, nodelist: NodeList) -> None:
        self.name = name
        self.nodelist = nodelist

    def render(self, context: Context) -> str:
        return self.nodelist.render(context)

    def __repr__(self):
        return f"<SlotNode name={self.name}>"
