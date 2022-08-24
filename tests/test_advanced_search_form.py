from django.template import Context, Template
from django.test import SimpleTestCase

from tests.mocks import CLMock, SearchFormTest


class TestAdvancedSearchTemplateTag(SimpleTestCase):

    def test_templatag_render(self):
        form = SearchFormTest()
        context = Context({'cl': CLMock, 'asf': form})
        template = Template(
            '{% load advanced_search_form %}'
            '{% advanced_search_form cl %}'
        ).render(context)

        for field, _ in form.fields.items():
            # search fields in template
            self.assertIn(str(form[field]), template)
            # search fields label's in template
            self.assertIn(form[field].label_tag(), template)

    def test_templatag_render_without_asf(self):
        context = Context({'cl': CLMock})
        template = Template(
            '{% load advanced_search_form %}'
            '{% advanced_search_form cl %}'
        ).render(context)
        self.assertEqual('', template)
