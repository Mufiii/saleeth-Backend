from django.urls import path
from .views import (
    # User Management
    UserListView,
    UserDetailView,
    UserBlockToggleView,
    UserBookAccessView,
    # Book Management
    AdminBookListView,
    AdminBookCreateView,
    AdminBookDetailView,
    AdminBookUpdateView,
    AdminBookDeleteView,
    # Chapter Management
    AdminChapterListView,
    AdminChapterCreateView,
    AdminChapterUpdateView,
    AdminChapterDeleteView,
    # YouTube Link Management
    AdminYouTubeLinkListView,
    AdminYouTubeLinkCreateView,
    AdminYouTubeLinkUpdateView,
    AdminYouTubeLinkDeleteView,
    # TOC Management
    AdminTOCEntryListView,
    AdminTOCEntryCreateView,
    AdminTOCEntryUpdateView,
    AdminTOCEntryDeleteView,
    # Book Content Management
    BookContentListView,
    BookContentCreateView,
    BookContentUpdateView,
    BookContentDeleteView,
    # Audio Upload
    AudioUploadView,
)

urlpatterns = [
    # User Management
    path('users/', UserListView.as_view(), name='admin-user-list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='admin-user-detail'),
    path('users/<int:user_id>/block-toggle/', UserBlockToggleView.as_view(), name='admin-user-block-toggle'),
    path('users/book-access/', UserBookAccessView.as_view(), name='admin-user-book-access'),
    
    # Book Management
    path('books/', AdminBookListView.as_view(), name='admin-book-list'),
    path('books/create/', AdminBookCreateView.as_view(), name='admin-book-create'),
    path('books/<int:pk>/', AdminBookDetailView.as_view(), name='admin-book-detail'),
    path('books/<int:pk>/update/', AdminBookUpdateView.as_view(), name='admin-book-update'),
    path('books/<int:pk>/delete/', AdminBookDeleteView.as_view(), name='admin-book-delete'),
    
    # Chapter Management
    path('chapters/', AdminChapterListView.as_view(), name='admin-chapter-list'),
    path('chapters/create/', AdminChapterCreateView.as_view(), name='admin-chapter-create'),
    path('chapters/<int:pk>/update/', AdminChapterUpdateView.as_view(), name='admin-chapter-update'),
    path('chapters/<int:pk>/delete/', AdminChapterDeleteView.as_view(), name='admin-chapter-delete'),
    
    # YouTube Link Management
    path('youtube-links/', AdminYouTubeLinkListView.as_view(), name='admin-youtube-link-list'),
    path('youtube-links/create/', AdminYouTubeLinkCreateView.as_view(), name='admin-youtube-link-create'),
    path('youtube-links/<int:pk>/update/', AdminYouTubeLinkUpdateView.as_view(), name='admin-youtube-link-update'),
    path('youtube-links/<int:pk>/delete/', AdminYouTubeLinkDeleteView.as_view(), name='admin-youtube-link-delete'),
    
    # TOC Management
    path('toc-entries/', AdminTOCEntryListView.as_view(), name='admin-toc-entry-list'),
    path('toc-entries/create/', AdminTOCEntryCreateView.as_view(), name='admin-toc-entry-create'),
    path('toc-entries/<int:pk>/update/', AdminTOCEntryUpdateView.as_view(), name='admin-toc-entry-update'),
    path('toc-entries/<int:pk>/delete/', AdminTOCEntryDeleteView.as_view(), name='admin-toc-entry-delete'),
    
    # Book Content Management
    path('books/<int:book_id>/contents/', BookContentListView.as_view(), name='admin-book-content-list'),
    path('books/<int:book_id>/contents/create/', BookContentCreateView.as_view(), name='admin-book-content-create'),
    path('books/<int:book_id>/contents/<int:pk>/update/', BookContentUpdateView.as_view(), name='admin-book-content-update'),
    path('books/<int:book_id>/contents/<int:pk>/delete/', BookContentDeleteView.as_view(), name='admin-book-content-delete'),
    
    # Audio Upload
    path('upload-audio/', AudioUploadView.as_view(), name='admin-audio-upload'),
]

