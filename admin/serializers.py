from rest_framework import serializers
from django.contrib.auth import get_user_model
from books.models import Book, Chapter, YouTubeLink, TableOfContentEntry, BookAccess, BookContent
import json

User = get_user_model()


class UserListSerializer(serializers.ModelSerializer):
    """Serializer for listing users with their book access information."""
    book_access_count = serializers.SerializerMethodField()
    book_accesses = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'phone', 'is_blocked', 'is_staff', 'is_superuser', 
                  'date_joined', 'book_access_count', 'book_accesses']
        read_only_fields = ['id', 'date_joined', 'is_staff', 'is_superuser']
    
    def get_book_access_count(self, obj):
        return BookAccess.objects.filter(user=obj).count()
    
    def get_book_accesses(self, obj):
        accesses = BookAccess.objects.filter(user=obj).select_related('book')
        return [{'book_id': access.book.id, 'book_title': access.book.title, 
                'unlocked_at': access.unlocked_at} for access in accesses]


class UserDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single user with expanded book access information."""
    book_access_count = serializers.SerializerMethodField()
    book_accesses = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'phone', 'is_blocked', 'is_staff', 'is_superuser', 
                  'date_joined', 'last_login', 'book_access_count', 'book_accesses']
        read_only_fields = ['id', 'date_joined', 'last_login', 'is_staff', 'is_superuser']
    
    def get_book_access_count(self, obj):
        return BookAccess.objects.filter(user=obj).count()
    
    def get_book_accesses(self, obj):
        accesses = BookAccess.objects.filter(user=obj).select_related('book').order_by('-unlocked_at')
        return [
            {
                'book_id': access.book.id,
                'book_title': access.book.title,
                'book_author': access.book.author,
                'book_price': str(access.book.price),
                'unlocked_at': access.unlocked_at,
            } 
            for access in accesses
        ]


class AdminBookSerializer(serializers.ModelSerializer):
    """Full book serializer for admin operations."""
    chapters_count = serializers.SerializerMethodField()
    youtube_links_count = serializers.SerializerMethodField()
    toc_entries_count = serializers.SerializerMethodField()
    users_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'description', 'cover_image', 'content_file', 
                  'content', 'markdown_content', 'toc_position', 'price', 'is_published', 'created_at', 'chapters_count', 
                  'youtube_links_count', 'toc_entries_count', 'users_count']
        read_only_fields = ['id', 'created_at']
    
    def to_internal_value(self, data):
        """Override to handle content field before validation."""
        # Make data mutable if it's not already
        if hasattr(data, '_mutable'):
            # It's a QueryDict (from FormData)
            data = data.copy()
        elif isinstance(data, dict):
            # It's a regular dict (from JSON)
            data = data.copy()
        else:
            # Unknown type, try to convert
            data = dict(data) if hasattr(data, 'items') else data
        
        # Handle content field if it exists and is a string
        if 'content' in data:
            content_value = data.get('content')
            
            # If it's a string, parse it as JSON
            if isinstance(content_value, str):
                if content_value.strip():
                    try:
                        # Parse JSON string to dict/list
                        data['content'] = json.loads(content_value)
                    except (json.JSONDecodeError, ValueError, TypeError) as e:
                        # If parsing fails, set to empty dict
                        # Don't raise error, just use empty dict
                        data['content'] = {}
                else:
                    # Empty string becomes empty dict
                    data['content'] = {}
            # If it's already None, set to empty dict (model default)
            elif content_value is None:
                data['content'] = {}
        
        return super().to_internal_value(data)
    
    def validate_content(self, value):
        """Validate content field - expects dict/list or None."""
        if value is None:
            return {}
        
        # If it's already a dict or list, return as is
        if isinstance(value, (dict, list)):
            return value
        
        # If it's a string at this point, try to parse it (shouldn't happen after to_internal_value)
        if isinstance(value, str):
            if not value.strip():
                return {}
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError, ValueError):
                return {}
        
        # For any other type, return empty dict
        return {}
    
    def get_chapters_count(self, obj):
        return obj.chapters.count()
    
    def get_youtube_links_count(self, obj):
        return obj.youtube_links.count()
    
    def get_toc_entries_count(self, obj):
        return obj.toc_entries.count()
    
    def get_users_count(self, obj):
        return obj.access_records.count()


class AdminChapterSerializer(serializers.ModelSerializer):
    """Chapter serializer with voice_file for admin operations."""
    book_title = serializers.CharField(source='book.title', read_only=True)
    
    class Meta:
        model = Chapter
        fields = ['id', 'book', 'book_title', 'title', 'order', 'content', 
                  'is_preview', 'voice_file']
        read_only_fields = ['id']


class AdminYouTubeLinkSerializer(serializers.ModelSerializer):
    """YouTube link serializer for admin operations."""
    book_title = serializers.CharField(source='book.title', read_only=True)
    
    class Meta:
        model = YouTubeLink
        fields = ['id', 'book', 'book_title', 'title', 'url', 'order']
        read_only_fields = ['id']


class AdminTOCEntrySerializer(serializers.ModelSerializer):
    """Table of Contents entry serializer for admin operations."""
    book_title = serializers.CharField(source='book.title', read_only=True)
    chapter_title = serializers.CharField(source='chapter.title', read_only=True, allow_null=True)
    parent_title = serializers.CharField(source='parent.title', read_only=True, allow_null=True)
    children_count = serializers.SerializerMethodField()
    
    class Meta:
        model = TableOfContentEntry
        fields = ['id', 'book', 'book_title', 'chapter', 'chapter_title', 
                  'title', 'level', 'order', 'parent', 'parent_title', 
                  'anchor_id', 'children_count']
        read_only_fields = ['id']
    
    def get_children_count(self, obj):
        """Get the number of child entries."""
        return obj.children.count() if hasattr(obj, 'children') else 0


class BulkBookAccessSerializer(serializers.Serializer):
    """Serializer for bulk book access operations."""
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False,
        help_text="List of user IDs"
    )
    book_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False,
        help_text="List of book IDs"
    )
    action = serializers.ChoiceField(
        choices=['grant', 'revoke'],
        help_text="Action to perform: 'grant' or 'revoke'"
    )
    
    def validate(self, attrs):
        user_ids = attrs.get('user_ids', [])
        book_ids = attrs.get('book_ids', [])
        
        # Validate users exist
        existing_users = User.objects.filter(id__in=user_ids).count()
        if existing_users != len(user_ids):
            raise serializers.ValidationError("Some user IDs are invalid.")
        
        # Validate books exist
        existing_books = Book.objects.filter(id__in=book_ids).count()
        if existing_books != len(book_ids):
            raise serializers.ValidationError("Some book IDs are invalid.")
        
        return attrs


class BookContentSerializer(serializers.ModelSerializer):
    """Serializer for BookContent with nested children support."""
    children = serializers.SerializerMethodField()
    book_title = serializers.CharField(source='book.title', read_only=True)
    
    class Meta:
        model = BookContent
        fields = ['id', 'book', 'book_title', 'title', 'url', 'parent', 'order', 'created_at', 'children']
        read_only_fields = ['id', 'created_at']
    
    def get_children(self, obj):
        """Recursively get all children."""
        children = obj.children.all().order_by('order', 'id')
        return BookContentSerializer(children, many=True).data


class BookContentTreeSerializer(serializers.ModelSerializer):
    """Serializer for BookContent tree structure (only root items with nested children)."""
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = BookContent
        fields = ['id', 'book', 'title', 'url', 'parent', 'order', 'created_at', 'children']
        read_only_fields = ['id', 'created_at']
    
    def get_children(self, obj):
        """Recursively get all children."""
        children = obj.children.all().order_by('order', 'id')
        return BookContentTreeSerializer(children, many=True).data

