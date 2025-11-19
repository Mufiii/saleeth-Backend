from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from accounts.models import User
from .models import Book, BookAccess, Chapter


class BookAccessTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='u@example.com', password='pass')
        self.book = Book.objects.create(title='B', author='A', description='D', is_published=True)
        Chapter.objects.create(book=self.book, title='Preview', order=1, content='P', is_preview=True)
        Chapter.objects.create(book=self.book, title='Full', order=2, content='F', is_preview=False)

    def test_list_requires_auth(self):
        url = reverse('book-list-create')
        res = self.client.get(url)
        self.assertEqual(res.status_code, 401)

    def test_locked_detail_shows_preview_only(self):
        self.client.force_authenticate(self.user)
        url = reverse('book-detail', args=[self.book.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.data['is_locked'])
        self.assertEqual(len(res.data['chapters']), 1)

    def test_unlocked_detail_shows_all(self):
        self.client.force_authenticate(self.user)
        BookAccess.objects.create(user=self.user, book=self.book)
        url = reverse('book-detail', args=[self.book.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertFalse(res.data['is_locked'])
        self.assertEqual(len(res.data['chapters']), 2)

    def test_blocked_user_denied(self):
        self.user.is_blocked = True
        self.user.save()
        self.client.force_authenticate(self.user)
        url = reverse('book-list-create')
        res = self.client.get(url)
        self.assertEqual(res.status_code, 403)
