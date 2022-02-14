import os
from collections import defaultdict
from typing import Callable, DefaultDict, Hashable, NoReturn, TypedDict, cast

from django import template
from django.template.base import Node, NodeList, Parser, Token
from django.template.context import Context
from django.template.library import parse_bits
from django.template.loader import get_template

from django_slots.templatetags.slot_tags import SlotNode
from django_slots.utils import pascalcase_to_snakecase

DEFAULT_SLOT_NAME = "slot"


SlotsDict = DefaultDict[str, str]


class ContextData(TypedDict):
    slot: str
    slots: SlotsDict


class ComponentError(Exception):
    pass


class ComponentValidationError(Exception):
    pass


class Component:
    inline_tag_name = "{name}/"
    block_tag_names = "{name}", "/{name}"
    namespace = ""
    name = None
    template_name = ""

    @classmethod
    def get_name(cls) -> str:
        if cls.name:
            return cls.name
        return pascalcase_to_snakecase(cls.__name__)

    @classmethod
    def get_namespaced_name(cls) -> str:
        name = cls.get_name()
        if cls.namespace:
            return f"{cls.namespace}:{name}"
        return name

    def get_template_name(self) -> str:
        if self.template_name:
            return self.template_name
        return os.path.join("components", self.namespace, f"{self.get_name()}.html")

    @classmethod
    def get_inline_tag_name(cls) -> str:
        return cls.inline_tag_name.format(name=cls.get_namespaced_name())

    @classmethod
    def get_block_tag_names(cls) -> tuple[str, str]:
        name = cls.get_namespaced_name()
        start_tag, end_tag = cls.block_tag_names
        return start_tag.format(name=name), end_tag.format(name=name)

    @classmethod
    def validation_error(cls, msg: str) -> NoReturn:
        raise ComponentValidationError(f"{cls.get_name()} component {msg}")

    @classmethod
    def inline_compile_function(
        cls,
    ) -> Callable[[Parser, Token], "ComponentNode"]:
        def compile_func(parser: Parser, token: Token):
            component_params, component_kwargs = parse_bits(
                parser=parser,
                bits=token.split_contents()[1:],
                params=[],
                takes_context=False,
                name=cls.get_inline_tag_name(),
                varargs=None,
                varkw=[],
                defaults=None,
                kwonly=[],
                kwonly_defaults=None,
            )
            component = cls()
            return ComponentNode(component=component, kwargs=component_kwargs, slots=[])

        return compile_func

    @classmethod
    def block_compile_function(
        cls,
    ) -> Callable[[Parser, Token], "ComponentNode"]:
        def compile_func(parser: Parser, token: Token):
            nodelist = parser.parse(parse_until=[cls.get_block_tag_names()[1]])
            parser.delete_first_token()
            component_params, component_kwargs = parse_bits(
                parser=parser,
                bits=token.split_contents()[1:],
                params=[],
                takes_context=False,
                name=cls.get_block_tag_names()[1],
                varargs=None,
                varkw=[],
                defaults=None,
                kwonly=[],
                kwonly_defaults=None,
            )
            component = cls()
            slots = component._find_slot_nodes(nodelist=nodelist)
            return ComponentNode(
                component=component, kwargs=component_kwargs, slots=slots
            )

        return compile_func

    @staticmethod
    def _find_slot_nodes(*, nodelist: NodeList) -> list[SlotNode]:
        slot_nodes = nodelist.get_nodes_by_type(SlotNode)
        remaining_nodes = NodeList(node for node in nodelist if node not in slot_nodes)
        return [SlotNode(name=DEFAULT_SLOT_NAME, nodelist=remaining_nodes), *slot_nodes]

    def get_context_data(
        self, slots: SlotsDict, **kwargs: dict[Hashable, object]
    ) -> ContextData:
        return cast(
            ContextData,
            {"slot": slots[DEFAULT_SLOT_NAME], "slots": slots, **kwargs},
        )


class ComponentNode(Node):
    def __init__(
        self, *, component: Component, kwargs: dict, slots: list[SlotNode]
    ) -> None:
        self.component = component
        self.kwargs = kwargs
        self.slots = slots

    def render(self, context: Context) -> str:
        # Convert to defaultdict to prevent KeyError with use of |default template filter
        slots: SlotsDict = defaultdict(
            str, {slot.name: slot.render(context) for slot in self.slots}
        )
        resolved_kwargs = {
            key: value.resolve(context) for key, value in self.kwargs.items()
        }
        try:
            context = self.component.get_context_data(slots, **resolved_kwargs)
        except TypeError as error:
            # Reraise unexpected arguments and required arguments errors
            # annotated with component name.
            raise self.component.validation_error(str(error)) from error
        return get_template(self.component.get_template_name()).render(context)


class Library(template.Library):
    def component(self, component_class: type[Component]) -> type[Component]:
        """
        Register inline and block component
        """
        self.inline_component(component_class)
        self.block_component(component_class)
        return component_class

    def inline_component(self, component_class: type[Component]) -> type[Component]:
        """
        Register an inline component
        """
        self.tag(
            component_class.get_inline_tag_name(),
            component_class.inline_compile_function(),
        )
        return component_class

    def block_component(self, component_class: type[Component]) -> type[Component]:
        """
        Register a block component
        """
        self.tag(
            component_class.get_block_tag_names()[0],
            component_class.block_compile_function(),
        )
        return component_class
