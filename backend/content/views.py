from __future__ import annotations

from rest_framework import filters, viewsets
from rest_framework.permissions import IsAdminUser

from .models import Post
from .serializers import PostDetailSerializer, PostListSerializer
from shop.permissions import IsAdminOrReadOnly


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.select_related("author").prefetch_related("tags")
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = "slug"
    filter_backends = [filters.SearchFilter]
    search_fields = ["title", "summary", "body", "tags__name", "meta_keywords"]

    def get_queryset(self):
        qs = super().get_queryset()
        user = getattr(self.request, "user", None)
        if user is None or not user.is_staff:
            qs = qs.published()
        return qs

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        return PostDetailSerializer


