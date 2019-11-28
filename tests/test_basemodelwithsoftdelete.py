from django.test import TestCase

from console import console

from .models import Category, Member, Person, Post

console = console(source=__name__)


class CustomBaseModelWithSoftDeleteTestCase(TestCase):
    """Unit tests of CustomBaseModelWithSoftDelete"""

    @classmethod
    def setUpTestData(cls):  # noqa: N802
        cls.category = Category.objects.create(title='Python')
        cls.posts = [
            Post.objects.create(category=cls.category, title='Python post 1'),
            Post.objects.create(category=cls.category, title='Python post 2'),
        ]
        cls.people = [Person.objects.create(name='Person 1'), Person.objects.create(name='Person 2')]
        cls.member = Member.objects.create(title='Membership')
        cls.member.members.add(*cls.people)

    def test_softdelete_for_many_to_many(self):
        deleted_member = self.member.delete()
        self.assertEqual(deleted_member, (3, {'tests.Member': 1, 'tests.Member_members': 2}))
        self.assertQuerysetEqual(Member.objects.all(), ['<Member: Membership>'])
        self.assertQuerysetEqual(Member.objects.actives(), [])
        self.assertQuerysetEqual(Member.objects.inactives(), ['<Member: Membership>'])
        self.assertQuerysetEqual(
            self.member.members.actives(), ['<Person: Person 1>', '<Person: Person 2>'], ordered=False
        )

    def test_basemodelwithsoftdelete_fields(self):
        """Test fields"""

        self.assertEqual(self.category.pk, self.category.id)
        for post in self.posts:
            self.assertIsNone(post.deleted_at)

    def test_basemodelwithsoftdelete_queryset(self):
        """Test queryset"""

        self.assertQuerysetEqual(
            self.category.posts.all().order_by('id'), ['<Post: Python post 1>', '<Post: Python post 2>']
        )
        self.assertQuerysetEqual(Category.objects.actives(), ['<Category: Python>'])
        self.assertQuerysetEqual(Category.objects.inactives(), [])

    def test_soft_deletetion(self):
        """Test soft deletion"""

        deleted_category = self.category.delete()
        self.assertEqual(deleted_category, (3, {'tests.Category': 1, 'tests.Post': 2}))
        self.assertQuerysetEqual(Category.objects.inactives(), ['<Category: Python>'])
        self.assertQuerysetEqual(
            Post.objects.inactives().order_by('id'), ['<Post: Python post 1>', '<Post: Python post 2>']
        )

    def test_softdelete_undelete(self):
        """Test undelete feature"""

        deleted_category = self.category.delete()
        self.assertEqual(deleted_category, (3, {'tests.Category': 1, 'tests.Post': 2}))

        undeleted_items = self.category.undelete()
        self.assertEqual(undeleted_items, (3, {'tests.Category': 1, 'tests.Post': 2}))
        self.assertQuerysetEqual(Post.objects.inactives(), [])

    def test_softdelete_all(self):
        deleted_posts = Post.objects.delete()
        self.assertEqual(deleted_posts, (2, {'tests.Post': 2}))
