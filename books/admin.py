# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django import forms
from django.db import models
from .models import Book, BookAccess, Chapter, YouTubeLink

class ChapterInline(admin.TabularInline):
    model = Chapter
    extra = 0
    fields = ('title', 'order', 'markdown_content', 'content', 'is_preview', 'voice_file')
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(attrs={'rows': 4, 'cols': 80})},
    }


class YouTubeLinkInline(admin.TabularInline):
    model = YouTubeLink
    extra = 0


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'price', 'created_at')
    search_fields = ('title', 'author')
    ordering = ('-created_at',)
    inlines = [ChapterInline, YouTubeLinkInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'author', 'description', 'price', 'is_published')
        }),
        ('Content', {
            'fields': ('markdown_content', 'content', 'content_file', 'cover_image'),
            'description': 'Use markdown_content for new books. Old fields (content, content_file) are deprecated.'
        }),
    )
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(attrs={'rows': 20, 'cols': 100})},
    }


@admin.register(BookAccess)
class BookAccessAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'unlocked_at')
    list_filter = ('book', 'user')
    
