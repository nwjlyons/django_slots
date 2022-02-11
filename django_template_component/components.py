import os
from typing import Tuple, Dict, List

from django import template
from django.template.base import Parser, Node, NodeList, Token
from django.template.library import parse_bits
from django.template.loader import get_template

from django_template_component.templatetags.slot_tags import SlotBlockNode
from django_template_component.utils import camelcase_to_underscore

DEFAULT_SLOT_NAME = 'slot'


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
        return camelcase_to_underscore(cls.__name__)

    @classmethod
    def get_namespaced_name(cls) -> str:
        name = cls.get_name()
        if cls.namespace:
            return f"{cls.namespace}:{name}"
        return name

    def get_template_name(self) -> str:
        if self.template_name:
            return self.template_name
        return os.path.join("components", f"{self.get_name()}.html")

    @classmethod
    def get_inline_tag_name(cls) -> str:
        return cls.inline_tag_name.format(name=cls.get_namespaced_name())

    @classmethod
    def get_block_tag_names(cls) -> Tuple[str, str]:
        name = cls.get_namespaced_name()
        start_tag, end_tag = cls.block_tag_names
        return start_tag.format(name=name), end_tag.format(name=name)

    @classmethod
    def validation_error(cls, msg: str):
        raise ComponentValidationError(f"{cls.get_name()} component {msg}")

    @classmethod
    def inline_compile_function(cls):
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
    def block_compile_function(cls):
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
            slots = component.find_slot_nodes(nodelist=nodelist)
            return ComponentNode(component=component, kwargs=component_kwargs, slots=slots)
        return compile_func

    @staticmethod
    def find_slot_nodes(*, nodelist: NodeList):
        if slots := nodelist.get_nodes_by_type(SlotBlockNode):
            return slots
        return [SlotBlockNode(name=DEFAULT_SLOT_NAME, nodelist=nodelist)]

    def get_context_data(self, filled_slots, **kwargs):
        raise NotImplementedError


class ComponentNode(Node):

    def __init__(self, *, component: Component, kwargs: Dict, slots: List):
        self.component = component
        self.kwargs = kwargs
        self.slots = slots

    def render(self, context):
        slots = {
            slot.name: slot.render(context)
            for slot in self.slots
        }
        resolved_kwargs = {key: value.resolve(context) for key, value in self.kwargs.items()}
        try:
            context = self.component.get_context_data(list(slots.keys()), **resolved_kwargs)
        except TypeError as error:
            raise self.component.validation_error(error) from error
        context['component'] = {}
        context['component']['slot'] = DEFAULT_SLOT_NAME in slots.keys()
        context['component']['slots'] = {slot_name: True for slot_name in slots.keys()}
        context['component']['_slots'] = slots
        return get_template(self.component.get_template_name()).render(context)


class Library(template.Library):

    def component(self, component_class: Component):
        self.inline_component(component_class)
        self.block_component(component_class)
        return component_class

    def inline_component(self, component_class: Component):
        self.tag(component_class.get_inline_tag_name(), component_class.inline_compile_function())
        return component_class

    def block_component(self, component_class: Component):
        self.tag(component_class.get_block_tag_names()[0], component_class.block_compile_function())
        return component_class
