from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView, RetrieveAPIView
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.conf import settings
from books.models import Book, Chapter, YouTubeLink, TableOfContentEntry, BookAccess, BookContent
from .serializers import (
    UserListSerializer, UserDetailSerializer, AdminBookSerializer, AdminChapterSerializer,
    AdminYouTubeLinkSerializer, AdminTOCEntrySerializer, BulkBookAccessSerializer,
    BookContentSerializer, BookContentTreeSerializer
)
from .permissions import IsAdminUser
import os

User = get_user_model()


# ==================== USER MANAGEMENT ====================

class UserListView(ListAPIView):
    """List all users with search and pagination (admin only)."""
    serializer_class = UserListSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        queryset = User.objects.all().order_by('-date_joined')
        
        # Search functionality - filter by name, email, or phone
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(email__icontains=search) |
                Q(phone__icontains=search)
            )
        
        return queryset


class UserDetailView(RetrieveAPIView):
    """Get detailed information about a single user (admin only)."""
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [IsAdminUser]


class UserBlockToggleView(APIView):
    """Block or unblock a user (admin only)."""
    permission_classes = [IsAdminUser]
    
    def patch(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            # Prevent blocking admin users
            if user.is_staff and user.is_superuser:
                return Response(
                    {'detail': 'Cannot block admin users.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.is_blocked = not user.is_blocked
            user.save()
            serializer = UserListSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response(
                {'detail': 'User not found.'},
                status=status.HTTP_404_NOT_FOUND
            )


class UserBookAccessView(APIView):
    """Grant or revoke book access for users (bulk operations, admin only)."""
    permission_classes = [IsAdminUser]
    
    def post(self, request):
        serializer = BulkBookAccessSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user_ids = serializer.validated_data['user_ids']
        book_ids = serializer.validated_data['book_ids']
        action = serializer.validated_data['action']
        
        users = User.objects.filter(id__in=user_ids)
        books = Book.objects.filter(id__in=book_ids)
        
        results = {'granted': 0, 'revoked': 0, 'errors': []}
        
        for user in users:
            for book in books:
                if action == 'grant':
                    access, created = BookAccess.objects.get_or_create(
                        user=user,
                        book=book
                    )
                    if created:
                        results['granted'] += 1
                elif action == 'revoke':
                    deleted_count, _ = BookAccess.objects.filter(
                        user=user,
                        book=book
                    ).delete()
                    if deleted_count > 0:
                        results['revoked'] += 1
        
        return Response(results, status=status.HTTP_200_OK)


# ==================== BOOK MANAGEMENT ====================

class AdminBookListView(ListAPIView):
    """List all books including unpublished (admin only)."""
    queryset = Book.objects.all().order_by('-created_at')
    serializer_class = AdminBookSerializer
    permission_classes = [IsAdminUser]


class AdminBookCreateView(CreateAPIView):
    """Create a new book (admin only)."""
    queryset = Book.objects.all()
    serializer_class = AdminBookSerializer
    permission_classes = [IsAdminUser]


class AdminBookDetailView(RetrieveAPIView):
    """Get book details (admin only)."""
    queryset = Book.objects.all()
    serializer_class = AdminBookSerializer
    permission_classes = [IsAdminUser]


class AdminBookUpdateView(UpdateAPIView):
    """Update a book (admin only)."""
    queryset = Book.objects.all()
    serializer_class = AdminBookSerializer
    permission_classes = [IsAdminUser]


class AdminBookDeleteView(DestroyAPIView):
    """Delete a book (admin only)."""
    queryset = Book.objects.all()
    serializer_class = AdminBookSerializer
    permission_classes = [IsAdminUser]
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {'detail': 'Book deleted successfully.'},
            status=status.HTTP_200_OK
        )


# ==================== CHAPTER MANAGEMENT ====================

class AdminChapterCreateView(CreateAPIView):
    """Create a new chapter (admin only)."""
    queryset = Chapter.objects.all()
    serializer_class = AdminChapterSerializer
    permission_classes = [IsAdminUser]


class AdminChapterUpdateView(UpdateAPIView):
    """Update a chapter (admin only)."""
    queryset = Chapter.objects.all()
    serializer_class = AdminChapterSerializer
    permission_classes = [IsAdminUser]


class AdminChapterDeleteView(DestroyAPIView):
    """Delete a chapter (admin only)."""
    queryset = Chapter.objects.all()
    serializer_class = AdminChapterSerializer
    permission_classes = [IsAdminUser]
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {'detail': 'Chapter deleted successfully.'},
            status=status.HTTP_200_OK
        )


class AdminChapterListView(ListAPIView):
    """List chapters for a book (admin only)."""
    serializer_class = AdminChapterSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        book_id = self.request.query_params.get('book_id', None)
        if book_id:
            return Chapter.objects.filter(book_id=book_id).order_by('order', 'id')
        return Chapter.objects.all().order_by('book', 'order', 'id')


# ==================== YOUTUBE LINK MANAGEMENT ====================

class AdminYouTubeLinkCreateView(CreateAPIView):
    """Create a new YouTube link (admin only)."""
    queryset = YouTubeLink.objects.all()
    serializer_class = AdminYouTubeLinkSerializer
    permission_classes = [IsAdminUser]


class AdminYouTubeLinkUpdateView(UpdateAPIView):
    """Update a YouTube link (admin only)."""
    queryset = YouTubeLink.objects.all()
    serializer_class = AdminYouTubeLinkSerializer
    permission_classes = [IsAdminUser]


class AdminYouTubeLinkDeleteView(DestroyAPIView):
    """Delete a YouTube link (admin only)."""
    queryset = YouTubeLink.objects.all()
    serializer_class = AdminYouTubeLinkSerializer
    permission_classes = [IsAdminUser]
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {'detail': 'YouTube link deleted successfully.'},
            status=status.HTTP_200_OK
        )


class AdminYouTubeLinkListView(ListAPIView):
    """List YouTube links for a book (admin only)."""
    serializer_class = AdminYouTubeLinkSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        book_id = self.request.query_params.get('book_id', None)
        if book_id:
            return YouTubeLink.objects.filter(book_id=book_id).order_by('order', 'id')
        return YouTubeLink.objects.all().order_by('book', 'order', 'id')


# ==================== TABLE OF CONTENTS MANAGEMENT ====================

class AdminTOCEntryCreateView(CreateAPIView):
    """Create a new TOC entry (admin only)."""
    queryset = TableOfContentEntry.objects.all()
    serializer_class = AdminTOCEntrySerializer
    permission_classes = [IsAdminUser]


class AdminTOCEntryUpdateView(UpdateAPIView):
    """Update a TOC entry (admin only)."""
    queryset = TableOfContentEntry.objects.all()
    serializer_class = AdminTOCEntrySerializer
    permission_classes = [IsAdminUser]


class AdminTOCEntryDeleteView(DestroyAPIView):
    """Delete a TOC entry (admin only)."""
    queryset = TableOfContentEntry.objects.all()
    serializer_class = AdminTOCEntrySerializer
    permission_classes = [IsAdminUser]
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {'detail': 'TOC entry deleted successfully.'},
            status=status.HTTP_200_OK
        )


class AdminTOCEntryListView(ListAPIView):
    """List TOC entries for a book (admin only)."""
    serializer_class = AdminTOCEntrySerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        book_id = self.request.query_params.get('book_id', None)
        if book_id:
            return TableOfContentEntry.objects.filter(book_id=book_id).order_by('order', 'id')
        return TableOfContentEntry.objects.all().order_by('book', 'order', 'id')


# ==================== BOOK CONTENT MANAGEMENT ====================

class BookContentListView(ListAPIView):
    """List all BookContent entries for a book in tree structure (admin only)."""
    serializer_class = BookContentTreeSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        book_id = self.kwargs.get('book_id')
        # Return only root items (parent=None), children will be nested via serializer
        return BookContent.objects.filter(book_id=book_id, parent=None).order_by('order', 'id')


class BookContentCreateView(CreateAPIView):
    """Create a new BookContent entry (admin only)."""
    queryset = BookContent.objects.all()
    serializer_class = BookContentSerializer
    permission_classes = [IsAdminUser]
    
    def perform_create(self, serializer):
        book_id = self.kwargs.get('book_id')
        serializer.save(book_id=book_id)


class BookContentUpdateView(UpdateAPIView):
    """Update a BookContent entry (admin only)."""
    queryset = BookContent.objects.all()
    serializer_class = BookContentSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        book_id = self.kwargs.get('book_id')
        return BookContent.objects.filter(book_id=book_id)


class BookContentDeleteView(DestroyAPIView):
    """Delete a BookContent entry (admin only)."""
    queryset = BookContent.objects.all()
    serializer_class = BookContentSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        book_id = self.kwargs.get('book_id')
        return BookContent.objects.filter(book_id=book_id)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # If deleting a parent, also delete all children (CASCADE)
        self.perform_destroy(instance)
        return Response(
            {'detail': 'BookContent entry deleted successfully.'},
            status=status.HTTP_200_OK
        )


class AudioUploadView(APIView):
    """Upload audio file for book content (admin only)."""
    permission_classes = [IsAdminUser]
    
    def post(self, request):
        if 'voice_file' not in request.FILES:
            return Response(
                {'detail': 'No audio file provided.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        audio_file = request.FILES['voice_file']
        
        # Validate file type
        allowed_extensions = ['.mp3', '.wav', '.ogg', '.m4a', '.aac', '.flac']
        file_ext = os.path.splitext(audio_file.name)[1].lower()
        if file_ext not in allowed_extensions:
            return Response(
                {'detail': f'Invalid file type. Allowed: {", ".join(allowed_extensions)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate file size (max 50MB)
        if audio_file.size > 50 * 1024 * 1024:
            return Response(
                {'detail': 'File size too large. Maximum size is 50MB.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Save the file
        try:
            # Save to media/book_voices/ directory
            from django.core.files.storage import default_storage
            file_path = default_storage.save(f'book_voices/{audio_file.name}', audio_file)
            file_url = default_storage.url(file_path)
            
            return Response(
                {
                    'url': file_url,
                    'voice_file': file_url,
                    'file_url': file_url,
                    'filename': audio_file.name,
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error uploading audio file: {e}")
            return Response(
                {'detail': 'Failed to upload audio file.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
