from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from taggit.managers import TaggableManager


class PostQuerySet(models.QuerySet):
    def published(self):
        return self.filter(is_published=True, published_at__lte=timezone.now())


class Post(models.Model):
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    title = models.CharField(max_length=255)
    summary = models.CharField(max_length=500, blank=True)
    body = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="posts",
    )
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.CharField(max_length=500, blank=True)
    meta_keywords = models.CharField(max_length=255, blank=True)
    og_image = models.ImageField(upload_to="blog/", blank=True, null=True)
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = TaggableManager(blank=True)

    objects = PostQuerySet.as_manager()

    class Meta:
        ordering = ("-published_at", "-created_at")
        verbose_name = "Post"
        verbose_name_plural = "Posts"

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = (
                slugify(self.title, allow_unicode=True) or f"post-{self.pk or ''}"
            )
            slug = base_slug
            counter = 1
            while Post.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                counter += 1
                slug = f"{base_slug}-{counter}"
            self.slug = slug
        if not self.meta_title:
            self.meta_title = self.title
        if not self.meta_description:
            candidates = [self.summary, self.body]
            self.meta_description = next(
                (value.strip()[:500] for value in candidates if value), ""
            )
        if self.is_published and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    @property
    def canonical_url(self) -> str:
        from django.conf import settings as django_settings

        base = getattr(django_settings, "SITE_URL", "http://localhost:8000")
        return f"{base.rstrip('/')}/blog/{self.slug}"
