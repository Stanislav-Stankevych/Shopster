from __future__ import annotations

from rest_framework import serializers

from .models import Post


class PostListSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")

    class Meta:
        model = Post
        fields = (
            "id",
            "slug",
            "title",
            "summary",
            "meta_title",
            "meta_description",
            "published_at",
            "tags",
        )


class PostDetailSerializer(PostListSerializer):
    body = serializers.CharField()
    meta_keywords = serializers.CharField(required=False, allow_blank=True)
    og_image = serializers.ImageField(required=False, allow_null=True)

    class Meta(PostListSerializer.Meta):
        fields = PostListSerializer.Meta.fields + (
            "body",
            "meta_keywords",
            "og_image",
            "created_at",
            "updated_at",
        )
