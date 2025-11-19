from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Book, BookAccess
from .serializers import BookListSerializer, BookDetailSerializer
from .permissions import IsNotBlocked
from .utils.markdown_processor import process_markdown
import logging

logger = logging.getLogger(__name__)

class BookListCreateView(generics.ListAPIView):
    serializer_class = BookListSerializer
    permission_classes = [permissions.IsAuthenticated, IsNotBlocked]
    
    def get_queryset(self):
        # Admins (staff + superuser) can see all books (including unpublished), regular users only published
        user = self.request.user
        if user.is_staff and user.is_superuser:
            return Book.objects.all()
        return Book.objects.filter(is_published=True)


class BookDetailView(generics.RetrieveAPIView):
    serializer_class = BookDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsNotBlocked]
    
    def get_queryset(self):
        # Admins (staff + superuser) can see all books (including unpublished), regular users only published
        user = self.request.user
        if user.is_staff and user.is_superuser:
            return Book.objects.all()
        return Book.objects.filter(is_published=True)
    
    

class BookReadView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsNotBlocked]

    def get(self, request, pk):
        user = request.user
        
        # Check if user is blocked (should be caught by IsNotBlocked, but double-check)
        if user.is_blocked:
            logger.warning(f"Blocked user {user.id} attempted to access book {pk}")
            return Response({'detail': 'Your account is blocked.'}, status=403)
        
        try:
            book = Book.objects.get(pk=pk)
        except Book.DoesNotExist:
            logger.warning(f"Book {pk} not found for user {user.id}")
            return Response({'detail': 'Book not found'}, status=404)

        # Admins (staff + superuser) can access all books, including unpublished ones
        is_admin = user.is_staff and user.is_superuser
        if not is_admin:
            # Check if book is published (only for non-admins)
            if not book.is_published:
                logger.warning(f"User {user.id} attempted to access unpublished book {pk}")
                return Response({'detail': 'This book is not available.'}, status=404)

            # Access logic: unlocked only if a BookAccess exists for this user-book
            # Use select_related for better performance and ensure exact match
            has_access = BookAccess.objects.filter(
                user=user,
                book=book
            ).exists()

            logger.info(f"User {user.id} access check for book {pk}: {has_access}")

            if not has_access:
                logger.warning(f"User {user.id} denied access to book {pk} - no BookAccess record")
                return Response({'detail': 'Access denied: this book is locked.'}, status=403)
        else:
            logger.info(f"Admin {user.id} (staff: {user.is_staff}, superuser: {user.is_superuser}) granted access to book {pk}")

        serializer = BookDetailSerializer(book, context={'request': request})
        logger.info(f"User {user.id} granted access to book {pk}")
        return Response({
            'message': f"You are reading '{book.title}'",
            'book': serializer.data
        }, status=200)


class BookContentView(APIView):
    """
    Get book content with HTML and TOC generated from markdown.
    GET /api/books/<id>/content/ - Returns {id, title, html, toc}
    """
    permission_classes = [permissions.IsAuthenticated, IsNotBlocked]

    def get(self, request, pk):
        user = request.user
        
        # Check if user is blocked
        if user.is_blocked:
            logger.warning(f"Blocked user {user.id} attempted to access book content {pk}")
            return Response({'detail': 'Your account is blocked.'}, status=403)
        
        try:
            book = Book.objects.get(pk=pk)
        except Book.DoesNotExist:
            logger.warning(f"Book {pk} not found for user {user.id}")
            return Response({'detail': 'Book not found'}, status=404)

        # Admins (staff + superuser) can access all books, including unpublished ones
        is_admin = user.is_staff and user.is_superuser
        if not is_admin:
            # Check if book is published (only for non-admins)
            if not book.is_published:
                logger.warning(f"User {user.id} attempted to access unpublished book {pk}")
                return Response({'detail': 'This book is not available.'}, status=404)

            # Check access
            has_access = BookAccess.objects.filter(
                user=user,
                book=book
            ).exists()

            if not has_access:
                logger.warning(f"User {user.id} denied access to book {pk} - no BookAccess record")
                return Response({'detail': 'Access denied: this book is locked.'}, status=403)
        else:
            logger.info(f"Admin {user.id} (staff: {user.is_staff}, superuser: {user.is_superuser}) granted access to book content {pk}")

        # Process markdown if available
        if book.markdown_content:
            result = process_markdown(book.markdown_content)
            html = result.get('html', '')
        else:
            html = ''

        # Get TOC from manual entries or markdown
        from .models import TableOfContentEntry
        
        manual_entries = TableOfContentEntry.objects.filter(book=book).order_by('order', 'id')
        if manual_entries.exists():
            # Build manual TOC with hierarchical numbering
            toc = self._build_manual_toc(list(manual_entries))
        elif book.markdown_content:
            result = process_markdown(book.markdown_content)
            toc = result.get('toc', [])
        else:
            toc = []

        logger.info(f"User {user.id} granted access to book content {pk}")
        return Response({
            'id': book.id,
            'title': book.title,
            'html': html,
            'toc': toc,
            'toc_position': book.toc_position
        }, status=200)
    
    def _build_manual_toc(self, entries):
        """Build hierarchical TOC from manual entries with numbering"""
        root_entries = [entry for entry in entries if entry.parent is None]
        
        def build_tree(entry_list, parent_number=""):
            """Recursively build TOC tree with numbers"""
            toc_list = []
            for idx, entry in enumerate(entry_list):
                # Calculate display number (1, 1.1, 1.2.1, etc.)
                number = parent_number + str(idx + 1) if parent_number else str(idx + 1)
                
                # Get children
                children = [e for e in entries if e.parent_id == entry.id]
                
                # Create TOC entry
                toc_entry = {
                    'id': entry.anchor_id or f'toc-entry-{entry.id}',
                    'title': entry.title,
                    'level': entry.level,
                    'number': number,
                }
                
                # Add children if any
                if children:
                    sorted_children = sorted(children, key=lambda e: e.order)
                    toc_entry['children'] = build_tree(sorted_children, number + '.')
                
                toc_list.append(toc_entry)
            
            return toc_list
        
        # Sort root entries by order
        sorted_roots = sorted(root_entries, key=lambda e: e.order)
        return build_tree(sorted_roots)


class UserPurchasedBooksView(APIView):
    """List all books the current user has access to."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        # Admins (staff + superuser) can see all books
        if user.is_staff and user.is_superuser:
            books = Book.objects.all()
        else:
            accesses = BookAccess.objects.filter(user=user)
            books = [access.book for access in accesses]
        serializer = BookListSerializer(books, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)