from rest_framework import serializers
from .models import Book, Chapter, YouTubeLink, BookAccess, TableOfContentEntry
from .utils.markdown_processor import process_markdown


class BookListSerializer(serializers.ModelSerializer):
    is_locked = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = (
            'id', 'title', 'author', 'cover_image', 'price', 'is_published', 'is_locked',
        )

    def get_is_locked(self, obj):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return True
        # Admins (staff + superuser) have access to all books
        if user.is_staff and user.is_superuser:
            return False
        return not BookAccess.objects.filter(user=user, book=obj).exists()


class ChapterSerializer(serializers.ModelSerializer):
    html = serializers.SerializerMethodField()
    toc = serializers.SerializerMethodField()
    
    class Meta:
        model = Chapter
        fields = ('id', 'title', 'order', 'content', 'markdown_content', 'html', 'toc', 'is_preview', 'voice_file')
    
    def get_html(self, obj):
        """Generate HTML from markdown_content"""
        if not obj.markdown_content:
            return None
        result = process_markdown(obj.markdown_content)
        return result.get('html')
    
    def get_toc(self, obj):
        """Generate TOC from markdown_content"""
        if not obj.markdown_content:
            return []
        result = process_markdown(obj.markdown_content)
        return result.get('toc', [])


class YouTubeLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = YouTubeLink
        fields = ('id', 'title', 'url', 'order')


class BookDetailSerializer(serializers.ModelSerializer):
    is_locked = serializers.SerializerMethodField()
    chapters = serializers.SerializerMethodField()
    youtube_links = YouTubeLinkSerializer(many=True, read_only=True)
    html = serializers.SerializerMethodField()
    toc = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = (
            'id', 'title', 'author', 'description', 'cover_image', 'content_file', 'content',
            'markdown_content', 'html', 'toc', 'toc_position', 'price', 'is_published', 'is_locked', 
            'chapters', 'youtube_links',
        )
    
    def get_html(self, obj):
        """Generate HTML from markdown_content"""
        if not obj.markdown_content:
            return None
        result = process_markdown(obj.markdown_content)
        return result.get('html')
    
    def get_toc(self, obj):
        """Get TOC from manual entries (TableOfContentEntry) or auto-generate from markdown"""
        # Check if manual TOC entries exist
        manual_entries = TableOfContentEntry.objects.filter(book=obj).order_by('order', 'id')
        
        if manual_entries.exists():
            # Return manual TOC entries with hierarchical numbering
            return self._build_manual_toc(manual_entries)
        
        # Fallback to auto-generated TOC from markdown
        if not obj.markdown_content:
            return []
        result = process_markdown(obj.markdown_content)
        return result.get('toc', [])
    
    def _build_manual_toc(self, entries):
        """Build hierarchical TOC from manual entries with numbering"""
        # Build tree structure
        entries_list = list(entries)
        root_entries = [entry for entry in entries_list if entry.parent is None]
        
        def build_tree(entry_list, parent_number=""):
            """Recursively build TOC tree with numbers"""
            toc_list = []
            for idx, entry in enumerate(entry_list):
                # Calculate display number (1, 1.1, 1.2.1, etc.)
                number = parent_number + str(idx + 1) if parent_number else str(idx + 1)
                
                # Get children
                children = [e for e in entries_list if e.parent_id == entry.id]
                
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

    def get_is_locked(self, obj):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return True
        # Admins (staff + superuser) have access to all books
        if user.is_staff and user.is_superuser:
            return False
        return not BookAccess.objects.filter(user=user, book=obj).exists()

    def get_chapters(self, obj):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        # Admins (staff + superuser) can see all chapters
        if user and user.is_staff and user.is_superuser:
            qs = obj.chapters.all()
        else:
            is_locked = self.get_is_locked(obj)
            if is_locked:
                qs = obj.chapters.filter(is_preview=True)
            else:
                qs = obj.chapters.all()
        return ChapterSerializer(qs, many=True).data

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Hide content_file when locked
        if data.get('is_locked'):
            data['content_file'] = None
        return data
