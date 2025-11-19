from django.urls import path
from .views import (
    BookListCreateView, BookDetailView, BookReadView, BookContentView, UserPurchasedBooksView,
)

urlpatterns = [
    # /api/books/purchased/
    path('purchased/', UserPurchasedBooksView.as_view(), name='user-purchased-books'),

    # Book-specific routes
    path('<int:pk>/content/', BookContentView.as_view(), name='book-content'),
    path('<int:pk>/read/', BookReadView.as_view(), name='book-read'),
    path('<int:pk>/', BookDetailView.as_view(), name='book-detail'),
    path('', BookListCreateView.as_view(), name='book-list-create'),
]
