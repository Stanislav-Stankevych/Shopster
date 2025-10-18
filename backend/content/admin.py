from django import forms
from django.contrib import admin
from ckeditor.widgets import CKEditorWidget

from .models import Post


class PostAdminForm(forms.ModelForm):
    body = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = Post
        fields = "__all__"


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    form = PostAdminForm
    list_display = ("title", "is_published", "published_at", "updated_at")
    list_filter = ("is_published", "tags")
    search_fields = ("title", "summary", "body")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ()
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("title", "slug", "summary", "body", "author", "tags")}),
        ("Publication", {"fields": ("is_published", "published_at")}),
        ("SEO", {"fields": ("meta_title", "meta_description", "meta_keywords", "og_image")}),
        ("System", {"classes": ("collapse",), "fields": ("created_at", "updated_at")}),
    )

