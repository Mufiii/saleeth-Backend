from django.db import models
from django.conf import settings
from accounts.models import User

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    description = models.TextField()
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True)
    # Deprecated: Use markdown_content instead
    content_file = models.FileField(upload_to='book_files/', blank=True, null=True)
    # Deprecated: Use markdown_content instead
    content = models.JSONField(default=dict, blank=True, null=True, help_text="Rich text content in JSON format (TipTap/ProseMirror)")
    # New markdown content field - primary content storage
    markdown_content = models.TextField(blank=True, null=True, help_text="Markdown content that will be converted to HTML with TOC")
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # Table of Contents position setting
    toc_position = models.CharField(
        max_length=20,
        choices=[
            ('sidebar', 'Sidebar (Left)'),
            ('top', 'Top of Page'),
            ('bottom', 'Bottom of Page'),
            ('none', 'Hidden'),
        ],
        default='sidebar',
        help_text="Where to display the Table of Contents"
    )
    # Convenience relation to users via access records
    users = models.ManyToManyField('accounts.User', through='BookAccess', related_name='books')
    
    def __str__(self):
        return self.title
    
class BookAccess(models.Model):
    """Represents which books a user has purchased/unlocked"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="book_access")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="access_records")
    unlocked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'book')

    def __str__(self):
        return f"{self.user.email} → {self.book.title}"


class Chapter(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='chapters')
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)
    # Deprecated: Use markdown_content instead
    content = models.TextField()
    # New markdown content field
    markdown_content = models.TextField(blank=True, null=True, help_text="Markdown content for chapter")
    is_preview = models.BooleanField(default=False)
    voice_file = models.FileField(upload_to='book_voices/', blank=True, null=True)

    class Meta:
        ordering = ['order', 'id']
        unique_together = ('book', 'order')

    def __str__(self):
        return f"{self.book.title} • {self.order}. {self.title}"


class YouTubeLink(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='youtube_links')
    title = models.CharField(max_length=200)
    url = models.URLField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.book.title} • {self.title}"


class TableOfContentEntry(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='toc_entries')
    chapter = models.ForeignKey('Chapter', on_delete=models.SET_NULL, null=True, blank=True, related_name='toc_entries')
    title = models.CharField(max_length=200)
    level = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=0)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    anchor_id = models.CharField(max_length=200, blank=True, null=True, help_text="ID attribute for linking to content sections")

    class Meta:
        ordering = ['order', 'id']
        unique_together = ('book', 'order', 'parent')

    def __str__(self):
        return f"{self.book.title} • L{self.level} • {self.title}"


class BookContent(models.Model):
    """Nested table of contents structure for books."""
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='book_contents')
    title = models.CharField(max_length=200)
    url = models.URLField(blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'id']
        unique_together = ('book', 'order', 'parent')

    def __str__(self):
        return f"{self.book.title} • {self.title}"
