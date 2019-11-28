from django.test import TestCase

from console import console

from .models import BasicPost

console = console(source=__name__)


class CustomBaseModelTestCase(TestCase):
    """Unit tests of CustomBaseModel"""

    @classmethod
    def setUpTestData(cls):  # noqa: N802
        cls.post = BasicPost.objects.create(title='Test Post 1')

    def test_basemodel_fields(self):
        """Test fields"""

        self.assertEqual(self.post.pk, self.post.id)

    def test_basemodel_queryset(self):
        """Test queryset"""

        self.assertQuerysetEqual(BasicPost.objects.all().order_by('id'), ['<BasicPost: Test Post 1>'])
