from django.template import Template, Context
from django.test import SimpleTestCase

from django_template_component.components import ComponentValidationError


class ComponentTestCase(SimpleTestCase):

    def test_no_keyword_arguments(self):
        self.assertHTMLEqual(
            Template("""
            {% load component_tags %}
            {% hr/ %}
            """).render(Context()),
            """
            <hr>
            """,
        )

    def test_keyword_argument(self):
        self.assertHTMLEqual(
            Template("""
            {% load component_tags %}
            {% button/ value="Save" %}
            """).render(Context()),
            """
            <button>Save</button>
            """,
        )

    def test_required_keyword_argument(self):
        with self.assertRaises(ComponentValidationError):
            Template("""
            {% load component_tags %}
            {% alert/ %}
            """).render(Context())

    def test_unexpected_keyword_argument(self):
        with self.assertRaises(ComponentValidationError):
            Template("""
            {% load component_tags %}
            {% alert/ message="Alert!" style='green' %}
            """).render(Context())


class SlotsTestCase(SimpleTestCase):

    def test_slot(self):
        self.assertHTMLEqual(
            Template("""
            {% load component_tags %}
            {% section %}default slot content{% /section %}
            """).render(Context()),
            """
            <section>
                default slot content
            </section>
            """,
        )
