from django.template import Context, Template, TemplateSyntaxError
from django.test import TestCase


def render(template: str, data: dict[str, object] = None) -> str:
    """Convenience function for rendering templates"""
    data = data or {}
    return Template("{% load components slot_tags %} " + template).render(
        Context(data or {})
    )


class ComponentsTestCase(TestCase):
    def test_inline_and_block_component(self):
        assert render("{% button/ %}")
        assert render("{% button %}{% /button %}")

    def test_inline_only_component(self):
        with self.assertRaisesMessage(
            TemplateSyntaxError, "Invalid block tag on line 1: 'hr'."
        ):
            assert render("{% hr %}{% /hr %}")

        assert render("{% hr/ %}")

    def test_block_only_component(self):
        with self.assertRaisesMessage(
            TemplateSyntaxError, "Invalid block tag on line 1: 'details/'."
        ):
            assert render("{% details/ %}")
        assert render("{% details %}{% /details %}")

    def test_default_slot(self):
        self.assertHTMLEqual(
            render("{% button %}the default <b>slot</b>{% /button %}"),
            "<button>the default <b>slot</b></button>",
        )

    def test_named_slot(self):
        self.assertHTMLEqual(
            render(
                """
                {% details %}
                    {% slot summary %}the <b>summary</b>{% /slot %}
                    the default <b>slot</b>
                {% /details %}
                """
            ),
            """
            <details>
                <summary>the <b>summary</b></summary>
                the default <b>slot</b>
            </details>
            """,
        )

    def test_keyword_args(self):
        self.assertHTMLEqual(
            render("{% button/ value='Save' %}"),
            "<button>Save</button>",
        )
