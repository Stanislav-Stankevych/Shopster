from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class UsernameOrEmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        username = attrs.get("username")
        if username:
            user_model = get_user_model()
            try:
                user = user_model.objects.get(username=username)
            except user_model.DoesNotExist:
                if "@" in username:
                    try:
                        user = user_model.objects.get(email__iexact=username)
                    except user_model.DoesNotExist:
                        user = None
                else:
                    user = None
            if user is not None:
                attrs[self.username_field] = getattr(user, self.username_field)
        return super().validate(attrs)


class UsernameOrEmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = UsernameOrEmailTokenObtainPairSerializer
